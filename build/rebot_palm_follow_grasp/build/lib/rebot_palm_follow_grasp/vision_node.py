#!/usr/bin/env python3
"""vision_node —— 相机 + 检测 + 深度保护链 + 捏合映射 + GUI/键盘（ROS2 版）

职责（与原 palm_follow_grasp.py 的视觉主循环逐一对应）：
  - Gemini 2 相机（60fps、手动曝光、断线自动重连）
  - MediaPipe 手掌检测 + LK 光流桥接（掉检顶帧）+ PalmTracker 平滑
  - 深度四层保护链：跳变剔除 → 重获校验（5帧一致+背景拒绝）→ 限速 → One Euro
  - 深度冻结（2D 新鲜但深度无效时冻结 z，占位 z=distance，frozen 标志）
  - 捏合(4-8 指尖距离) → One Euro/EMA → 夹爪目标角（度）
  - 发布 /palm_target（PalmTarget）；键盘 g/空格 → /follow_enable（Bool）
  - 订阅 /servo_status（String JSON），合并进 DBG 行与 HUD

捏合冻结门控在 servo_node（它才知道关节速度）；本节点只算目标角。
"""

import json
import os
import time

import numpy as np
import cv2
import yaml

import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, String

from rebot_interfaces.msg import PalmTarget

from .gemini2_camera import Gemini2Camera
from .palm_detection import (PalmDetector, PalmTracker, OneEuroFilter,
                             LKPalmBridge,
                             get_median_depth, pixel_to_3d,
                             draw_palm, draw_landmarks, pinch_distance_px)


def _cfg_path(name):
    """配置文件解析：launch 注入的 share/config > 包内 config/。"""
    env_dir = os.environ.get("REBOT_PFG_CONFIG_DIR")
    mod_dir = os.path.dirname(os.path.abspath(__file__))
    for c in (os.path.join(env_dir, name) if env_dir else None,
              os.path.join(mod_dir, "..", "config", name),
              os.path.join(mod_dir, "config", name)):
        if c and os.path.exists(c):
            return os.path.abspath(c)
    return None


