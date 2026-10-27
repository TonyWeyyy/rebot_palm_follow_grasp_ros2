import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/tony/wey/rebot_developer/rebot_CV_control/rebot_palm_follow_grasp_ros2/install/rebot_palm_follow_grasp'
