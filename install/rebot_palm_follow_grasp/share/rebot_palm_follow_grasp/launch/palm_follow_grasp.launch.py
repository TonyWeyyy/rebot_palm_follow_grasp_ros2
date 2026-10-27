"""一键启动：vision_node + servo_node

用法：
  ros2 launch rebot_palm_follow_grasp palm_follow_grasp.launch.py
  ros2 launch rebot_palm_follow_grasp palm_follow_grasp.launch.py enable_servo:=false  # 纯视觉演练
  ros2 launch rebot_palm_follow_grasp palm_follow_grasp.launch.py headless:=true       # 无窗口（SSH）

参数文件默认取安装后的 share/rebot_palm_follow_grasp/config/params.yaml，
可用 params_file:=<路径> 换成工作区里的版本直接改参调试。
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable, Shutdown
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    share = get_package_share_directory("rebot_palm_follow_grasp")
    config_dir = os.path.join(share, "config")
    default_params = os.path.join(config_dir, "params.yaml")

    params_file = LaunchConfiguration("params_file")
    enable_servo = LaunchConfiguration("enable_servo")
    headless = LaunchConfiguration("headless")

    return LaunchDescription([
        DeclareLaunchArgument("params_file", default_value=default_params,
                              description="参数文件路径"),
        DeclareLaunchArgument("enable_servo", default_value="true",
                              description="false = 纯视觉演练（不碰机械臂）"),
        DeclareLaunchArgument("headless", default_value="false",
                              description="true = 不开视觉窗口"),
        # 库模块（模型/标定/零位修正）从 share/config 解析数据文件
        SetEnvironmentVariable("REBOT_PFG_CONFIG_DIR", config_dir),

        Node(package="rebot_palm_follow_grasp",
             executable="vision_node",
             name="vision_node",
             output="screen",
             # q 退出视觉节点时联动结束 launch，servo 收到 SIGINT 后走安全回零。
             on_exit=Shutdown(reason="vision_node 已退出"),
             parameters=[params_file, {"headless": headless}]),

        Node(package="rebot_palm_follow_grasp",
             executable="servo_node",
             name="servo_node",
             output="screen",
             condition=IfCondition(enable_servo),
             # servo 异常退出也不能留下“看似仍在运行”的纯视觉窗口。
             on_exit=Shutdown(reason="servo_node 已退出"),
             parameters=[params_file]),
    ])
