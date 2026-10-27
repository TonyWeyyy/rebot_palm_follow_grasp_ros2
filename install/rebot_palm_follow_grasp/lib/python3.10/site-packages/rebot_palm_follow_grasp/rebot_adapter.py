#!/usr/bin/env python3
"""
reBot Arm B601-RS 机械臂适配层
替代原项目的 Panthera_lib.Panthera，对外暴露几乎相同的接口，
使得视觉伺服主程序（palm_follow_grasp.py）里的控制数学可以原样保留。

设计：
  ┌─ 运动下发：rebot_control（LAN-GER/rebot_control，MIT 位置控制 + 关节限速）
  │     原项目的 robot.Joint_Vel(关节速度) 在这里实现为：
  │     每个控制周期把关节速度积分成位置目标 q_target += dq*dt，
  │     再调 set_joint_angles()，由库内部 200Hz 平滑斜坡执行。
  │     效果等价于速度伺服，且天然带每关节速度上限保护。
  │
  ├─ 夹爪（J7）：通过 set_joint_angles 的第 7 个通道下发（单位：度），
  │     用 set_gripper_deg() 设置目标角。与 6 关节共用同一 CAN 主机，
  │     不存在第二个 motorbridge 连接争抢电机 7 的问题。
  │
  └─ 运动学：NumPy 直接解析 reBotArm_control_py 仓库里的 URDF，
        FK 与雅可比坐标定义和原 Pinocchio 版本一致，不加载 C++ 运动学库

依赖：
    git clone https://github.com/LAN-GER/rebot_control.git
    pip install motorbridge pynput pyyaml numpy
    URDF 来自 https://github.com/Seeed-Projects/reBotArm_control_py 的 urdf/ 目录

⚠️ 使用前先核对：
    1. 你机器上 rebot_control 的实际类名/方法名（不同版本可能有出入，
       本文件所有对机械臂 SDK 的调用都集中在 _ArmIO 类里，只需改这一个类）
    2. URDF 路径与关节名称（B601_RS_JOINT_NAMES）
    3. 单位：rebot_control 用【度】，URDF 运动学用【弧度】，适配层对外一律用弧度

⚠️ 安全停机约定（2026-09 事故后修订）：
    stop() 必须走 rebot_control 的「缓慢回零 → 到位后失能」完整流程
    （return_to_zero=True, wait=True）。
    严禁在任何非零位/非重力平衡位姿下直接失能电机——
    屈肘姿态下失能 = 机械臂自由下落（已发生过真实事故）。
"""

import os
import sys
import time
import numpy as np

# 运动学只使用 NumPy + 标准库 XML 解析。servo_node 不再导入 Pinocchio，
# 因而 ROS/cmeel 的 eigenpy、urdfdom、Boost 等 C++ 库不可能再混载。
try:
    from .urdf_kinematics import URDFKinematics
except ImportError:  # tools/ 下以源码顶层模块方式运行
    from urdf_kinematics import URDFKinematics

# ─────────────────────────────────────────────────────────────
# 需要你按实际环境修改的配置
# ─────────────────────────────────────────────────────────────
# rebot_control 仓库（git clone 使用，非 pip 包，需把仓库根目录加入 sys.path）
REBOT_CONTROL_PATH = os.path.expanduser(
    "~/wey/rebot_developer/MIT_control/rebot_control")

URDF_PATH = "~/wey/rebot_developer/reBotArm_control_py/urdf/RS/urdf/ReBot_Arm_RS.urdf"

# B601 RS 的 6 个关节在 URDF 里的名称（按 1→6 顺序，已在 ReBot_Arm_RS.urdf 中核对）
B601_RS_JOINT_NAMES = ["joint1", "joint2", "joint3",
                       "joint4", "joint5", "joint6"]

# 软件关节限位（弧度）。rebot_control 明确声明【不含软件限位】，必须在这里加。
# 先用 URDF 里的 limit 再向内收 10° 作为保守值，跑顺后再放宽。
JOINT_LIMIT_MARGIN = np.deg2rad(10.0)

