// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from rebot_interfaces:msg/PalmTarget.idl
// generated code does not contain a copyright notice

#ifndef REBOT_INTERFACES__MSG__DETAIL__PALM_TARGET__STRUCT_H_
#define REBOT_INTERFACES__MSG__DETAIL__PALM_TARGET__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.h"

/// Struct defined in msg/PalmTarget in the package rebot_interfaces.
/**
  * Palm target + pinch state (vision_node -> servo_node)
 */
typedef struct rebot_interfaces__msg__PalmTarget
{
  std_msgs__msg__Header header;
  /// Palm 3D position in camera frame (m); invalid when visible=false
  float position[3];
  /// Frame valid = detected/bridged and depth passed the protection chain
  bool visible;
  /// Depth-frozen frame (z is placeholder; servo skips KF update)
  bool frozen;
  /// Optical-flow bridged frame (MediaPipe miss, LK fills in)
  bool bridged;
  /// Consecutive lost frames (detector's view)
  int32_t lost;
  /// Gripper target angle (degrees); invalid when pinch_valid=false
  double pinch_deg;
  bool pinch_valid;
} rebot_interfaces__msg__PalmTarget;

// Struct for a sequence of rebot_interfaces__msg__PalmTarget.
typedef struct rebot_interfaces__msg__PalmTarget__Sequence
{
  rebot_interfaces__msg__PalmTarget * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} rebot_interfaces__msg__PalmTarget__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // REBOT_INTERFACES__MSG__DETAIL__PALM_TARGET__STRUCT_H_
