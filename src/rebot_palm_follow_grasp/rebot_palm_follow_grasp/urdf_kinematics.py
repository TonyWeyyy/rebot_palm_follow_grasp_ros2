#!/usr/bin/env python3
"""轻量 URDF 串联运动学：只依赖 NumPy，不加载任何 C++ 运动学库。

B601-RS 的伺服只需要末关节 FK 和 LOCAL_WORLD_ALIGNED 雅可比。
直接解析 URDF 的 joint origin/axis/limit 即可，避免 ROS 与 cmeel 的
Pinocchio/eigenpy/urdfdom/Boost 动态库在同一进程中混载。

坐标约定与 Pinocchio 一致：
  T_child = T_parent * T_origin * Rotation(axis, q)
  Jv_i = axis_world_i × (p_tcp - p_joint_i)
  Jw_i = axis_world_i
角度单位为弧度，长度单位为米。
"""

import os
import xml.etree.ElementTree as ET

import numpy as np


def _floats(text, count, default):
    if text is None:
        return np.array(default, dtype=np.float64)
    values = np.fromstring(text, sep=" ", dtype=np.float64)
    if values.size != count or not np.all(np.isfinite(values)):
        raise ValueError(f"URDF 数值应为 {count} 个有限数，实际为: {text!r}")
    return values


def rpy_to_matrix(rpy):
    """URDF 固定角 roll-pitch-yaw：R = Rz(yaw) Ry(pitch) Rx(roll)。"""
    roll, pitch, yaw = np.asarray(rpy, dtype=np.float64)
    cr, sr = np.cos(roll), np.sin(roll)
    cp, sp = np.cos(pitch), np.sin(pitch)
    cy, sy = np.cos(yaw), np.sin(yaw)
    return np.array([
        [cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr],
        [sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr],
        [-sp, cp * sr, cp * cr],
    ], dtype=np.float64)


def axis_angle_to_matrix(axis, angle):
    """Rodrigues 旋转公式；axis 必须已归一化。"""
    x, y, z = np.asarray(axis, dtype=np.float64)
    K = np.array([[0.0, -z, y], [z, 0.0, -x], [-y, x, 0.0]])
    return (np.eye(3) + np.sin(angle) * K
            + (1.0 - np.cos(angle)) * (K @ K))


def transform(rotation, translation):
    T = np.eye(4)
    T[:3, :3] = rotation
    T[:3, 3] = translation
    return T


class URDFKinematics:
    """按给定关节顺序解析一条串联 revolute/continuous 链。"""

    def __init__(self, urdf_path, joint_names):
        self.urdf_path = os.path.abspath(os.path.expanduser(urdf_path))
        self.joint_names = list(joint_names)
        if not self.joint_names:
            raise ValueError("joint_names 不能为空")
        if not os.path.isfile(self.urdf_path):
            raise FileNotFoundError(f"URDF 不存在: {self.urdf_path}")

        root = ET.parse(self.urdf_path).getroot()
        xml_joints = {j.get("name"): j for j in root.findall("joint")}
        if len(xml_joints) != len(root.findall("joint")):
            raise ValueError("URDF 存在重名 joint")

        self._origins = []
        self._axes = []
        lower, upper = [], []
        parent_link = None

        for name in self.joint_names:
            joint = xml_joints.get(name)
            if joint is None:
                raise ValueError(f"URDF 中找不到关节 {name!r}")
            if joint.get("type") not in ("revolute", "continuous"):
                raise ValueError(
                    f"关节 {name!r} 类型为 {joint.get('type')!r}，"
                    "本伺服链只支持 revolute/continuous")
            parent = joint.find("parent")
            child = joint.find("child")
            if parent is None or child is None:
                raise ValueError(f"关节 {name!r} 缺少 parent/child link")
            if parent_link is not None and parent.get("link") != parent_link:
                raise ValueError(
                    f"关节 {name!r} 的 parent={parent.get('link')!r}，"
                    f"与上一关节 child={parent_link!r} 不连续")

            origin = joint.find("origin")
            xyz = _floats(None if origin is None else origin.get("xyz"),
                          3, (0.0, 0.0, 0.0))
            rpy = _floats(None if origin is None else origin.get("rpy"),
                          3, (0.0, 0.0, 0.0))
            self._origins.append(transform(rpy_to_matrix(rpy), xyz))

            axis_el = joint.find("axis")
            axis = _floats(None if axis_el is None else axis_el.get("xyz"),
                           3, (1.0, 0.0, 0.0))
            norm = float(np.linalg.norm(axis))
            if norm < 1e-12:
                raise ValueError(f"关节 {name!r} 的 axis 为零向量")
            self._axes.append(axis / norm)

            limit = joint.find("limit")
            if joint.get("type") == "continuous":
                lower.append(-np.inf)
                upper.append(np.inf)
            elif limit is None:
                raise ValueError(f"revolute 关节 {name!r} 缺少 limit")
            else:
                lo, hi = float(limit.get("lower")), float(limit.get("upper"))
                if not np.isfinite([lo, hi]).all() or lo >= hi:
                    raise ValueError(f"关节 {name!r} 的 limit 非法: {lo}, {hi}")
                lower.append(lo)
                upper.append(hi)
            parent_link = child.get("link")

        self._origins = np.asarray(self._origins)
        self._axes = np.asarray(self._axes)
        self.lower = np.asarray(lower)
        self.upper = np.asarray(upper)
        self.n_dof = len(self.joint_names)
        self.end_link = parent_link

    def _validate_q(self, joint_positions):
        q = np.asarray(joint_positions, dtype=np.float64)
        if q.shape != (self.n_dof,) or not np.all(np.isfinite(q)):
            raise ValueError(f"关节角必须是 {self.n_dof} 维有限向量")
        return q

    def fk(self, joint_positions):
        """返回末关节坐标系相对基座的 4×4 齐次变换。"""
        q = self._validate_q(joint_positions)
        T = np.eye(4)
        for origin, axis, angle in zip(self._origins, self._axes, q):
            T = T @ origin
            T = T @ transform(axis_angle_to_matrix(axis, angle),
                              (0.0, 0.0, 0.0))
        return T

    def fk_and_jacobian(self, joint_positions, tool_offset=None):
        """返回 (TCP位置, 末关节旋转, 世界系对齐的 6×N 雅可比)。"""
        q = self._validate_q(joint_positions)
        if tool_offset is None:
            tool_offset = np.zeros(3)
        tool_offset = np.asarray(tool_offset, dtype=np.float64)
        if tool_offset.shape != (3,) or not np.all(np.isfinite(tool_offset)):
            raise ValueError("tool_offset 必须是 3 维有限向量")

        T = np.eye(4)
        joint_positions_world = []
        joint_axes_world = []
        for origin, axis, angle in zip(self._origins, self._axes, q):
            T = T @ origin
            joint_positions_world.append(T[:3, 3].copy())
            joint_axes_world.append(T[:3, :3] @ axis)
            T = T @ transform(axis_angle_to_matrix(axis, angle),
                              (0.0, 0.0, 0.0))

        rotation = T[:3, :3].copy()
        tcp_position = T[:3, 3] + rotation @ tool_offset
        J = np.zeros((6, self.n_dof))
        for i, (p_joint, axis_world) in enumerate(
                zip(joint_positions_world, joint_axes_world)):
            J[:3, i] = np.cross(axis_world, tcp_position - p_joint)
            J[3:, i] = axis_world
        return tcp_position.copy(), rotation, J