# ── 关节零位修正（2026-09-30 手眼+零位联合标定实测）──────────────
# SDK 上报的关节角零位与 URDF 的关节零位存在固定小偏差
# （实测约 J2=0.75° J3=0.46° J4=-2.06° J5=-2.21°）。
# 不加修正时 FK 平移与实物系统性偏差 ~30%，手眼标定/视觉伺服全挂。
# 修正只作用于 FK/雅可比（_build_q_full），不影响下发给 SDK 的角度。
import json as _json


def _resolve_config_file(name):
    """配置文件解析：环境变量 REBOT_PFG_CONFIG_DIR（launch 注入的
    ament share 目录）> 模块相对 config/ > 包根 config/（源码树直跑）。"""
    cands = []
    env_dir = os.environ.get("REBOT_PFG_CONFIG_DIR")
    if env_dir:
        cands.append(os.path.join(env_dir, name))
    mod_dir = os.path.dirname(os.path.abspath(__file__))
    cands.append(os.path.join(mod_dir, "config", name))
    cands.append(os.path.join(mod_dir, "..", "config", name))
    for c in cands:
        if os.path.exists(c):
            return os.path.abspath(c)
    return os.path.abspath(cands[1])   # 默认返回模块相对路径（报错信息友好）

_JOINT_OFFSET_FILE = _resolve_config_file("joint_offset.json")
if os.path.exists(_JOINT_OFFSET_FILE):
    with open(_JOINT_OFFSET_FILE) as _f:
        JOINT_OFFSET = np.array(_json.load(_f)["joint_offset_rad"],
                                dtype=np.float64)
    print(f"[RebotAdapter] 已加载关节零位修正 (度): "
          f"{np.rad2deg(JOINT_OFFSET).round(2).tolist()}")
else:
    JOINT_OFFSET = np.zeros(6)
    print("[RebotAdapter] ⚠️ 未找到 joint_offset.json，FK 将不带零位修正。"
          "请先运行 handeye_joint_calib.py")

# 每关节最大速度（弧度/秒）——双保险之一（控制层也有限幅）
# 左右跟随的速度上限 ≈ J1 限速 × 臂展，这是横向跟随的物理瓶颈。
# 已从保守值 0.6 提到 0.8；RS06 额定转速远高于此，若想更快可逐步
# 试 1.0 → 1.2（每次只提一档，观察电机温度与跟随稳定性）。
# 关节速度上限 (rad/s)：用户实测 [1.5,1.5,1.5,2.0,2.0,2.0] 效果最佳。
# RS06/RS00 额定 ≈10.5 rad/s，硬件余量很大；瓶颈在视觉延迟而非电机。
# 用户实测定案：全 2.0 效果明显优于 [1.5,1.5,1.5,2.0,2.0,2.0]（J1-J3 不憋屈）。
MAX_JOINT_SPEED = np.array([2.0, 2.0, 2.0, 2.0, 2.0, 2.0])

# ── 夹爪（J7）参数 ──────────────────────────────────────────
# J7 与 6 个关节共用同一条 CAN 总线、同一个 rebot_control 控制器，
# 夹爪目标角通过 set_joint_angles 的第 7 个通道下发（单位：度）。
# 捏合跟随需要夹爪有足够响应速度（RS00 参考 vlim≈3 rad/s ≈ 172°/s）。
GRIPPER_SPEED_DEG_S = 150.0                 # 夹爪最大速度（度/秒）
GRIPPER_SOFT_LIMIT_DEG = (-100.0, 400.0)    # 角度硬限幅（兜底保护；
                                            # 正常开合范围由 config/grasp.yaml 标定值决定，
                                            # 且应落在本范围内）

# 控制周期（位置目标积分步长）
CTRL_DT = 0.02   # 仅作 dt 钳制参照；实际积分用墙上时钟，主循环 100Hz 下行为不变


