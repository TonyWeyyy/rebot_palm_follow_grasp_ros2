// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from rebot_interfaces:msg/PalmTarget.idl
// generated code does not contain a copyright notice

#ifndef REBOT_INTERFACES__MSG__DETAIL__PALM_TARGET__STRUCT_HPP_
#define REBOT_INTERFACES__MSG__DETAIL__PALM_TARGET__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__rebot_interfaces__msg__PalmTarget __attribute__((deprecated))
#else
# define DEPRECATED__rebot_interfaces__msg__PalmTarget __declspec(deprecated)
#endif

namespace rebot_interfaces
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct PalmTarget_
{
  using Type = PalmTarget_<ContainerAllocator>;

  explicit PalmTarget_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      std::fill<typename std::array<float, 3>::iterator, float>(this->position.begin(), this->position.end(), 0.0f);
      this->visible = false;
      this->frozen = false;
      this->bridged = false;
      this->lost = 0l;
      this->pinch_deg = 0.0;
      this->pinch_valid = false;
    }
  }

  explicit PalmTarget_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_alloc, _init),
    position(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      std::fill<typename std::array<float, 3>::iterator, float>(this->position.begin(), this->position.end(), 0.0f);
      this->visible = false;
      this->frozen = false;
      this->bridged = false;
      this->lost = 0l;
      this->pinch_deg = 0.0;
      this->pinch_valid = false;
    }
  }

  // field types and members
  using _header_type =
    std_msgs::msg::Header_<ContainerAllocator>;
  _header_type header;
  using _position_type =
    std::array<float, 3>;
  _position_type position;
  using _visible_type =
    bool;
  _visible_type visible;
  using _frozen_type =
    bool;
  _frozen_type frozen;
  using _bridged_type =
    bool;
  _bridged_type bridged;
  using _lost_type =
    int32_t;
  _lost_type lost;
  using _pinch_deg_type =
    double;
  _pinch_deg_type pinch_deg;
  using _pinch_valid_type =
    bool;
  _pinch_valid_type pinch_valid;

  // setters for named parameter idiom
  Type & set__header(
    const std_msgs::msg::Header_<ContainerAllocator> & _arg)
  {
    this->header = _arg;
    return *this;
  }
  Type & set__position(
    const std::array<float, 3> & _arg)
  {
    this->position = _arg;
    return *this;
  }
  Type & set__visible(
    const bool & _arg)
  {
    this->visible = _arg;
    return *this;
  }
  Type & set__frozen(
    const bool & _arg)
  {
    this->frozen = _arg;
    return *this;
  }
  Type & set__bridged(
    const bool & _arg)
  {
    this->bridged = _arg;
    return *this;
  }
  Type & set__lost(
    const int32_t & _arg)
  {
    this->lost = _arg;
    return *this;
  }
  Type & set__pinch_deg(
    const double & _arg)
  {
    this->pinch_deg = _arg;
    return *this;
  }
  Type & set__pinch_valid(
    const bool & _arg)
  {
    this->pinch_valid = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    rebot_interfaces::msg::PalmTarget_<ContainerAllocator> *;
  using ConstRawPtr =
    const rebot_interfaces::msg::PalmTarget_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<rebot_interfaces::msg::PalmTarget_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<rebot_interfaces::msg::PalmTarget_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      rebot_interfaces::msg::PalmTarget_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<rebot_interfaces::msg::PalmTarget_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      rebot_interfaces::msg::PalmTarget_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<rebot_interfaces::msg::PalmTarget_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<rebot_interfaces::msg::PalmTarget_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<rebot_interfaces::msg::PalmTarget_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__rebot_interfaces__msg__PalmTarget
    std::shared_ptr<rebot_interfaces::msg::PalmTarget_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__rebot_interfaces__msg__PalmTarget
    std::shared_ptr<rebot_interfaces::msg::PalmTarget_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const PalmTarget_ & other) const
  {
    if (this->header != other.header) {
      return false;
    }
    if (this->position != other.position) {
      return false;
    }
    if (this->visible != other.visible) {
      return false;
    }
    if (this->frozen != other.frozen) {
      return false;
    }
    if (this->bridged != other.bridged) {
      return false;
    }
    if (this->lost != other.lost) {
      return false;
    }
    if (this->pinch_deg != other.pinch_deg) {
      return false;
    }
    if (this->pinch_valid != other.pinch_valid) {
      return false;
    }
    return true;
  }
  bool operator!=(const PalmTarget_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct PalmTarget_

// alias to use template instance with default allocator
using PalmTarget =
  rebot_interfaces::msg::PalmTarget_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace rebot_interfaces

#endif  // REBOT_INTERFACES__MSG__DETAIL__PALM_TARGET__STRUCT_HPP_
