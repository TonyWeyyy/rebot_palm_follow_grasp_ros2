#!/usr/bin/env python3
"""servo_node —— 跟随伺服 + 夹爪下发节点（ROS2 版）

职责（与原 palm_follow_grasp.py 的伺服控制线程逐一对应）：
  - 唯一持有 RebotAdapter（单一 CAN 主机红线：夹爪走 rebot_control 第 7 通道）
  - 订阅 /palm_target（vision_node 发布），100Hz 伺服循环：
    卡尔曼目标滤波（新架构）/ 帧间差分+EMA（老架构）、静止锁存、
    死区回差、丢失外推、伸展衰减、软墙/硬墙、奇异保护、加速度限制
  - 夹爪冻结门控（手臂运动时冻结）在本节点——只有它知道关节速度
  - 订阅 /follow_enable（Bool，vision_node 的键盘 g/空格 发布）
  - 发布 /servo_status（String，JSON，2Hz：joint_speed/tcp/err/ffm）

安全红线（与原版本一致，不可删）：
  - 退出路径：保持 → 缓慢回零(return_to_zero=True, wait=True) → 确认到位 → 失能
  - 严禁在非零位/非重力平衡位姿直接失能电机（屈肘失能 = 自由下落事故）
  - 帧计数常量全部由控制周期推导（改 ctrl_rate_hz 不用手改别的）
"""

import json
import os
import time

import numpy as np

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rcl_interfaces.msg import SetParametersResult
from std_msgs.msg import Bool, String

from rebot_interfaces.msg import PalmTarget

from .kalman_target import KalmanTarget3D
from .servo_math import (compute_damped_pseudoinverse, compute_manipulability,
                         compute_orientation_error, compute_tcp_fk_and_jacobian,
                         camera_velocity_to_tcp)


def _cfg_path(name):
    """配置文件解析（与库模块同一约定：环境变量 > 包内 config/）。"""
    env_dir = os.environ.get("REBOT_PFG_CONFIG_DIR")
    mod_dir = os.path.dirname(os.path.abspath(__file__))
    for c in (os.path.join(env_dir, name) if env_dir else None,
              os.path.join(mod_dir, "..", "config", name),
              os.path.join(mod_dir, "config", name)):
        if c and os.path.exists(c):
            return os.path.abspath(c)
    return None