class VisionNode(Node):
    def __init__(self):
        super().__init__("vision_node")

        P = self.declare_parameter
        P("fps", 60)
        P("color_exposure_ms", 6.0)
        P("detector_backend", "auto")
        P("headless", False)
        P("distance", 0.35)
        P("hybrid_track_enable", True)
        P("hybrid_max_frames", 15)
        P("hybrid_box_half", 45)
        P("hybrid_max_step_px", 90.0)
        P("z3d_max_jump", 0.08)
        P("z3d_max_rate", 0.05)
        P("z_freeze_max", 0.20)
        P("depth_oe_min_cutoff", 0.75)
        P("depth_oe_beta", 0.03)
        P("pinch_closed_px", 20.0)
        P("pinch_open_px", 200.0)
        P("pinch_filter_type", "one_euro")
        P("pinch_smoothing", 0.35)
        P("pinch_min_cutoff_hz", 2.0)
        P("pinch_beta", 0.010)
        P("pinch_dcutoff_hz", 1.0)
        P("gripper_enabled", True)
        P("gripper_closed_deg", -19.7)
        P("gripper_open_deg", 293.6)

        g = lambda n: self.get_parameter(n).value
        self.camera_fps = int(g("fps"))
        self.color_exposure_ms = float(g("color_exposure_ms"))
        self.headless = bool(g("headless"))
        self.desired_depth = float(g("distance"))
        self.z3d_max_jump = float(g("z3d_max_jump"))
        self.z3d_max_rate = float(g("z3d_max_rate"))
        self.z_freeze_max = float(g("z_freeze_max"))

        # 捏合映射（合法性检查：映射区间退化会导致 interp 异常）
        self.pinch_closed_px = float(g("pinch_closed_px"))
        self.pinch_open_px = float(g("pinch_open_px"))
        self.gripper_enabled = bool(g("gripper_enabled"))
        self.gripper_closed_deg = float(g("gripper_closed_deg"))
        self.gripper_open_deg = float(g("gripper_open_deg"))

        # gripper_j7_calibrate.py 的实测结果写入 grasp.yaml；若存在，
        # 标定文件优先于 params.yaml 中的初始值，避免“标定了但运行没用上”。
        grasp_file = _cfg_path("grasp.yaml")
        if grasp_file is not None:
            try:
                with open(grasp_file, "r", encoding="utf-8") as f:
                    grasp = yaml.safe_load(f) or {}
                calib = grasp.get("gripper", {}) if isinstance(grasp, dict) else {}
                if isinstance(calib, dict):
                    self.gripper_enabled = bool(calib.get("enabled", self.gripper_enabled))
                    self.gripper_closed_deg = float(calib.get("closed_deg", self.gripper_closed_deg))
                    self.gripper_open_deg = float(calib.get("open_deg", self.gripper_open_deg))
                    self.get_logger().info(
                        f"[夹爪标定] 使用 {grasp_file}: "
                        f"闭合 {self.gripper_closed_deg:.1f}° / "
                        f"张开 {self.gripper_open_deg:.1f}°"
                        f"{'（禁用）' if not self.gripper_enabled else ''}")
            except Exception as exc:
                self.get_logger().error(f"读取 grasp.yaml 失败，改用 params.yaml: {exc}")

        if self.pinch_open_px <= self.pinch_closed_px:
            raise ValueError("pinch_open_px 必须大于 pinch_closed_px")
        if abs(self.gripper_open_deg - self.gripper_closed_deg) < 5.0:
            raise ValueError("夹爪开合区间过小，请运行 gripper_j7_calibrate.py 重新标定")
        self.pinch_filter_type = str(g("pinch_filter_type")).lower()
        self.pinch_smoothing = float(g("pinch_smoothing"))
        self.pinch_oe = OneEuroFilter(float(g("pinch_min_cutoff_hz")),
                                      float(g("pinch_beta")))
        self.smoothed_gripper_deg = (self.gripper_closed_deg
                                     + self.gripper_open_deg) / 2.0
        if self.pinch_filter_type == "one_euro":
            self.pinch_oe(self.smoothed_gripper_deg)

        # ── 相机与检测 ──
        self.get_logger().info(f"初始化 Gemini 2 相机（{self.camera_fps} fps）...")
        self.cam = Gemini2Camera(fps=self.camera_fps,
                                 color_exposure_ms=self.color_exposure_ms)
        self.fx, self.fy, self.cx, self.cy = \
            self.cam.fx, self.cam.fy, self.cam.cx, self.cam.cy
        # 捏合像素阈值按 640 宽标定，分辨率不同按比例换算
        if self.cam.width != 640:
            scale = self.cam.width / 640.0
            self.pinch_closed_px *= scale
            self.pinch_open_px *= scale
            self.get_logger().info(
                f"[配置] 相机宽度 {self.cam.width}px，捏合阈值自动 x{scale:.2f}")
        self.desired_u = int(round(self.cx))
        self.desired_v = int(round(self.cy))

        self.get_logger().info("初始化手掌检测...")
        self.detector = PalmDetector(backend=str(g("detector_backend")))
        self.lk_bridge = LKPalmBridge(
            enable=bool(g("hybrid_track_enable")),
            max_frames=int(g("hybrid_max_frames")),
            box_half=int(g("hybrid_box_half")),
            max_step_px=float(g("hybrid_max_step_px")))
        self.tracker = PalmTracker()
        self.depth_oe = OneEuroFilter(float(g("depth_oe_min_cutoff")),
                                      float(g("depth_oe_beta")))

        # 深度保护链状态
        self.last_valid_depth = 0.0
        self.last_valid_depth_time = 0.0
        self.z3d_reject_count = 0
        self.reacq_buf = []

        # ── ROS 接口 ──
        self.target_pub = self.create_publisher(PalmTarget, "/palm_target", 10)
        self.enable_pub = self.create_publisher(Bool, "/follow_enable", 10)
        self.following = False
        self.last_toggle = 0.0
        self.servo_status = {"joint_speed": 0.0, "error": "", "active": False,
                             "ffm": True, "tcp": None, "following": False}
        self.create_subscription(String, "/servo_status",
                                 self._on_servo_status, 10)

        if not self.headless:
            cv2.namedWindow("Palm Follow + Grasp", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("Palm Follow + Grasp", 640, 480)

        self.get_logger().info(
            f"夹爪映射: 捏合 {self.pinch_closed_px:.0f}px → "
            f"{self.gripper_closed_deg:.1f}° | 张开 {self.pinch_open_px:.0f}px → "
            f"{self.gripper_open_deg:.1f}°  滤波={self.pinch_filter_type}"
            f"{'（已禁用）' if not self.gripper_enabled else ''}")
        self.get_logger().info(
            "操作: 视觉窗口按 g/空格 启停跟随 | q 退出 | Ctrl+C 退出并安全回零")

        # 视觉主循环：用 1ms 定时器驱动（相机 get_frames 自身阻塞到帧到达）
        self.fps_ema = 0.0
        self.t_prev_frame = time.time()
        self.last_frame_time = time.time()
        self.ms_grab = 0.0
        self.ms_det = 0.0
        self.quit_flag = False
        self.create_timer(0.001, self._vision_cycle)

    # ── 伺服状态订阅 ──

    def _on_servo_status(self, msg: String):
        try:
            self.servo_status = json.loads(msg.data)
            # 安全回 HOME 会由 servo 锁定跟随；同步本地按键状态，避免用户
            # 需要连按两次 g。刚按键后的 0.5s 内不回写，避免状态往返竞争。
            if ("following" in self.servo_status
                    and time.time() - self.last_toggle > 0.5):
                self.following = bool(self.servo_status["following"])
        except Exception:
            pass

    # ── 键盘 → 启停 ──

    def _toggle_tracking(self):
        now = time.time()
        if now - self.last_toggle < 0.25:
            return
        self.last_toggle = now
        self.following = not self.following
        m = Bool()
        m.data = self.following
        self.enable_pub.publish(m)
        self.get_logger().info(
            "[跟随] 启动" if self.following else "[跟随] 停止（保持当前位置）")

    # ── 视觉主循环 ──

    def _vision_cycle(self):
        if self.quit_flag:
            # q 键退出：就地清理 + 进程级硬退出。
            # 不能指望 rclpy.shutdown + destroy_node 链：OpenCV 的
            # destroyAllWindows 在部分版本上假死、spin 在回调内收到
            # shutdown 也可能不返回，任一环挂住就是"窗口冻结进程不死"。
            # os._exit 跳过所有析构直接退，视觉节点不持有机械臂，安全。
            import os as _os
            try:
                self.detector.close()
            except Exception:
                pass
            try:
                self.cam.stop()
            except Exception:
                pass
            if not self.headless:
                try:
                    cv2.destroyAllWindows()
                    for _ in range(3):
                        cv2.waitKey(1)
                except Exception:
                    pass
            self.get_logger().info("视觉节点退出")
            _os._exit(0)
            return

        t0 = time.perf_counter()
        color_image, depth_raw, depth_scale = self.cam.get_frames()
        t1 = time.perf_counter()

        if color_image is None:
            if not self.headless:
                cv2.waitKey(1)
            # 帧看门狗：连续 2 秒无有效帧 → 自动重连（USB 瞬断 SDK 不自愈）
            if time.time() - self.last_frame_time > 2.0:
                self.get_logger().warn("[相机] 超过 2 秒无有效帧，尝试断开重连...")
                try:
                    self.cam.stop()
                except Exception:
                    pass
                time.sleep(1.0)
                try:
                    self.cam = Gemini2Camera(
                        fps=self.camera_fps,
                        color_exposure_ms=self.color_exposure_ms)
                    self.last_valid_depth = 0.0
                    self.reacq_buf.clear()
                    self.get_logger().info("[相机] 重连成功")
                except Exception as exc:
                    self.get_logger().warn(f"[相机] 重连失败（{exc}），2 秒后重试...")
                self.last_frame_time = time.time()
            return
        self.last_frame_time = time.time()

        t_now = time.time()
        if t_now > self.t_prev_frame:
            self.fps_ema = (0.2 * (1.0 / (t_now - self.t_prev_frame))
                            + 0.8 * self.fps_ema)
        self.t_prev_frame = t_now

        u, v, landmarks = self.detector.detect(color_image)
        t2 = time.perf_counter()
        bu, bv, bsrc = self.lk_bridge.update(
            color_image, (u, v) if u is not None else None)
        if bsrc == "lk":
            u, v = bu, bv
            landmarks = None
        track = self.tracker.update((u, v) if u is not None else None)
        if track is not None:
            track["bridged"] = (bsrc == "lk")
        self.ms_grab = 0.9 * self.ms_grab + 0.1 * (t1 - t0) * 1000
        self.ms_det = 0.9 * self.ms_det + 0.1 * (t2 - t1) * 1000

        frozen = False
        if track is not None and track["lost"] == 0:
            ui, vi = int(round(track["u"])), int(round(track["v"]))
            depth_m = get_median_depth(depth_raw, depth_scale, ui, vi)
            # 第 1 层：深度跳变剔除（≥15 帧连续超限才放行，防锁死）
            if depth_m > 0 and self.last_valid_depth > 0 and \
                    abs(depth_m - self.last_valid_depth) > self.z3d_max_jump:
                self.z3d_reject_count += 1
                if self.z3d_reject_count < 15:
                    depth_m = 0.0
            else:
                self.z3d_reject_count = 0
            # 第 2 层：重获校验（参照无效时 5 帧一致 + 背景深度拒绝）
            if depth_m > 0 and self.last_valid_depth == 0:
                if depth_m > self.desired_depth + 0.25:
                    depth_m = 0.0
                    self.reacq_buf.clear()
                else:
                    self.reacq_buf.append(depth_m)
                    if len(self.reacq_buf) > 5:
                        self.reacq_buf.pop(0)
                    if len(self.reacq_buf) == 5 and \
                            max(self.reacq_buf) - min(self.reacq_buf) <= self.z3d_max_jump:
                        depth_m = float(np.median(self.reacq_buf))
                    else:
                        depth_m = 0.0
            if depth_m > 0:
                # 第 3 层：深度限速
                if self.last_valid_depth > 0:
                    depth_m = float(np.clip(
                        depth_m,
                        self.last_valid_depth - self.z3d_max_rate,
                        self.last_valid_depth + self.z3d_max_rate))
                # 第 4 层：深度通道 One Euro
                depth_m = self.depth_oe(depth_m)
                self.last_valid_depth = depth_m
                self.last_valid_depth_time = time.time()
                track["x3d"], track["y3d"], track["z3d"] = pixel_to_3d(
                    track["u"], track["v"], depth_m,
                    self.fx, self.fy, self.cx, self.cy)
                track["z3d_frozen"] = False
            else:
                # 深度冻结：2D 新鲜但深度无效 → 冻结 z（占位 distance）
                if (self.last_valid_depth > 0 and
                        time.time() - self.last_valid_depth_time <= self.z_freeze_max):
                    track["x3d"], track["y3d"], _ = pixel_to_3d(
                        track["u"], track["v"],
                        self.last_valid_depth, self.fx, self.fy, self.cx, self.cy)
                    track["z3d"] = self.desired_depth
                    track["z3d_frozen"] = True
                    frozen = True
                else:
                    track["z3d"] = 0.0
                    track["z3d_frozen"] = False
        elif track is None or track["lost"] >= 30:
            self.last_valid_depth = 0.0
            self.z3d_reject_count = 0
            self.reacq_buf.clear()

        # ── 捏合 → 夹爪目标角 ──
        pinch_deg = 0.0
        pinch_valid = False
        pinch_px_now = None
        pinch_pts = None
        pinch_fresh = (track is not None and track["lost"] == 0
                       and not track.get("bridged", False))
        if self.gripper_enabled and landmarks is not None and pinch_fresh:
            pinch_px, p1, p2 = pinch_distance_px(landmarks, color_image.shape)
            pinch_px_now = pinch_px
            pinch_pts = (p1, p2)
            t_norm = float(np.interp(pinch_px,
                                     [self.pinch_closed_px, self.pinch_open_px],
                                     [0.0, 1.0]))
            target_deg = self.gripper_closed_deg + t_norm * (
                self.gripper_open_deg - self.gripper_closed_deg)
            if self.pinch_filter_type == "one_euro":
                self.smoothed_gripper_deg = self.pinch_oe(target_deg)
            else:
                self.smoothed_gripper_deg = (
                    self.pinch_smoothing * target_deg
                    + (1 - self.pinch_smoothing) * self.smoothed_gripper_deg)
            pinch_deg = self.smoothed_gripper_deg
            pinch_valid = True

        # ── 发布目标 ──
        msg = PalmTarget()
        msg.header.stamp = self.get_clock().now().to_msg()
        if track is not None and track["lost"] == 0 and track["z3d"] > 0:
            msg.position = [track["x3d"], track["y3d"], track["z3d"]]
            msg.visible = True
            msg.frozen = bool(track.get("z3d_frozen", False))
        else:
            msg.visible = False
        msg.bridged = bool(track.get("bridged", False)) if track else False
        msg.lost = int(track["lost"]) if track else 0
        msg.pinch_deg = float(pinch_deg)
        msg.pinch_valid = bool(pinch_valid)
        self.target_pub.publish(msg)

        # ── DBG（每 0.5s）──
        if time.time() - getattr(self, "_last_dbg", 0) > 0.5:
            self._last_dbg = time.time()
            det = "None"
            if track is not None:
                det = (f"u={track['u']:.0f} v={track['v']:.0f} "
                       f"lost={track['lost']} z3d={track['z3d']:.3f}"
                       f"{'❄冻结' if (track.get('z3d_frozen') and track['lost'] == 0) else ''}"
                       f"{'◦桥接' if track.get('bridged') else ''}")
            pinch_info = (f"pinch={pinch_px_now:.0f}px→{pinch_deg:.1f}°"
                          if pinch_px_now is not None else "pinch=None")
            st = self.servo_status
            err = st.get("error", "")
            if st.get("following") and not st.get("ffm", True):
                err = (f"{err}·静止" if err else "·静止")

            # 夹爪诊断：目标/正在下发的指令/实际角。三者不一致时可直接定位
            # vision 消息、适配层缓存、SDK 斜坡或 CAN/电机中的哪一环断了。
            def _g(v):
                return f"{float(v):.1f}" if isinstance(v, (int, float)) else "?"

            grip_err = st.get("gripper_actual_error", "")
            grip_info = (
                f"grip={_g(st.get('gripper_target'))}/"
                f"{_g(st.get('gripper_cmd'))}/{_g(st.get('gripper_actual'))}°"
                f"{'冻' if st.get('gripper_frozen') else ''}"
                f"{' rx✗' if not st.get('gripper_rx_valid', False) else ''}"
                f"{' ' + grip_err if grip_err else ''}")
            self.get_logger().info(
                f"[DBG] fps={self.fps_ema:4.1f}  palm=({det})  "
                f"following={st.get('following', False)}  "
                f"joint_speed={st.get('joint_speed', 0.0):.3f}  "
                f"{pinch_info}  {grip_info}  tcp={st.get('tcp')}  err={err}  "
                f"延迟ms(取帧/识别)={self.ms_grab:.0f}/{self.ms_det:.0f} "
                f"丢帧={getattr(self.cam, 'dropped_frames', 0)}")

        # ── 可视化 ──
        if not self.headless:
            display = color_image.copy()
            if landmarks is not None:
                draw_landmarks(display, landmarks)
            draw_palm(display, track, self.desired_u, self.desired_v)
            if pinch_pts is not None:
                cv2.line(display, pinch_pts[0], pinch_pts[1], (255, 0, 255), 3)
                cv2.circle(display, pinch_pts[0], 8, (255, 0, 255), cv2.FILLED)
                cv2.circle(display, pinch_pts[1], 8, (255, 0, 255), cv2.FILLED)
            if self.gripper_enabled:
                span = self.gripper_open_deg - self.gripper_closed_deg
                open_pct = (float(np.clip(
                    (self.smoothed_gripper_deg - self.gripper_closed_deg) / span,
                    0.0, 1.0)) * 100.0 if abs(span) > 1e-6 else 0.0)
                cv2.putText(display,
                            f"Gripper: {open_pct:.0f}% "
                            f"({self.smoothed_gripper_deg:.1f}deg)",
                            (10, 120), cv2.FONT_HERSHEY_SIMPLEX,
                            0.6, (255, 0, 255), 2)
            st = self.servo_status
            state = ("FOLLOWING" if st.get("active") else
                     ("HOLD (hand lost)" if st.get("following")
                      else "IDLE (press g/space)"))
            color_map = {"FOLLOWING": (0, 255, 0),
                         "IDLE (press g/space)": (0, 200, 255)}
            cv2.putText(display, state, (10, 460), cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, color_map.get(state, (0, 165, 255)), 2)
            cv2.putText(display,
                        f"FPS: {self.fps_ema:.0f}  JointSpeed: "
                        f"{st.get('joint_speed', 0.0):.3f} rad/s",
                        (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (255, 255, 0), 1)
            if st.get("error"):
                cv2.putText(display, f"CTRL: {st['error'][:60]}",
                            (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            (0, 0, 255), 1)
            cv2.imshow("Palm Follow + Grasp", display)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                self.quit_flag = True
            if key in (ord("g"), ord(" ")):
                self._toggle_tracking()

    def destroy_node(self):
        if getattr(self, "_destroyed", False):
            return
        self._destroyed = True
        try:
            self.detector.close()
        except Exception:
            pass
        try:
            self.cam.stop()
        except Exception:
            pass
        if not self.headless:
            try:
                cv2.destroyAllWindows()
                # OpenCV 经典坑：destroyAllWindows 只标记销毁，事件还压在
                # GUI 队列里；不泵 waitKey 会窗口假死、进程挂住
                for _ in range(5):
                    cv2.waitKey(1)
            except Exception:
                pass
        try:
            super().destroy_node()
        except Exception:
            pass


def main(args=None):
    rclpy.init(args=args)
    node = VisionNode()
    try:
        # 用 spin_once 轮询而不是 rclpy.spin：q 键触发的 rclpy.shutdown()
        # 发生在定时器回调内部，rclpy.spin 在同线程收到 shutdown 后
        # 不会自动返回（进程挂死、窗口冻结）；spin_once 循环在
        # rclpy.ok() 变 False 后立即退出，finally 正常走清理。
        while rclpy.ok():
            rclpy.spin_once(node, timeout_sec=0.1)
    except KeyboardInterrupt:
        pass
    finally:
        # 硬退出：清理链（detector.close / cam.stop / destroyAllWindows）
        # 在 MediaPipe 推理在飞或相机重连中途时可能挂死（SIGINT 后 5 秒
        # 被 launch SIGTERM 强杀就是实证）。视觉节点不持有机械臂，进程
        # 退出后相机/GPU 资源由 OS 回收，直接 os._exit 保证必退。
        import os as _os
        _os._exit(0)


if __name__ == "__main__":
    main()
