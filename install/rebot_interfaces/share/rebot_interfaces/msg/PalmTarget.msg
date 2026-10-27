# Palm target + pinch state (vision_node -> servo_node)
std_msgs/Header header
# Palm 3D position in camera frame (m); invalid when visible=false
float32[3] position
# Frame valid = detected/bridged and depth passed the protection chain
bool visible
# Depth-frozen frame (z is placeholder; servo skips KF update)
bool frozen
# Optical-flow bridged frame (MediaPipe miss, LK fills in)
bool bridged
# Consecutive lost frames (detector's view)
int32 lost
# Gripper target angle (degrees); invalid when pinch_valid=false
float64 pinch_deg
bool pinch_valid