# ─────────────────────────────────────────────────────────────
# 底层 IO：所有与 rebot_control SDK 相关的调用只出现在这个类里
# ─────────────────────────────────────────────────────────────
class _ArmIO:
    def __init__(self):
        # rebot_control 是源码仓库（无 pip 包），真实包名为 rebot，
        # 控制器类为 ReBotRSMITController（已在本地仓库核对：
        # set_joint_angles 收 7 个【度】(6关节+夹爪)、set_max_speeds 单位度/秒、
        # read_joint_angles 是同步 CAN 读、stop(return_to_zero, wait)）
        if REBOT_CONTROL_PATH not in sys.path:
            sys.path.insert(0, REBOT_CONTROL_PATH)
        from rebot import ReBotRSMITController
        self.arm = ReBotRSMITController()
        # enable_esc=False + install_signal_handlers=False：
        # SDK 的 Esc/SIGINT 拦截会在主线程内触发它自己的回零线程，与
        # ROS launch 的退出信号、以及本程序的 safe_shutdown 竞争
        # （实机日志已验证：enable_esc=False 并不会关闭 SIGINT handler）。
        # 退出统一由本程序的 q/Esc/Ctrl+C 路径处理，最终同样调用
        # self.stop()（回零→保持→失能），安全性不变。
        # start 之后任一步失败，都必须在本对象内部完成安全回零；
        # 否则 _ArmIO() 尚未返回，外层还没有 self.io 可用于清理。
        try:
            self.arm.start(enable_esc=False,
                           install_signal_handlers=False)
            # 安全速度包络（度/秒）；第 7 项为夹爪
            self.arm.set_max_speeds(np.rad2deg(MAX_JOINT_SPEED).tolist()
                                    + [GRIPPER_SPEED_DEG_S])
            # 夹爪初始目标必须读实际角，读不到就失败，绝不能猜 0° 后猛动。
            angles = np.asarray(self.arm.read_joint_angles(), dtype=np.float64)
            if angles.size < 7 or not np.all(np.isfinite(angles[:7])):
                raise RuntimeError("CAN 首帧关节读数无效，拒绝继续初始化")
            self.gripper_deg = float(angles[6])
        except BaseException:
            try:
                self.arm.stop(return_to_zero=True, wait=True)
            except Exception as stop_exc:
                print(f"[_ArmIO] 初始化失败后的安全回零也失败: {stop_exc}",
                      flush=True)
            raise

    def send_joint_positions_deg(self, q_deg_7):
        q = np.asarray(q_deg_7, dtype=np.float64)
        if q.shape != (7,) or not np.all(np.isfinite(q)):
            raise ValueError("下发必须是 6 关节 + J7 共 7 个有限角度")
        self.arm.set_joint_angles(q.tolist())

    def read_joint_positions_deg(self):
        q = np.asarray(self.arm.read_joint_angles(), dtype=np.float64)
        if q.size < 6 or not np.all(np.isfinite(q[:6])):
            raise RuntimeError("CAN 关节读数无效")
        return q[:6].copy()

    def stop(self):
        """
        安全停机：缓慢回零 → 确认到位 → 才失能电机。

        ★★★ 绝对禁止改回 return_to_zero=False ★★★
        return_to_zero=False 会在当前位姿（可能是屈肘抬起等需要力矩
        对抗重力的姿态）直接失能电机，导致机械臂自由下落。

        wait=True 同样不可省略：shutdown 是守护线程，不等它跑完主线程退出时，
        解释器会把「失能电机/关闭 CAN」杀在半路上。
        """
        # 不吞异常：调用者必须知道安全回零是否真正完成。
        self.arm.stop(return_to_zero=True, wait=True)


