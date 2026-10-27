// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from rebot_interfaces:msg/PalmTarget.idl
// generated code does not contain a copyright notice

#ifndef REBOT_INTERFACES__MSG__DETAIL__PALM_TARGET__TRAITS_HPP_
#define REBOT_INTERFACES__MSG__DETAIL__PALM_TARGET__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "rebot_interfaces/msg/detail/palm_target__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__traits.hpp"

namespace rebot_interfaces
{

namespace msg
{

inline void to_flow_style_yaml(
  const PalmTarget & msg,
  std::ostream & out)
{
  out << "{";
  // member: header
  {
    out << "header: ";
    to_flow_style_yaml(msg.header, out);
    out << ", ";
  }

  // member: position
  {
    if (msg.position.size() == 0) {
      out << "position: []";
    } else {
      out << "position: [";
      size_t pending_items = msg.position.size();
      for (auto item : msg.position) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: visible
  {
    out << "visible: ";
    rosidl_generator_traits::value_to_yaml(msg.visible, out);
    out << ", ";
  }

  // member: frozen
  {
    out << "frozen: ";
    rosidl_generator_traits::value_to_yaml(msg.frozen, out);
    out << ", ";
  }

  // member: bridged
  {
    out << "bridged: ";
    rosidl_generator_traits::value_to_yaml(msg.bridged, out);
    out << ", ";
  }

  // member: lost
  {
    out << "lost: ";
    rosidl_generator_traits::value_to_yaml(msg.lost, out);
    out << ", ";
  }

  // member: pinch_deg
  {
    out << "pinch_deg: ";
    rosidl_generator_traits::value_to_yaml(msg.pinch_deg, out);
    out << ", ";
  }

  // member: pinch_valid
  {
    out << "pinch_valid: ";
    rosidl_generator_traits::value_to_yaml(msg.pinch_valid, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const PalmTarget & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: header
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "header:\n";
    to_block_style_yaml(msg.header, out, indentation + 2);
  }

  // member: position
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.position.size() == 0) {
      out << "position: []\n";
    } else {
      out << "position:\n";
      for (auto item : msg.position) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: visible
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "visible: ";
    rosidl_generator_traits::value_to_yaml(msg.visible, out);
    out << "\n";
  }

  // member: frozen
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "frozen: ";
    rosidl_generator_traits::value_to_yaml(msg.frozen, out);
    out << "\n";
  }

  // member: bridged
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "bridged: ";
    rosidl_generator_traits::value_to_yaml(msg.bridged, out);
    out << "\n";
  }

  // member: lost
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "lost: ";
    rosidl_generator_traits::value_to_yaml(msg.lost, out);
    out << "\n";
  }

  // member: pinch_deg
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "pinch_deg: ";
    rosidl_generator_traits::value_to_yaml(msg.pinch_deg, out);
    out << "\n";
  }

  // member: pinch_valid
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "pinch_valid: ";
    rosidl_generator_traits::value_to_yaml(msg.pinch_valid, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const PalmTarget & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace msg

}  // namespace rebot_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use rebot_interfaces::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const rebot_interfaces::msg::PalmTarget & msg,
  std::ostream & out, size_t indentation = 0)
{
  rebot_interfaces::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use rebot_interfaces::msg::to_yaml() instead")]]
inline std::string to_yaml(const rebot_interfaces::msg::PalmTarget & msg)
{
  return rebot_interfaces::msg::to_yaml(msg);
}

template<>
inline const char * data_type<rebot_interfaces::msg::PalmTarget>()
{
  return "rebot_interfaces::msg::PalmTarget";
}

template<>
inline const char * name<rebot_interfaces::msg::PalmTarget>()
{
  return "rebot_interfaces/msg/PalmTarget";
}

template<>
struct has_fixed_size<rebot_interfaces::msg::PalmTarget>
  : std::integral_constant<bool, has_fixed_size<std_msgs::msg::Header>::value> {};

template<>
struct has_bounded_size<rebot_interfaces::msg::PalmTarget>
  : std::integral_constant<bool, has_bounded_size<std_msgs::msg::Header>::value> {};

template<>
struct is_message<rebot_interfaces::msg::PalmTarget>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // REBOT_INTERFACES__MSG__DETAIL__PALM_TARGET__TRAITS_HPP_
