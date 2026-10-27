#!/usr/bin/env python3
"""视觉伺服纯数学函数（与原 palm_follow_grasp.py 完全一致，无状态）。"""

import numpy as np

TOOL_OFFSET = np.array([0.0, 0.0, 0.0])   # TCP 相对末关节的偏移（米）


def compute_damped_pseudoinverse(J, damping=0.01):
    m, n = J.shape
    JJT = J @ J.T
    damping_matrix = (damping ** 2) * np.eye(m)
    try:
        return J.T @ np.linalg.inv(JJT + damping_matrix)
    except np.linalg.LinAlgError:
        return J.T @ np.linalg.inv(JJT + ((damping * 10) ** 2) * np.eye(m))


def compute_manipulability(J):
    return np.sqrt(max(0.0, np.linalg.det(J @ J.T)))


def rotation_matrix_to_axis_angle(R):
    theta = np.arccos(np.clip((np.trace(R) - 1) / 2, -1.0, 1.0))
    if abs(theta) < 1e-6:
        return np.zeros(3)
    if abs(np.pi - theta) < 1e-3:
        S = (R + np.eye(3)) / 2.0
        axis = np.array([np.sqrt(max(S[0, 0], 0.0)),
                         np.sqrt(max(S[1, 1], 0.0)),
                         np.sqrt(max(S[2, 2], 0.0))])
        axis[1] = np.copysign(axis[1], R[0, 1] + R[1, 0])
        axis[2] = np.copysign(axis[2], R[0, 2] + R[2, 0])
        n = np.linalg.norm(axis)
        if n < 1e-9:
            return np.zeros(3)
        return theta * axis / n
    k = 1 / (2 * np.sin(theta)) * np.array([
        R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]])
    return theta * k


def compute_orientation_error(R_current, R_desired):
    return rotation_matrix_to_axis_angle(R_desired @ R_current.T)


def skew(v):
    return np.array([[0.0, -v[2], v[1]],
                     [v[2], 0.0, -v[0]],
                     [-v[1], v[0], 0.0]])


def compute_tcp_fk_and_jacobian(robot, joint_positions):
    """返回 TCP 位姿和 LOCAL_WORLD_ALIGNED TCP 雅可比（6x6）。

    运动学实现位于 URDFKinematics，纯 NumPy；坐标和雅可比定义与原先
    Pinocchio LOCAL_WORLD_ALIGNED 完全一致。
    """
    q = robot._build_q_full(joint_positions)
    return robot.kinematics.fk_and_jacobian(q, TOOL_OFFSET)


def camera_velocity_to_tcp(v_camera, T_tcp_camera):
    """相机系速度 → TCP 系速度（速度伴随变换）"""
    R_tcp_cam = T_tcp_camera[:3, :3]
    t_tcp_cam = T_tcp_camera[:3, 3]
    V = np.zeros((6, 6))
    V[:3, :3] = R_tcp_cam
    V[:3, 3:] = skew(t_tcp_cam) @ R_tcp_cam
    V[3:, 3:] = R_tcp_cam
    return V @ v_camera
