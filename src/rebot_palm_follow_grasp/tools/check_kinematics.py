#!/usr/bin/env python3
"""无 CAN、无相机、无机械臂运动的 URDF 运动学自检。"""

import argparse
import json
import os
import sys

import numpy as np

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "rebot_palm_follow_grasp"))

from urdf_kinematics import URDFKinematics  # noqa: E402
from rebot_adapter import (URDF_PATH, B601_RS_JOINT_NAMES,  # noqa: E402
                           JOINT_OFFSET)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--urdf", default=URDF_PATH)
    args = parser.parse_args()
    kin = URDFKinematics(args.urdf, B601_RS_JOINT_NAMES)
    print(f"[OK] URDF 解析成功: {kin.n_dof} 自由度，末端 {kin.end_link}")
    print("[OK] 运行时为 NumPy 运动学，未加载 Pinocchio")

    home_file = os.path.join(_ROOT, "config", "home_pose.json")
    if os.path.exists(home_file):
        with open(home_file) as f:
            q_home = np.asarray(json.load(f)["home_joint_pos"], dtype=np.float64)
    else:
        q_home = np.array([0.0, 1.2, 1.05, 0.0, 0.0, 0.0])
    T = kin.fk(q_home + JOINT_OFFSET)
    print(f"[OK] HOME TCP 位置: {T[:3, 3].round(4).tolist()} m")

    rng = np.random.default_rng(7)
    worst = 0.0
    eps = 1e-7
    for _ in range(20):
        q = rng.uniform(kin.lower + 0.05, kin.upper - 0.05)
        p, _, J = kin.fk_and_jacobian(q)
        J_fd = np.zeros_like(J)
        for i in range(kin.n_dof):
            dq = np.zeros(kin.n_dof)
            dq[i] = eps
            pp, Rp, _ = kin.fk_and_jacobian(q + dq)
            pm, Rm, _ = kin.fk_and_jacobian(q - dq)
            J_fd[:3, i] = (pp - pm) / (2 * eps)
            dR = Rp @ Rm.T
            J_fd[3:, i] = np.array([
                dR[2, 1] - dR[1, 2], dR[0, 2] - dR[2, 0],
                dR[1, 0] - dR[0, 1]]) / (4 * eps)
        worst = max(worst, float(np.max(np.abs(J - J_fd))))
        assert np.all(np.isfinite(p)) and np.all(np.isfinite(J))
    print(f"[OK] 20 组雅可比有限差分检查，最大误差 {worst:.3e}")
    if worst > 2e-6:
        raise RuntimeError("雅可比数值检查失败")
    print("[PASS] 运动学自检通过；本测试未连接 CAN，未使能电机")


if __name__ == "__main__":
    main()
