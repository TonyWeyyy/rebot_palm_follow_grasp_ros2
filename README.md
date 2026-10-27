# reBot Arm B601-RS 手掌跟随 + 捏合抓取（ROS2 版）

原单脚本项目 `rebot_palm_follow_grasp` 的 ROS2 工程化移植。
控制算法、安全机制、最终调定参数与原项目逐一对应（详见文末对照表）。

## 架构

```
┌─────────────────────┐   /palm_target (PalmTarget, 60Hz)   ┌─────────────────────┐
│    vision_node      │ ──────────────────────────────────▶ │     servo_node      │
│  Gemini2 相机        │                                     │  唯一持有机械臂        │
│  MediaPipe+LK 桥接   │   /follow_enable (Bool, g/空格)     │  KF/老架构伺服 100Hz  │
│  深度四层保护链       │ ──────────────────────────────────▶ │  软/硬墙+奇异保护      │
│  捏合→目标角(度)      │                                     │  夹爪冻结门控+J7下发   │
│  GUI 窗口 + 键盘     │ ◀────────────────────────────────── │  (单一 CAN 主机)      │
└─────────────────────┘   /servo_status (String JSON, 2Hz)  └─────────────────────┘
```

- `rebot_interfaces`：自定义消息 `PalmTarget`（掌心 3D + 可见/冻结/桥接标志 + 捏合目标角）
- `rebot_palm_follow_grasp`：两个 Python 节点 + 参数文件 + launch + 标定工具

**职责边界的理由**：夹爪走 rebot_control 第 7 通道，必须与关节指令同一 CAN 主机，
所以机械臂只能由 servo_node 持有；而「手臂运动时冻结夹爪」需要关节速度，
也只有 servo_node 知道——夹爪目标角在 vision_node 算好（One Euro 滤波），
冻结与下发在 servo_node 完成。

## 编译

> ⚠️ **工作区路径必须全英文**！rosidl 消息生成器无法处理中文路径
> （如 `~/下载/`），会报 `list index: 1 out of range` 且生成的依赖
> 路径被截断。请把工作区放在如 `~/rebot_ws` 这样的纯英文路径下。

> ⚠️ **只使用系统 `/usr/bin/python3`（3.10）和 `/opt/ros/humble`**。
> 编译前退出 conda；不要在 conda 的 `rebot-cv` 环境编译或运行本工程。
> 每个新终端都必须先 source 系统 ROS，再编译，最后 source 工作区。

```bash
conda deactivate 2>/dev/null || true
source /opt/ros/humble/setup.bash
cd rebot_palm_follow_grasp_ros2
# 从旧包升级时清掉旧构建副本，避免 launch 继续运行旧 rebot_adapter.py
rm -rf build install log
colcon build
source install/setup.bash
```

视觉依赖为 mediapipe、opencv、pynput、numpy 等；运动学只依赖 NumPy，
**不再需要 pin/pinocchio**。
相机 SDK 用 **pyorbbecsdk2**（v2.x，导入名仍是 `pyorbbecsdk`）：

```bash
# 在运行节点的 Python 环境里安装（系统 python3 或 conda rebot-cv 均可）
pip install --no-deps pyorbbecsdk2
```

> ⚠️ 三个坑，都是实测踩过的：
> 1. **必须 `--no-deps`**：pyorbbecsdk2 的依赖声明会拖入 numpy<2.0 +
>    open3d/dash，破坏现有 NumPy/OpenCV/MediaPipe 和 colcon 环境。
>    SDK 本体运行时只需要 numpy，示例代码才需要那些包。
> 2. **先卸载 v1**：`pip uninstall pyorbbecsdk`（v1 和 v2 导入名相同，
>    会互相覆盖）；装完确认 `python3 -c "import pyorbbecsdk"` 通过。
> 3. **相机代码 v1/v2 双兼容**：gemini2_camera.py 对两版 API 差异
>    （深度工作模式 .name/get_name()、profile 列表遍历、帧聚合模式）
>    已做兼容，两版都能跑；推荐 v2。

## 运行环境（最终定稿）

- **系统 Python3.10 + /opt/ros/humble**，不要进 conda 环境编译/运行本工程。
- 每个新终端：`source /opt/ros/humble/setup.bash`（可设别名 `ros2up`）
  → 进工作区 → `colcon build` → `source install/setup.bash` → launch。
