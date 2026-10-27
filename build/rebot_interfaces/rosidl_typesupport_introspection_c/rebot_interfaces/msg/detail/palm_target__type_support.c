// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from rebot_interfaces:msg/PalmTarget.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "rebot_interfaces/msg/detail/palm_target__rosidl_typesupport_introspection_c.h"
#include "rebot_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "rebot_interfaces/msg/detail/palm_target__functions.h"
#include "rebot_interfaces/msg/detail/palm_target__struct.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/header.h"
// Member `header`
#include "std_msgs/msg/detail/header__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void rebot_interfaces__msg__PalmTarget__rosidl_typesupport_introspection_c__PalmTarget_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  rebot_interfaces__msg__PalmTarget__init(message_memory);
}

void rebot_interfaces__msg__PalmTarget__rosidl_typesupport_introspection_c__PalmTarget_fini_function(void * message_memory)
{
  rebot_interfaces__msg__PalmTarget__fini(message_memory);
}

size_t rebot_interfaces__msg__PalmTarget__rosidl_typesupport_introspection_c__size_function__PalmTarget__position(
  const void * untyped_member)
{
  (void)untyped_member;
  return 3;
}

const void * rebot_interfaces__msg__PalmTarget__rosidl_typesupport_introspection_c__get_const_function__PalmTarget__position(
  const void * untyped_member, size_t index)
{
  const float * member =
    (const float *)(untyped_member);
  return &member[index];
}

void * rebot_interfaces__msg__PalmTarget__rosidl_typesupport_introspection_c__get_function__PalmTarget__position(
  void * untyped_member, size_t index)
{
  float * member =
    (float *)(untyped_member);
  return &member[index];
}

void rebot_interfaces__msg__PalmTarget__rosidl_typesupport_introspection_c__fetch_function__PalmTarget__position(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const float * item =
    ((const float *)
    rebot_interfaces__msg__PalmTarget__rosidl_typesupport_introspection_c__get_const_function__PalmTarget__position(untyped_member, index));
  float * value =
    (float *)(untyped_value);
  *value = *item;
}

void rebot_interfaces__msg__PalmTarget__rosidl_typesupport_introspection_c__assign_function__PalmTarget__position(
  void * untyped_member, size_t index, const void * untyped_value)
{
  float * item =
    ((float *)
    rebot_interfaces__msg__PalmTarget__rosidl_typesupport_introspection_c__get_function__PalmTarget__position(untyped_member, index));
  const float * value =
    (const float *)(untyped_value);
  *item = *value;
}

static rosidl_typesupport_introspection_c__MessageMember rebot_interfaces__msg__PalmTarget__rosidl_typesupport_introspection_c__PalmTarget_message_member_array[8] = {
  {
    "header",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rebot_interfaces__msg__PalmTarget, header),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "position",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    true,  // is array
    3,  // array size
    false,  // is upper bound
    offsetof(rebot_interfaces__msg__PalmTarget, position),  // bytes offset in struct
    NULL,  // default value
    rebot_interfaces__msg__PalmTarget__rosidl_typesupport_introspection_c__size_function__PalmTarget__position,  // size() function pointer
    rebot_interfaces__msg__PalmTarget__rosidl_typesupport_introspection_c__get_const_function__PalmTarget__position,  // get_const(index) function pointer
    rebot_interfaces__msg__PalmTarget__rosidl_typesupport_introspection_c__get_function__PalmTarget__position,  // get(index) function pointer
    rebot_interfaces__msg__PalmTarget__rosidl_typesupport_introspection_c__fetch_function__PalmTarget__position,  // fetch(index, &value) function pointer
    rebot_interfaces__msg__PalmTarget__rosidl_typesupport_introspection_c__assign_function__PalmTarget__position,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "visible",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rebot_interfaces__msg__PalmTarget, visible),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "frozen",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rebot_interfaces__msg__PalmTarget, frozen),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "bridged",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rebot_interfaces__msg__PalmTarget, bridged),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "lost",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_INT32,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rebot_interfaces__msg__PalmTarget, lost),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "pinch_deg",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rebot_interfaces__msg__PalmTarget, pinch_deg),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "pinch_valid",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rebot_interfaces__msg__PalmTarget, pinch_valid),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers rebot_interfaces__msg__PalmTarget__rosidl_typesupport_introspection_c__PalmTarget_message_members = {
  "rebot_interfaces__msg",  // message namespace
  "PalmTarget",  // message name
  8,  // number of fields
  sizeof(rebot_interfaces__msg__PalmTarget),
  rebot_interfaces__msg__PalmTarget__rosidl_typesupport_introspection_c__PalmTarget_message_member_array,  // message members
  rebot_interfaces__msg__PalmTarget__rosidl_typesupport_introspection_c__PalmTarget_init_function,  // function to initialize message memory (memory has to be allocated)
  rebot_interfaces__msg__PalmTarget__rosidl_typesupport_introspection_c__PalmTarget_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t rebot_interfaces__msg__PalmTarget__rosidl_typesupport_introspection_c__PalmTarget_message_type_support_handle = {
  0,
  &rebot_interfaces__msg__PalmTarget__rosidl_typesupport_introspection_c__PalmTarget_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_rebot_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, rebot_interfaces, msg, PalmTarget)() {
  rebot_interfaces__msg__PalmTarget__rosidl_typesupport_introspection_c__PalmTarget_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, std_msgs, msg, Header)();
  if (!rebot_interfaces__msg__PalmTarget__rosidl_typesupport_introspection_c__PalmTarget_message_type_support_handle.typesupport_identifier) {
    rebot_interfaces__msg__PalmTarget__rosidl_typesupport_introspection_c__PalmTarget_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &rebot_interfaces__msg__PalmTarget__rosidl_typesupport_introspection_c__PalmTarget_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