class ServoNode(Node):
    def __init__(self):
        super().__init__("servo_node")

        # ── 参数声明（config/params.yaml 覆盖；全部可 ros2 param set 在线调）──
        P = self.declare_parameter
        P("distance", 0.35)
        P("gain", 2.35)
        P("gain_x", 2.4)
        P("max_vel", 0.50)
        P("max_vel_joint", 1.50)
        P("max_vel_angular", 1.50)
        P("position_deadband", 0.022)
        P("deadband_hysteresis", 1.6)
        P("orientation_deadband_deg", 2.0)
        P("vel_feedforward", 1.0)
        P("ff_smooth", 0.55)
        P("ff_max_vel", 0.7)
        P("ff_min_speed", 0.030)
        P("ff_taper_dist", 0.07)
        P("kf_enable", True)
        P("kf_q", 1.5)
        P("kf_r", 0.004)
        P("kf_lead_ms", 8.0)
        P("kf_ff_deadband_off", 0.06)
        P("kf_ff_deadband_on", 0.13)
        P("kf_ff_exit_frames", 7)
        P("kf_hold_tol", 0.04)
        P("kf_resync_frames", 3)
        P("kf_adapt_enable", False)
        P("kf_adapt_ref", 0.10)
        P("kf_adapt_max", 2.5)
        P("kf_adapt_decay", 0.85)
        P("smooth_alpha", 0.48)
        P("reversal_fast_response", True)
        P("max_accel", 2.8)
        P("reversal_accel_boost", 2.0)
        P("reach_soft_start", 0.27)
        P("reach_soft_end", 0.40)
        P("reach_min_scale", 0.58)
        P("reach_dock_dist", 0.21)
        P("reach_att_tau", 0.15)
        P("k_orientation", 1.6)
        P("lost_hold_s", 0.30)
        P("coast_window_s", 0.12)
        P("coast_decay_per20ms", 0.90)
        P("coast_max_vel", 0.35)
        P("gripper_hold_while_moving", True)
        P("gripper_move_speed_threshold", 0.05)
        P("gripper_deadband_deg", 2.0)
        P("servo_direction", 1.0)
        P("damping_base", 0.010)
        P("damping_adaptive", True)
        P("manipulability_threshold", 0.004)
        P("min_manip_speed_scale", 0.35)
        P("ctrl_rate_hz", 100.0)
        P("workspace_min", [-0.40, -0.10, 0.03])
        P("workspace_max", [0.40, 0.40, 0.60])
        P("workspace_radius", 0.42)  # 70% 臂展规则，单位 m，禁止调大

        self._reload_params()
        # 在线调参：ros2 param set /servo_node kf_q 1.8（安全热更新，无锁竞争）
        self.add_on_set_parameters_callback(self._on_params)

        # ── 手眼标定与 HOME ──
        calib_file = _cfg_path("hand_eye_calibration.json")
        if calib_file is None:
            raise FileNotFoundError(
                "未找到 hand_eye_calibration.json，请先运行 "
                "tools/handeye_joint_calib.py 完成标定")
        with open(calib_file) as f:
            self.T_tcp_camera = np.array(json.load(f)["T_tcp_camera"])

        self.HOME_JOINT_POS = [0.0, 1.2, 1.05, 0.0, 0.0, 0.0]
        home_file = _cfg_path("home_pose.json")
        if home_file is not None:
            with open(home_file) as f:
                home = json.load(f)
            self.HOME_JOINT_POS = home["home_joint_pos"]
            self.get_logger().info(
                f"[HOME] 使用示教 HOME: {np.round(self.HOME_JOINT_POS, 3).tolist()}")

        # ── 机械臂（本节点唯一持有）──
        from .rebot_adapter import RebotAdapter
        self.get_logger().info("初始化机械臂...")
        self.robot = RebotAdapter()
        try:
            self.get_logger().info(
                "正在低速移动到示教 HOME（预计数秒；此阶段 g/空格 无效，"
                "可按 q 或 Ctrl+C 触发安全回零）...")
            self.robot.move_to_joints(self.HOME_JOINT_POS, speed_deg_s=15.0,
                                      wait=True, timeout=30.0)
            time.sleep(0.5)
            fk_home = self.robot.forward_kinematics()
            self.desired_rotation = np.array(fk_home["rotation"])
            self.get_logger().info(
                f"初始 TCP 位置: {np.array(fk_home['position']).round(3)} m")
        except BaseException:
            # HOME/CAN 读数失败或被 Ctrl+C 中断时，都不能带着已使能电机
            # 直接退出。BaseException 覆盖 KeyboardInterrupt/SystemExit。
            try:
                self.robot.stop()
            except Exception as stop_exc:
                print(f"[servo_node] 初始化失败后的安全回零也失败: {stop_exc}",
                      flush=True)
            raise

        # 夹爪：以当前实际角为起点，避免启动猛动
        self.last_sent_gripper_deg = float(self.robot.get_gripper_deg())
        self.latest_pinch_deg = None          # vision 侧滤波后的目标角
        self.latest_pinch_valid = False       # 当前消息是否带有效捏合目标
        self._last_gripper_actual_read = 0.0  # 低频 CAN 实读时间戳
        self._last_gripper_target_log = 0.0

        # ── 目标状态（由 /palm_target 订阅维护）──
        self.target_cam = None
        self.target_frozen = False
        self.palm_visible = False
        self.last_target_time = 0.0
        self.following = False
        self.camera_fps = 60.0   # 仅用于 KF 跳变守卫的阈值推导

        # ── 伺服内部状态 ──
        self.actual_velocity = np.zeros(6)
        self.prev_cmd_vel = np.zeros(3)
        self.lost_counter = 0
        self.prev_target_cam = None
        self.target_vel_f = np.zeros(3)
        self.in_deadband = False
        self.coast_offset = np.zeros(3)
        self.coast_vel = np.zeros(3)
        self.coast_err = 1e9
        self.near_wall = True
        self.reach_r_now = 0.0
        self.reach_att = 1.0
        self.kf = KalmanTarget3D(q=self.kf_q, r=self.kf_r)
        self.kf_last_meas = None
        self.kf_reject_count = 0
        self.kf_rejected_now = False
        self.ff_moving = False
        self.ff_exit_count = 0
        self.hold_latch = None
        self.status = {"joint_speed": 0.0, "error": "", "active": False,
                       "ffm": True, "tcp": None,
                       "gripper_rx_valid": False, "gripper_rx_deg": None,
                       "gripper_frozen": False,
                       "gripper_target": round(self.last_sent_gripper_deg, 1),
                       "gripper_cmd": None, "gripper_actual": None,
                       "gripper_actual_error": ""}

        # ── ROS 接口 ──
        self.create_subscription(PalmTarget, "/palm_target",
                                 self._on_target, 10)
        self.create_subscription(Bool, "/follow_enable",
                                 self._on_enable, 10)
        self.status_pub = self.create_publisher(String, "/servo_status", 10)
        self.create_timer(0.5, self._publish_status)

        self.get_logger().info(
            f"跟随参数: 距离 {self.desired_depth}m  gain(x/y/z)="
            f"{self.lambda_gain_xyz.tolist()}  max_vel={self.max_vel_cart}  "
            f"前馈={self.vel_feedforward}")
        if self.kf_enable:
            self.get_logger().info(
                f"卡尔曼: Q={self.kf_q} R={self.kf_r} lead={self.kf_lead_ms}ms  "
                f"速度死区={self.kf_deadband_off}/{self.kf_deadband_on}m/s")
        self.get_logger().info("等待 vision_node 目标（/palm_target）；"
                               "g/空格（视觉窗口）启停跟随")

        # 伺服主循环定时器
        self.servo_timer = self.create_timer(self.ctrl_dt, self._servo_cycle)

    # ── 参数装载 / 在线更新 ──────────────────────────────────

    def _reload_params(self, overrides=None):
        # on_set_parameters 回调发生在 ROS 真正写入参数之前；热更新时必须
        # 优先读取本次 proposed values，否则内部会错误地继续使用旧值。
        overrides = overrides or {}
        g = lambda n: (overrides[n] if n in overrides
                       else self.get_parameter(n).value)
        self.desired_depth = float(g("distance"))
        if not 0.18 <= self.desired_depth <= 0.60:
            raise ValueError("distance 须在 0.18~0.60 m 之间")
        self.lambda_gain_xyz = np.array([float(g("gain_x")),
                                         float(g("gain")), float(g("gain"))])
        self.max_vel_cart = float(g("max_vel"))
        self.max_vel_joint = float(g("max_vel_joint"))
        self.max_vel_angular = float(g("max_vel_angular"))
        self.position_deadband = float(g("position_deadband"))
        self.deadband_hysteresis = float(g("deadband_hysteresis"))
        self.orientation_deadband = np.deg2rad(float(g("orientation_deadband_deg")))
        self.vel_feedforward = float(g("vel_feedforward"))
        self.ff_smooth = float(g("ff_smooth"))
        self.ff_max_vel = float(g("ff_max_vel"))
        self.ff_min_speed = float(g("ff_min_speed"))
        self.ff_taper_dist = float(g("ff_taper_dist"))
        self.kf_enable = bool(g("kf_enable"))
        self.kf_q = float(g("kf_q"))
        self.kf_r = float(g("kf_r"))
        self.kf_lead_ms = float(g("kf_lead_ms"))
        self.kf_deadband_off = float(g("kf_ff_deadband_off"))
        self.kf_deadband_on = float(g("kf_ff_deadband_on"))
        self.kf_exit_frames = int(g("kf_ff_exit_frames"))
        self.kf_hold_tol = float(g("kf_hold_tol"))
        self.kf_resync_frames = int(g("kf_resync_frames"))
        self.kf_adapt_enable = bool(g("kf_adapt_enable"))
        self.kf_adapt_ref = float(g("kf_adapt_ref"))
        self.kf_adapt_max = float(g("kf_adapt_max"))
        self.kf_adapt_decay = float(g("kf_adapt_decay"))
        self.smooth_alpha = float(g("smooth_alpha"))
        self.reversal_fast_response = bool(g("reversal_fast_response"))
        self.max_accel = float(g("max_accel"))
        self.reversal_accel_boost = float(g("reversal_accel_boost"))
        self.reach_soft_start = float(g("reach_soft_start"))
        self.reach_soft_end = float(g("reach_soft_end"))
        self.reach_min_scale = float(g("reach_min_scale"))
        self.reach_dock_dist = float(g("reach_dock_dist"))
        self.reach_att_tau = float(g("reach_att_tau"))
        self.k_orientation = float(g("k_orientation"))
        ctrl_rate = float(g("ctrl_rate_hz"))
        if not 20.0 <= ctrl_rate <= 200.0:
            raise ValueError("ctrl_rate_hz 必须在 20~200Hz 之间")
        self.ctrl_dt = 1.0 / ctrl_rate
        # 帧计数常量由控制周期推导（红线：不手改）
        self.lost_hold_frames = round(float(g("lost_hold_s")) / self.ctrl_dt)
        self.coast_frames = round(float(g("coast_window_s")) / self.ctrl_dt)
        self.coast_decay = float(g("coast_decay_per20ms")) ** (self.ctrl_dt / 0.02)
        self.coast_max_vel = float(g("coast_max_vel"))
        self.gripper_hold_moving = bool(g("gripper_hold_while_moving"))
        self.gripper_move_thresh = float(g("gripper_move_speed_threshold"))
        self.gripper_deadband = float(g("gripper_deadband_deg"))
        self.servo_direction = float(g("servo_direction"))
        self.damping_base = float(g("damping_base"))
        self.damping_adaptive = bool(g("damping_adaptive"))
        self.manip_threshold = float(g("manipulability_threshold"))
        self.min_manip_scale = float(g("min_manip_speed_scale"))
        self.workspace_min = np.array(g("workspace_min"), dtype=np.float64)
        self.workspace_max = np.array(g("workspace_max"), dtype=np.float64)
        if (self.workspace_min.shape != (3,) or self.workspace_max.shape != (3,)
                or not np.all(np.isfinite(self.workspace_min))
                or not np.all(np.isfinite(self.workspace_max))
                or np.any(self.workspace_min >= self.workspace_max)):
            raise ValueError("workspace_min/max 必须是逐轴递增的 3 维有限边界")
        self.workspace_radius = float(g("workspace_radius"))
        if not 0.10 <= self.workspace_radius <= 0.42:
            raise ValueError("workspace_radius 必须在 0.10~0.42m 内（70% 臂展红线）")

    def _on_params(self, params):
        # 参数校验必须可回滚：若某一项非法，不能把前面已赋值的内部状态
        # 留在“新值”，而 ROS 参数服务器仍保持“旧值”的分裂状态。
        before = dict(self.__dict__)
        try:
            names = {p.name for p in params}
            self._reload_params({p.name: p.value for p in params})
            # KF 结构性参数变化时重置滤波器（防状态与新参数不匹配）
            if names & {"kf_q", "kf_r"}:
                self.kf = KalmanTarget3D(q=self.kf_q, r=self.kf_r)
                self.kf_last_meas = None
                self.hold_latch = None
            if "ctrl_rate_hz" in names and hasattr(self, "servo_timer"):
                self.destroy_timer(self.servo_timer)
                self.servo_timer = self.create_timer(self.ctrl_dt,
                                                     self._servo_cycle)
            self.get_logger().info(f"参数已热更新: {sorted(names)}")
            return SetParametersResult(successful=True)
        except Exception as exc:
            self.__dict__.update(before)
            return SetParametersResult(successful=False, reason=str(exc))

    # ── 订阅回调 ────────────────────────────────────────────

    def _on_target(self, msg: PalmTarget):
        # 只有可见帧才更新目标位置！不可见帧 msg.position 是 [0,0,0]，
        # 若照单全收，丢手后的 lost_hold 窗口（0.3s）伺服会拿原点当目标
        # 往相机方向扎。不可见时保留最后有效目标，交给丢失外推/保持链。
        if msg.visible:
            self.target_cam = np.array(msg.position, dtype=np.float64)
            self.target_frozen = bool(msg.frozen)
            self.palm_visible = True
        else:
            self.palm_visible = False
        self.last_target_time = time.time()   # 话题活性（超时也判丢失）
        # 每个消息都刷新有效性；无效帧只保持旧目标，不更新。
        self.latest_pinch_valid = bool(msg.pinch_valid)
        if msg.pinch_valid:
            self.latest_pinch_deg = float(msg.pinch_deg)

    def _on_enable(self, msg: Bool):
        if bool(msg.data) != self.following:
            self.following = bool(msg.data)
            self.get_logger().info(
                "[跟随] 启动" if self.following else "[跟随] 停止（保持当前位置）")

    # ── 状态发布（2Hz，vision_node 合并进 DBG 行）─────────────

    def _publish_status(self):
        s = dict(self.status)
        s["following"] = self.following

        # 夹爪诊断链：vision 目标 → 适配层缓存目标 → SDK 平滑指令 → CAN 实读。
        try:
            s["gripper_target"] = round(float(self.robot.get_gripper_deg()), 1)
        except Exception as exc:
            s["gripper_target"] = None
            s["gripper_actual_error"] = f"目标读取失败: {exc}"
        try:
            s["gripper_cmd"] = round(float(self.robot.get_gripper_command_deg()), 1)
        except Exception as exc:
            s["gripper_cmd"] = None
            s["gripper_actual_error"] = f"指令读取失败: {exc}"

        # 实际 J7 用低频同步 CAN 读（7 路串行读不能放进 100Hz 热循环）。
        now = time.time()
        if now - self._last_gripper_actual_read >= 2.0:
            self._last_gripper_actual_read = now
            try:
                s["gripper_actual"] = round(float(self.robot.read_gripper_deg()), 1)
                s["gripper_actual_error"] = ""
            except Exception as exc:
                s["gripper_actual"] = None
                s["gripper_actual_error"] = f"实读失败: {exc}"

        m = String()
        m.data = json.dumps(s)
        self.status_pub.publish(m)

    # ── 伺服主循环（与原 servo_control_loop 逐一对应）────────

    def _servo_cycle(self):
        dt = self.ctrl_dt
        target_cam = (None if self.target_cam is None
                      else np.array(self.target_cam, dtype=np.float64))
        frozen_meas = self.target_frozen
        # 话题超时（vision 崩溃/未启动）等效手掌丢失
        visible = (self.palm_visible
                   and (time.time() - self.last_target_time) < 0.15)

        if not visible:
            self.lost_counter += 1
        else:
            self.lost_counter = 0

        # ── 卡尔曼目标滤波维护（新架构）──
        if self.kf_enable:
            self.kf_rejected_now = False
            if visible and target_cam is not None and not frozen_meas:
                new_meas = (self.kf_last_meas is None
                            or np.linalg.norm(target_cam - self.kf_last_meas) > 1e-9)
                if new_meas:
                    if self.kf.initialized:
                        innov = float(np.linalg.norm(target_cam - self.kf.position()))
                        gate = (0.06 + 2.0 * float(np.linalg.norm(self.kf.velocity()))
                                * (1.0 / max(self.camera_fps, 1.0)))
                    else:
                        innov, gate = 0.0, 1e9
                    if innov > gate:
                        self.kf_reject_count += 1
                        self.kf_rejected_now = True
                        if self.kf_reject_count >= self.kf_resync_frames:
                            self.kf.reset()
                            self.kf.update(target_cam, dt)
                            self.kf_reject_count = 0
                            self.hold_latch = None
                            self.status["error"] = "KF重同步"
                        else:
                            self.kf.q_scale = max(1.0, self.kf.q_scale
                                                  * self.kf_adapt_decay)
                            self.kf.predict(dt)
                    else:
                        if self.kf_adapt_enable:
                            self.kf.q_scale = float(np.clip(
                                innov / self.kf_adapt_ref, 1.0, self.kf_adapt_max))
                        self.kf.update(target_cam, dt)
                        self.kf_reject_count = 0
                    self.kf_last_meas = target_cam.copy()
                else:
                    self.kf.q_scale = max(1.0, self.kf.q_scale * self.kf_adapt_decay)
                    self.kf.predict(dt)
            else:
                self.kf.q_scale = max(1.0, self.kf.q_scale * self.kf_adapt_decay)
                self.kf.predict(dt)

            # 速度死区（带回差）+ 跳出确认帧
            kv = self.kf.velocity()
            kvn = float(np.linalg.norm(kv))
            was_moving = self.ff_moving
            if self.ff_moving:
                if kvn < self.kf_deadband_off:
                    self.ff_moving = False
                    self.ff_exit_count = 0
            elif kvn > self.kf_deadband_on:
                self.ff_exit_count += 1
                if self.ff_exit_count >= self.kf_exit_frames:
                    self.ff_moving = True
                    self.ff_exit_count = 0
            else:
                self.ff_exit_count = 0
            if self.ff_moving != was_moving:
                self.status["ffm"] = self.ff_moving

            # 静止目标锁存
            if self.ff_moving:
                self.hold_latch = None
            elif self.kf.initialized:
                if self.hold_latch is None:
                    self.hold_latch = self.kf.position().copy()
                else:
                    d = self.kf.position() - self.hold_latch
                    dn = float(np.linalg.norm(d))
                    if dn > self.kf_hold_tol:
                        step = min(dn - self.kf_hold_tol, 0.06 * dt)
                        self.hold_latch = self.hold_latch + d / dn * step
            if self.ff_moving:
                self.target_vel_f = np.clip(kv, -self.ff_max_vel, self.ff_max_vel)
            else:
                self.target_vel_f = np.zeros(3)

        # ── 丢失外推（滑行）──
        if visible:
            self.coast_offset[:] = 0.0
            cv = self.target_vel_f.copy()
            cvn = float(np.linalg.norm(cv))
            if cvn > self.coast_max_vel:
                cv *= self.coast_max_vel / cvn
            self.coast_vel = cv
            self.coast_err = float(np.linalg.norm(
                target_cam - np.array([0.0, 0.0, self.desired_depth]))) \
                if target_cam is not None else 1e9
        elif (target_cam is not None and 0 < self.lost_counter <= self.coast_frames
                and self.coast_err < 0.15
                and not self.near_wall
                and self.reach_r_now <= self.reach_soft_start):
            self.coast_offset += self.coast_vel * dt
            self.coast_vel *= self.coast_decay
        if target_cam is not None and self.lost_counter > 0:
            target_cam = target_cam + self.coast_offset

        # ── KF 目标替换（lead 外推 / 锁存）──
        if (self.kf_enable and visible
                and self.kf.initialized and not self.kf_rejected_now):
            if self.hold_latch is not None:
                target_cam = self.hold_latch
            elif self.kf_lead_ms > 0.0:
                target_cam = (self.kf.position()
                              + self.kf.velocity() * (self.kf_lead_ms / 1000.0))

        if (self.following and target_cam is not None
                and self.lost_counter <= self.lost_hold_frames):
            self._servo_step(target_cam)
        else:
            self._hold_step()

        # ── 夹爪下发（本节点门控：手臂运动时冻结）──
        rx_valid = bool(self.latest_pinch_valid)
        rx_deg = self.latest_pinch_deg
        frozen = bool(self.gripper_hold_moving
                      and self.status["joint_speed"] > self.gripper_move_thresh)
        gripper_changed = False
        if rx_valid and rx_deg is not None:
            old_target = float(self.robot.get_gripper_deg())
            if (not frozen
                    and abs(rx_deg - self.last_sent_gripper_deg)
                    >= self.gripper_deadband):
                self.robot.set_gripper_deg(rx_deg)
                self.last_sent_gripper_deg = float(rx_deg)
                gripper_changed = True
                new_target = float(self.robot.get_gripper_deg())
                now = time.time()
                if now - self._last_gripper_target_log >= 1.0:
                    self._last_gripper_target_log = now
                    self.get_logger().info(
                        f"[夹爪] 目标 {old_target:.1f}° → {new_target:.1f}°"
                        f"（vision {rx_deg:.1f}°，关节速度="
                        f"{self.status['joint_speed']:.3f} rad/s）")

        # 诊断字段供 vision DBG 与 ros2 topic echo /servo_status 查看。
        self.status["gripper_rx_valid"] = rx_valid
        self.status["gripper_rx_deg"] = (round(float(rx_deg), 1)
                                         if rx_deg is not None else None)
        self.status["gripper_frozen"] = frozen
        self.status["gripper_target"] = round(float(self.robot.get_gripper_deg()), 1)
        self.status["gripper_target_changed"] = gripper_changed

    def _servo_step(self, target_cam):
        try:
            current_joints = self.robot.get_command_pos()
            tcp_pos, tcp_rot, J_robot = compute_tcp_fk_and_jacobian(
                self.robot, current_joints)
            self.status["tcp"] = tcp_pos.round(3).tolist()

            reach_r = float(np.hypot(tcp_pos[0], tcp_pos[1]))
            # 硬墙：笛卡尔盒或 70% 臂展圆域越界 >5cm → 回 HOME 并锁定跟随。
            if (np.any(tcp_pos < self.workspace_min - 0.05)
                    or np.any(tcp_pos > self.workspace_max + 0.05)
                    or reach_r > self.workspace_radius + 0.05):
                self.robot.hold()
                self.following = False  # 即使回 HOME 失败，也禁止下周期再次伺服
                self.get_logger().warn(
                    f"[安全] TCP 越过硬墙 {tcp_pos.round(2).tolist()}，自动回 HOME...")
                self.robot.move_to_joints(self.HOME_JOINT_POS, speed_deg_s=12.0,
                                          wait=True, timeout=30.0)
                self._reset_filters()
                self.status["error"] = "已自动回 HOME，跟随已锁定；按 g 重新启动"
                self.status["active"] = False
                self.status["joint_speed"] = 0.0
                return

            target_desired = np.array([0.0, 0.0, self.desired_depth])
            pos_err_cam = target_cam - target_desired
            pos_err_norm = float(np.linalg.norm(pos_err_cam))
            if self.in_deadband:
                if pos_err_norm > self.position_deadband * self.deadband_hysteresis:
                    self.in_deadband = False
            elif pos_err_norm < self.position_deadband:
                self.in_deadband = True
            v_cam = np.zeros(6)
            if not self.in_deadband:
                v_cam[:3] = self.servo_direction * self.lambda_gain_xyz * pos_err_cam

            # 老架构前馈（差分+EMA）；新架构前馈已在 KF 维护段写入 target_vel_f
            if self.vel_feedforward > 0.0:
                if not self.kf_enable and self.prev_target_cam is not None:
                    if np.linalg.norm(target_cam - self.prev_target_cam) < 0.06:
                        tv = (target_cam - self.prev_target_cam) / self.ctrl_dt
                        tv = np.clip(tv, -self.ff_max_vel, self.ff_max_vel)
                        self.target_vel_f = (self.ff_smooth * tv
                                             + (1 - self.ff_smooth) * self.target_vel_f)
                self.prev_target_cam = target_cam.copy()
                if self.in_deadband or \
                        np.linalg.norm(self.target_vel_f) < self.ff_min_speed:
                    self.target_vel_f = np.zeros(3)
                else:
                    ff_scale = min(1.0, pos_err_norm / self.ff_taper_dist)
                    v_cam[:3] += (self.vel_feedforward * ff_scale
                                  * self.target_vel_f)

            ori_err = compute_orientation_error(tcp_rot, self.desired_rotation)
            v_cam[:3] = self.max_vel_cart * np.tanh(v_cam[:3] / self.max_vel_cart)

            # 伸展度增益调度（EMA 平滑，只衰减停靠段）
            self.reach_r_now = reach_r
            att_target = 1.0
            if reach_r > self.reach_soft_start:
                dock = float(np.clip(
                    1.0 - pos_err_norm / self.reach_dock_dist, 0.0, 1.0))
                reach_scale = float(np.clip(
                    1.0 - (1.0 - self.reach_min_scale)
                    * (reach_r - self.reach_soft_start)
                    / max(self.reach_soft_end - self.reach_soft_start, 1e-6),
                    self.reach_min_scale, 1.0))
                att_target = 1.0 - (1.0 - reach_scale) * dock
            self.reach_att += ((att_target - self.reach_att)
                               * min(1.0, self.ctrl_dt / self.reach_att_tau))
            v_cam[:3] *= self.reach_att

            angular_world = (self.k_orientation * ori_err
                             if np.linalg.norm(ori_err) > self.orientation_deadband
                             else np.zeros(3))
            angular_world = np.clip(angular_world,
                                    -self.max_vel_angular, self.max_vel_angular)

            if (self.reversal_fast_response
                    and np.dot(v_cam[:3], self.actual_velocity[:3]) < 0):
                self.actual_velocity[:3] = 0.0

            self.actual_velocity += (v_cam - self.actual_velocity) * self.smooth_alpha

            # 加速度限制（启停梯形化；反转给 BOOST 额度）
            dv_cmd = self.actual_velocity[:3] - self.prev_cmd_vel
            accel_cap = self.max_accel
            if np.dot(self.actual_velocity[:3], self.prev_cmd_vel) < 0:
                accel_cap *= self.reversal_accel_boost
            max_dv = accel_cap * self.ctrl_dt
            dv_norm = float(np.linalg.norm(dv_cmd))
            if dv_norm > max_dv:
                self.actual_velocity[:3] = (self.prev_cmd_vel
                                            + dv_cmd * (max_dv / dv_norm))
            self.prev_cmd_vel = self.actual_velocity[:3].copy()

            # 相机系 → TCP 系 → 世界系
            v_tcp = camera_velocity_to_tcp(self.actual_velocity, self.T_tcp_camera)
            v_world = np.zeros(6)
            v_world[0:3] = tcp_rot @ v_tcp[0:3]
            v_world[3:6] = angular_world

            # 软墙：只削"继续往外走"的分量
            wall_touch = False
            for ax in range(3):
                if tcp_pos[ax] <= self.workspace_min[ax] and v_world[ax] < 0:
                    v_world[ax] = 0.0
                    wall_touch = True
                elif tcp_pos[ax] >= self.workspace_max[ax] and v_world[ax] > 0:
                    v_world[ax] = 0.0
                    wall_touch = True
            # 径向软墙：只去掉继续向 70% 臂展圆域外运动的分量，
            # 保留切向和向内的运动，避免硬墙死锁。
            if reach_r >= self.workspace_radius and reach_r > 1e-9:
                outward = float(np.dot(tcp_pos[:2], v_world[:2]))
                if outward > 0.0:
                    v_world[:2] -= (outward / (reach_r ** 2)) * tcp_pos[:2]
                    wall_touch = True
            self.near_wall = bool(
                np.any(tcp_pos < self.workspace_min + 0.05)
                or np.any(tcp_pos > self.workspace_max - 0.05)
                or reach_r > self.workspace_radius - 0.05)

            # 可操作度自适应阻尼（奇异保护）
            manip = compute_manipulability(J_robot)
            if self.damping_adaptive and manip < self.manip_threshold:
                damping = self.damping_base * (
                    1.0 + (self.manip_threshold - manip) * 100)
                v_world *= max(self.min_manip_scale,
                               manip / self.manip_threshold)
            else:
                damping = self.damping_base

            joint_vel = compute_damped_pseudoinverse(J_robot, damping) @ v_world
            joint_vel = np.clip(joint_vel, -self.max_vel_joint, self.max_vel_joint)
            if (self.in_deadband
                    and np.linalg.norm(ori_err) <= self.orientation_deadband):
                joint_vel[:] = 0.0

            self.robot.joint_vel_cmd(joint_vel)   # 第 7 通道自动携带夹爪目标角
            self.status["joint_speed"] = float(np.linalg.norm(joint_vel))
            st = "贴墙滑动中" if wall_touch else ""
            if self.reach_att < 0.95:
                st += ("" if not st else " ") + f"伸展衰减x{self.reach_att:.2f}"
            self.status["error"] = st
            self.status["active"] = True

        except Exception as exc:
            # 控制异常必须锁存为停止，不能下一周期带着旧速度自动重试。
            self.following = False
            self.actual_velocity = np.zeros(6)
            self.prev_cmd_vel[:] = 0.0
            self._reset_filters()
            try:
                self.robot.hold()
            except Exception as hold_exc:
                exc = f"{exc}；保持指令也失败: {hold_exc}"
            self.status["error"] = f"控制异常，跟随已锁定: {exc}"
            self.status["active"] = False
            self.status["joint_speed"] = 0.0

    def _hold_step(self):
        """未启动跟随 / 丢手超阈值：手臂保持不动，状态复位。"""
        self.actual_velocity = np.zeros(6)
        self.prev_cmd_vel[:] = 0.0
        self.prev_target_cam = None
        self._reset_filters()
        self.in_deadband = False
        self.coast_offset[:] = 0.0
        self.coast_vel[:] = 0.0
        self.coast_err = 1e9
        self.robot.hold()
        self.status["joint_speed"] = 0.0
        self.status["active"] = False
        if self.following and self.lost_counter > self.lost_hold_frames:
            self.status["error"] = "手掌丢失，保持位置"

    def _reset_filters(self):
        self.kf.reset()
        self.kf_last_meas = None
        self.kf_reject_count = 0
        self.ff_moving = False
        self.ff_exit_count = 0
        self.hold_latch = None
        self.reach_att = 1.0
        self.target_vel_f = np.zeros(3)

    # ── 安全停机（红线：保持 → 缓慢回零 → 到位 → 失能）────────

    def safe_shutdown(self):
        if getattr(self, "_shutdown_done", False):
            return
        self._shutdown_done = True
        self.following = False
        if hasattr(self, "servo_timer"):
            self.servo_timer.cancel()
        self.get_logger().info("机械臂保持当前位置...")
        try:
            self.robot.hold()
            time.sleep(0.3)
            self.get_logger().info("正在安全回零（约3秒），请勿重复按键...")
            self.robot.stop()   # return_to_zero=True, wait=True（适配层默认）
        except Exception as exc:
            # 明确报警，绝不把失败的回零当作安全停机成功。
            self.get_logger().error(f"停机流程异常，机械臂可能尚未安全回零: {exc}")


def main(args=None):
    rclpy.init(args=args)
    try:
        node = ServoNode()
    except KeyboardInterrupt:
        # 初始化阶段按 q/Ctrl+C：ServoNode 内部已完成安全回零，这里安静退出。
        print("[servo_node] 初始化被用户中断，已完成安全回零", flush=True)
        if rclpy.ok():
            rclpy.shutdown()
        raise SystemExit(0)
    except BaseException as exc:
        # 初始化失败要显式报错退出，不能让节点半死不活地挂着
        print(f"[servo_node] 初始化失败: {exc}", flush=True)
        if rclpy.ok():
            rclpy.shutdown()
        raise SystemExit(1)
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.safe_shutdown()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