- 机械臂 bring-up：`ip link show can0` 确认 UP；
  否则 `sudo ip link set can0 up type can bitrate 1000000`。
- pip 依赖（系统 python）：`pyorbbecsdk2`（--no-deps）、mediapipe、
  opencv-contrib-python、motorbridge、numpy；不需要 pin/pinocchio。
  rebot_control 与 reBotArm_control_py 仓库路径在 rebot_adapter.py 顶部。

## 运行时问题修复记录（2026-10 全面审查）

1. **Pinocchio 段错误/double free（exit -11/-6）**：根因是 launch 进程内
   同时混载 ROS 与 cmeel 的 pinocchio/eigenpy/urdfdom/Boost 动态库。
   最终修复不是继续预加载补丁，而是运行时完全移除 Pinocchio：
   `urdf_kinematics.py` 用标准库 XML + NumPy 解析同一 URDF，计算 FK 和
   LOCAL_WORLD_ALIGNED 雅可比。servo 与标定工具均不再导入 Pinocchio。
2. **初始化安全顺序**：所有 URDF、限位和配置检查都在 CAN/电机使能前完成；
   CAN 初始化后的异常会触发安全回零，初始化分 1/2/3 步打印便于定位。
3. **丢手目标污染**：servo_node 此前不论 visible 真假都更新目标，
   不可见帧的 [0,0,0] 会让 lost_hold 窗口内机械臂往相机方向扎。
   已改为仅 visible 帧更新目标，不可见保持最后有效目标。
4. **q 键 / Ctrl+C 卡死**：OpenCV destroyAllWindows 假死 + spin 回调内
   shutdown 不返回 + MediaPipe close 阻塞 → 视觉节点 q/Ctrl+C 均
   `os._exit(0)` 硬退出（不持有机械臂，资源由 OS 回收）；
   servo_node 保持「保持→回零→失能」优雅安全停机。
5. **节点退出联动**：q 退出视觉节点会结束整个 launch，servo 随即安全回零；
   servo 初始化失败也会关闭视觉窗口，不再留下半套系统运行。
6. **HOME 到位检查**：必须同时确认内部命令斜坡（1°）和 CAN 实际角度
   （5°、连续 0.25s）到位；30 秒超时即报错并安全回零，不再把超时当成
   回 HOME 成功。移动期间每 2 秒打印一次目标/指令误差/实际误差。
7. **热更新旧值问题**：参数回调现在使用本次 proposed values；修改
   `ctrl_rate_hz` 时会重建伺服定时器，帧计数常量仍由控制周期自动推导。
8. **工作空间球形保护**：新增 0.42m 水平伸展软墙和硬墙，越界回 HOME 后
   锁定跟随；视觉侧同步该状态，避免要多按一次 g。
9. **YAML 静默不生效**：将错误的 `ros__parameters__` 改为 ROS2 实际识别的
   `ros__parameters`；两个节点共 77 项声明已与 YAML 逐项自动核对。
10. **标定工具导入路径**：tools/ 已适配 ROS2 包的子目录结构，新增
   `check_kinematics.py` 无 CAN 自检，不再沿用旧单脚本模块路径。
11. **异常锁存与首帧保护**：CAN 首帧无效或 HOME 后初始化失败会就地安全回零；
   伺服异常会锁定跟随、清空速度状态，非法热更新会完整回滚内部参数。
12. **SDK 信号抢占**：`enable_esc=False` 并不会关闭 rebot_control 的 SIGINT
   handler（实机日志已验证），初始化中按 q/Ctrl+C 曾由 SDK 抢先回零、随后
   又误报 HOME 超时。已改为 `install_signal_handlers=False`，退出统一由
   本程序 safe_shutdown 处理；初始化阶段中断同样先安全回零再退出。
13. **夹爪诊断链与标定文件**：servo 状态新增 vision 目标 / 适配层目标 /
   SDK 平滑指令 / CAN 实读 J7 四段显示；`gripper_j7_calibrate.py` 写入的
   `config/grasp.yaml` 现在会被 vision_node 自动加载，避免标定后运行值
   仍停留在旧 params 的问题。

## 运行