# ─────────────────────────────────────────────────────────────
# 对外适配器：接口对齐 Panthera
# ─────────────────────────────────────────────────────────────
class RebotAdapter:
    def __init__(self, urdf_path=URDF_PATH, joint_names=B601_RS_JOINT_NAMES):
        # 所有可能失败的纯软件初始化都在 CAN/电机使能之前完成。
        print("[RebotAdapter] 1/3 解析 URDF（NumPy 运动学，不加载 Pinocchio）...",
              flush=True)
        self.joint_names = list(joint_names)
        self.motor_count = 6
        if len(self.joint_names) != self.motor_count or JOINT_OFFSET.shape != (6,):
            raise ValueError("B601-RS 必须是 6 关节，JOINT_OFFSET 也必须是 6 维")
        self.kinematics = URDFKinematics(urdf_path, self.joint_names)
        self.q_min = self.kinematics.lower + JOINT_LIMIT_MARGIN
        self.q_max = self.kinematics.upper - JOINT_LIMIT_MARGIN
        if np.any(self.q_min >= self.q_max):
            raise ValueError("URDF 关节限位内收 10° 后无有效范围")

        print(f"[RebotAdapter] 2/3 URDF 解析完成（{self.kinematics.n_dof} 自由度），"
              "初始化 CAN/电机接口...", flush=True)
        self.io = None
        try:
            self.io = _ArmIO()
            print("[RebotAdapter] 3/3 CAN 连接成功", flush=True)
            # 初始目标 = 当前实际位置，防止使能瞬间跳动。
            self._q_target = self.get_current_pos()
            self._last_cmd_time = time.time()
        except Exception:
            # CAN 已使能后的任何初始化失败都不能直接退出进程。
            if self.io is not None:
                try:
                    self.io.stop()
                except Exception as stop_exc:
                    print(f"[RebotAdapter] 初始化失败后的安全回零也失败: {stop_exc}",
                          flush=True)
            raise

    # ── 状态读取 ─────────────────────────────────────────────
    def get_current_pos(self):
        """
        返回 6 关节实际角度（弧度）—— 对应 Panthera.get_current_pos()
        ⚠️ 这是 7 路串行同步 CAN 读（持有 io_lock，单次约数 ms~数十 ms），
        会挤占 200Hz MIT 下发线程。只允许低频使用（初始化、标定采样、
        到位等待），50Hz 伺服热循环里请用 get_command_pos()。
        """
        return np.deg2rad(self.io.read_joint_positions_deg())

    def get_command_pos(self):
        """
        返回 6 关节"当前实际下发值"（弧度）：rebot_control 内部 200Hz 斜坡
        正在发送的角度，纯内存读取、无 CAN I/O，可在伺服热循环中每周期调用。
        伺服稳态下与实际位置差异很小；需要真值时低频调用 get_current_pos() 校准。
        """
        return np.deg2rad(np.array(self.io.arm.get_command_angles()[:6],
                                   dtype=np.float64))

    # ── 运动指令 ─────────────────────────────────────────────
    def joint_vel_cmd(self, dq_rad):
        """
        对应 Panthera.Joint_Vel(dq)：关节速度指令。
        实现方式：积分成位置目标后下发（50Hz）。
        dq_rad: 6 维关节速度（rad/s），None 或全零 = 保持
        """
        now = time.time()
        # dt 上限钳制到 3 个控制周期：hold()/move_to_joints() 之后或循环卡顿
        # 时若不钳制，积分项 dq*dt 会让目标位置跳变一大步（安全隐患）
        dt = min(max(now - self._last_cmd_time, 1e-3), 3 * CTRL_DT)
        self._last_cmd_time = now

        if dq_rad is not None:
            dq = np.clip(np.asarray(dq_rad, dtype=np.float64),
                         -MAX_JOINT_SPEED, MAX_JOINT_SPEED)
            self._q_target = self._q_target + dq * dt
            # 软限位：撞到边界就把目标钉在边界上，防止积分饱和
            self._q_target = np.clip(self._q_target, self.q_min, self.q_max)

        q_deg = np.rad2deg(self._q_target).tolist()
        q_deg.append(self._gripper_keep_deg())     # 夹爪保持当前值
        self.io.send_joint_positions_deg(q_deg)

    def hold(self):
        """保持当前位置（丢手/暂停时调用）。用内部下发值重锚定，无 CAN I/O。"""
        self._q_target = self.get_command_pos().copy()
        self._last_cmd_time = time.time()   # 重置积分时钟，防止恢复后 dt 过大
        q_deg = np.rad2deg(self._q_target).tolist()
        q_deg.append(self._gripper_keep_deg())
        self.io.send_joint_positions_deg(q_deg)

    def move_to_joints(self, q_rad, speed_deg_s=20.0, wait=True, timeout=15.0):
        """低速关节空间移动；wait=True 时必须确认内部指令斜坡和实际位置都到位。

        到位判据：
          1. SDK 平滑指令角进入目标 1° 内（证明命令链没有被卡住）；
          2. 低频同步 CAN 实读角进入目标 5° 内，并持续 0.25s（吸收 MIT
             稳态误差和偶尔一次 CAN 读数抖动）。
        5° 不是放松安全：它只用于"启动 HOME/回 HOME"到位确认；运行期
        工作空间/软墙/加速度保护全部由伺服层独立完成。
        """
        q = np.asarray(q_rad, dtype=np.float64)
        if q.shape != (6,) or not np.all(np.isfinite(q)):
            raise ValueError("move_to_joints 需要 6 维有限关节角")
        if not np.isfinite(speed_deg_s) or not 0.0 < speed_deg_s <= 60.0:
            raise ValueError("speed_deg_s 必须在 0~60°/s 内")
        if wait and (not np.isfinite(timeout) or timeout <= 0.0):
            raise ValueError("timeout 必须是正数")

        command_tol = np.deg2rad(1.0)
        actual_tol = np.deg2rad(5.0)
        settle_time = 0.25
        log_period = 2.0
        self._q_target = np.clip(q, self.q_min, self.q_max)
        arrived = False
        settle_start = None
        last_log = 0.0
        last_cmd_err = None
        last_actual_err = None
        last_actual_deg = None
        last_read_error = None
        read_fail_count = 0
        t0 = time.monotonic()

        try:
            self.io.arm.set_max_speeds([speed_deg_s] * 6
                                       + [GRIPPER_SPEED_DEG_S])
            q_deg = np.rad2deg(self._q_target).tolist()
            q_deg.append(self._gripper_keep_deg())
            self.io.send_joint_positions_deg(q_deg)
            print(f"[RebotAdapter] 关节目标(°): "
                  f"{np.round(np.rad2deg(self._q_target), 2).tolist()}",
                  flush=True)
            if not wait:
                return

            while time.monotonic() - t0 < timeout:
                # q/Ctrl+C 已由上层接管；若 SDK 因任何原因进入停机流程，
                # 立刻放弃等待，不再把“控制器已停止”误报成移动超时。
                if getattr(self.io.arm, "shutdown_started", False):
                    raise RuntimeError("控制器已进入停机流程，放弃移动等待")

                cmd_err = np.abs(self.get_command_pos() - self._q_target)
                last_cmd_err = np.rad2deg(cmd_err)
                now = time.monotonic()

                if float(np.max(cmd_err)) < command_tol:
                    try:
                        actual_rad = self.get_current_pos()
                        actual_err = np.abs(actual_rad - self._q_target)
                        last_actual_err = np.rad2deg(actual_err)
                        last_actual_deg = np.rad2deg(actual_rad)
                        last_read_error = None
                        read_fail_count = 0
                    except Exception as exc:
                        # 单次 CAN 实读失败可能只是总线短暂竞争；连续失败
                        # 会在超时报错里体现，不在此误触发停机。
                        read_fail_count += 1
                        last_read_error = exc
                        actual_err = None

                    if actual_err is not None and float(np.max(actual_err)) < actual_tol:
                        if settle_start is None:
                            settle_start = now
                        elif now - settle_start >= settle_time:
                            arrived = True
                            print(f"[RebotAdapter] 到位确认: "
                                  f"指令误差={float(np.max(last_cmd_err)):.2f}° "
                                  f"实际误差={float(np.max(last_actual_err)):.2f}°",
                                  flush=True)
                            break
                    else:
                        settle_start = None
                else:
                    settle_start = None

                if now - last_log >= log_period:
                    last_log = now
                    detail = (f"指令误差={np.round(last_cmd_err, 2).tolist()}"
                              if last_cmd_err is not None else "指令误差=N/A")
                    if last_actual_err is not None:
                        detail += f" 实际误差={np.round(last_actual_err, 2).tolist()}"
                    if last_read_error is not None:
                        detail += f" 实读失败x{read_fail_count}: {last_read_error}"
                    print(f"[RebotAdapter] 移动中 {now - t0:4.1f}s/{timeout:.1f}s  "
                          f"{detail}", flush=True)

                time.sleep(0.1)
        finally:
            # 停机流程一旦已开始，set_max_speeds 只改内存且对象即将销毁；
            # 跳过可避免在 CAN 已关闭后制造无意义异常。
            if not getattr(self.io.arm, "shutdown_started", False):
                self.io.arm.set_max_speeds(np.rad2deg(MAX_JOINT_SPEED).tolist()
                                           + [GRIPPER_SPEED_DEG_S])
            self._last_cmd_time = time.time()

        if wait and not arrived:
            target_deg = np.round(np.rad2deg(self._q_target), 2).tolist()
            cmd_txt = (np.round(last_cmd_err, 2).tolist()
                       if last_cmd_err is not None else "N/A")
            act_txt = (np.round(last_actual_deg, 2).tolist()
                       if last_actual_deg is not None else "N/A")
            err_txt = (np.round(last_actual_err, 2).tolist()
                       if last_actual_err is not None else "N/A")
            raise TimeoutError(
                f"关节移动 {timeout:.1f}s 超时：目标(°)={target_deg}；"
                f"末次指令误差(°)={cmd_txt}；末次实际角(°)={act_txt}；"
                f"末次实际误差(°)={err_txt}；"
                f"CAN 实读连续失败={read_fail_count}"
                + (f"；末次读数错误={last_read_error}" if last_read_error else "")
                + "。禁止继续进入跟随，请检查 CAN、电机状态、机械阻挡或 HOME 配置")

    def stop(self):
        self.io.stop()

    def _gripper_keep_deg(self):
        # 夹爪（J7）目标角：初始化时读取并缓存，之后由 set_gripper_deg() 更新。
        # 用缓存值随每个控制周期下发，避免每周期多发一次同步 CAN 读。
        return self.io.gripper_deg

    # ── 夹爪（J7）控制 ─────────────────────────────────────
    def set_gripper_deg(self, deg):
        """设定夹爪（J7）目标角度（度），随下一次 50Hz 指令下发生效。

        带硬限幅兜底。正常开合范围请先运行 gripper_j7_calibrate.py
        实测标定（结果写入 config/grasp.yaml），不要凭猜填写。
        """
        lo, hi = GRIPPER_SOFT_LIMIT_DEG
        self.io.gripper_deg = float(np.clip(deg, lo, hi))

    def get_gripper_deg(self):
        """当前夹爪目标角度（度）"""
        return float(self.io.gripper_deg)

    def get_gripper_command_deg(self):
        """SDK 当前正在平滑下发的 J7 角度（度，纯内存读取，无 CAN I/O）。"""
        return float(self.io.arm.get_command_angles()[6])

    def read_gripper_deg(self):
        """同步 CAN 读取 J7 实际机械角度（度）。低频诊断用，勿放热循环。"""
        angles = np.asarray(self.io.arm.read_joint_angles(), dtype=np.float64)
        if angles.size < 7 or not np.isfinite(angles[6]):
            raise RuntimeError("CAN 夹爪读数无效")
        return float(angles[6])

    # ── 运动学（NumPy，单位弧度/米）─────────────────────────
    def _build_q_full(self, joint_positions):
        """保留原接口名：SDK 六关节角加零位修正，得到 URDF 六关节角。"""
        q = np.asarray(joint_positions, dtype=np.float64)
        if q.shape != (6,) or not np.all(np.isfinite(q)):
            raise ValueError("关节角必须是 6 维有限向量")
        return q + JOINT_OFFSET

    def forward_kinematics(self):
        """对应 Panthera.forward_kinematics() → {'position','rotation'}"""
        T = self.kinematics.fk(self._build_q_full(self.get_current_pos()))
        return {'position': T[:3, 3].copy(),
                'rotation': T[:3, :3].copy()}
