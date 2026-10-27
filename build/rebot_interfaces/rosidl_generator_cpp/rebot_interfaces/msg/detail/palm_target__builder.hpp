// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from rebot_interfaces:msg/PalmTarget.idl
// generated code does not contain a copyright notice

#ifndef REBOT_INTERFACES__MSG__DETAIL__PALM_TARGET__BUILDER_HPP_
#define REBOT_INTERFACES__MSG__DETAIL__PALM_TARGET__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "rebot_interfaces/msg/detail/palm_target__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace rebot_interfaces
{

namespace msg
{

namespace builder
{

class Init_PalmTarget_pinch_valid
{
public:
  explicit Init_PalmTarget_pinch_valid(::rebot_interfaces::msg::PalmTarget & msg)
  : msg_(msg)
  {}
  ::rebot_interfaces::msg::PalmTarget pinch_valid(::rebot_interfaces::msg::PalmTarget::_pinch_valid_type arg)
  {
    msg_.pinch_valid = std::move(arg);
    return std::move(msg_);
  }

private:
  ::rebot_interfaces::msg::PalmTarget msg_;
};

class Init_PalmTarget_pinch_deg
{
public:
  explicit Init_PalmTarget_pinch_deg(::rebot_interfaces::msg::PalmTarget & msg)
  : msg_(msg)
  {}
  Init_PalmTarget_pinch_valid pinch_deg(::rebot_interfaces::msg::PalmTarget::_pinch_deg_type arg)
  {
    msg_.pinch_deg = std::move(arg);
    return Init_PalmTarget_pinch_valid(msg_);
  }

private:
  ::rebot_interfaces::msg::PalmTarget msg_;
};

class Init_PalmTarget_lost
{
public:
  explicit Init_PalmTarget_lost(::rebot_interfaces::msg::PalmTarget & msg)
  : msg_(msg)
  {}
  Init_PalmTarget_pinch_deg lost(::rebot_interfaces::msg::PalmTarget::_lost_type arg)
  {
    msg_.lost = std::move(arg);
    return Init_PalmTarget_pinch_deg(msg_);
  }

private:
  ::rebot_interfaces::msg::PalmTarget msg_;
};

class Init_PalmTarget_bridged
{
public:
  explicit Init_PalmTarget_bridged(::rebot_interfaces::msg::PalmTarget & msg)
  : msg_(msg)
  {}
  Init_PalmTarget_lost bridged(::rebot_interfaces::msg::PalmTarget::_bridged_type arg)
  {
    msg_.bridged = std::move(arg);
    return Init_PalmTarget_lost(msg_);
  }

private:
  ::rebot_interfaces::msg::PalmTarget msg_;
};

class Init_PalmTarget_frozen
{
public:
  explicit Init_PalmTarget_frozen(::rebot_interfaces::msg::PalmTarget & msg)
  : msg_(msg)
  {}
  Init_PalmTarget_bridged frozen(::rebot_interfaces::msg::PalmTarget::_frozen_type arg)
  {
    msg_.frozen = std::move(arg);
    return Init_PalmTarget_bridged(msg_);
  }

private:
  ::rebot_interfaces::msg::PalmTarget msg_;
};

class Init_PalmTarget_visible
{
public:
  explicit Init_PalmTarget_visible(::rebot_interfaces::msg::PalmTarget & msg)
  : msg_(msg)
  {}
  Init_PalmTarget_frozen visible(::rebot_interfaces::msg::PalmTarget::_visible_type arg)
  {
    msg_.visible = std::move(arg);
    return Init_PalmTarget_frozen(msg_);
  }

private:
  ::rebot_interfaces::msg::PalmTarget msg_;
};

class Init_PalmTarget_position
{
public:
  explicit Init_PalmTarget_position(::rebot_interfaces::msg::PalmTarget & msg)
  : msg_(msg)
  {}
  Init_PalmTarget_visible position(::rebot_interfaces::msg::PalmTarget::_position_type arg)
  {
    msg_.position = std::move(arg);
    return Init_PalmTarget_visible(msg_);
  }

private:
  ::rebot_interfaces::msg::PalmTarget msg_;
};

class Init_PalmTarget_header
{
public:
  Init_PalmTarget_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_PalmTarget_position header(::rebot_interfaces::msg::PalmTarget::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_PalmTarget_position(msg_);
  }

private:
  ::rebot_interfaces::msg::PalmTarget msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::rebot_interfaces::msg::PalmTarget>()
{
  return rebot_interfaces::msg::builder::Init_PalmTarget_header();
}

}  // namespace rebot_interfaces

#endif  // REBOT_INTERFACES__MSG__DETAIL__PALM_TARGET__BUILDER_HPP_