```bash
# 一键启动（跟随 + 夹爪完整模式）
ros2 launch rebot_palm_follow_grasp palm_follow_grasp.launch.py

# 纯视觉演练（不碰机械臂，等价原 --no-arm）
ros2 launch rebot_palm_follow_grasp palm_follow_grasp.launch.py enable_servo:=false

# 无窗口模式（SSH；启停跟随用下文的 topic 发布）
ros2 launch rebot_palm_follow_grasp palm_follow_grasp.launch.py headless:=true

# 用工作区里的参数文件调试（改完不用 colcon build）
ros2 launch rebot_palm_follow_grasp palm_follow_grasp.launch.py \
    params_file:=$PWD/src/rebot_palm_follow_grasp/config/params.yaml
```

正常启动必须先看到 `URDF 解析完成`、`CAN 连接成功`、`初始 TCP 位置`，
随后才进入目标等待；若仍出现 Pinocchio/eigenpy 错误，说明运行的是旧构建副本。

操作：视觉窗口按 **g/空格** 启停跟随，**q** 退出整套系统；servo 会安全回零。
headless 模式下启停跟随：
```bash
ros2 topic pub --once /follow_enable std_msgs/msg/Bool "{data: true}"
```

退出路径（红线保留）：q 或 Ctrl+C → 机械臂保持 → 缓慢回零 → 到位 → 失能。

## 调参

全部参数集中在 `config/params.yaml`（两个节点各自一节，键内注释含范围）。
数值 = 原项目最终版实机调定值，行为一致。

**ROS2 相比原版新增的便利：在线热调参**（不用重启）：

```bash
ros2 param set /servo_node kf_q 1.8
ros2 param set /servo_node gain 2.5
ros2 param set /vision_node hybrid_track_enable false
```

注意：`kf_q` / `kf_r` 热更新会自动重置卡尔曼滤波器（防状态失配）；
`distance` 在 vision 与 servo 两侧都有（背景拒绝/冻结占位在 vision，
误差计算在 servo），**改的时候要两边同步**：
`ros2 param set /servo_node distance 0.4 && ros2 param set /vision_node distance 0.4`

新/老架构切换：`ros2 param set /servo_node kf_enable false`（或改 params.yaml）。

## 分步验证（首次部署按此顺序）

```bash
# 第 0a 步：纯运动学自检（不连接 CAN、不使能电机）
cd src/rebot_palm_follow_grasp
/usr/bin/python3 tools/check_kinematics.py
cd ../..

# 第 0b 步：纯视觉演练
ros2 launch rebot_palm_follow_grasp palm_follow_grasp.launch.py enable_servo:=false

# 第 1 步：仅夹爪——起两个节点但不启动跟随（不按 g），捏合验证开合
ros2 launch rebot_palm_follow_grasp palm_follow_grasp.launch.py

# 第 2 步：仅跟随——params.yaml 中 vision_node.gripper_enabled 设 false

# 第 3 步：完整模式
```

## 标定工具

`src/rebot_palm_follow_grasp/tools/` 下的脚本与原项目一致，
直接在源码目录运行（它们从环境变量 `REBOT_PFG_CONFIG_DIR` 或
包内 `config/` 找标定文件）：

```bash
export REBOT_PFG_CONFIG_DIR=$PWD/src/rebot_palm_follow_grasp/config
cd src/rebot_palm_follow_grasp
python3 tools/gripper_j7_calibrate.py     # 夹爪开合标定 → 回写 params.yaml
python3 tools/handeye_joint_calib.py      # 手眼标定 → hand_eye_calibration.json
python3 tools/teach_home.py               # 示教 HOME 位姿
```

## 与原单脚本版的对照

| 原 palm_follow_grasp.py | ROS2 版位置 |
| --- | --- |
| 视觉主循环（取帧/检测/桥接/深度链/捏合） | vision_node._vision_cycle |
| 伺服控制线程 servo_control_loop | servo_node._servo_cycle |
| 夹爪 set_gripper_deg（视觉侧直发） | vision 算目标角 → servo 冻结门控后下发 |
| follow.yaml + grasp.yaml | config/params.yaml（键名扁平化，注释保留范围） |
| 键盘 g/q（pynput + OpenCV） | vision_node 窗口按键 → /follow_enable；headless 用 topic |
| 命令行 --no-arm / --no-follow / --headless | launch 参数 enable_servo / params.yaml gripper_enabled / headless |
| DBG 行 | vision_node 日志（合并 /servo_status 的 joint_speed/tcp/err） |

技术原理与踩坑记录见原项目《技术手册.md》（一并附在 docs/ 下）。

MIT License.
