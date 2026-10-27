# generated from rosidl_cmake/cmake/rosidl_cmake_aggregate_target-extras.cmake.in

# Create a convenience aggregate target rebot_interfaces::rebot_interfaces
# that links all generated interface targets, so downstream packages can use
# a single modern CMake target name instead of ${rebot_interfaces_TARGETS}.
if(rebot_interfaces_TARGETS AND NOT TARGET rebot_interfaces::rebot_interfaces)
  add_library(rebot_interfaces::rebot_interfaces INTERFACE IMPORTED)
  set_target_properties(rebot_interfaces::rebot_interfaces PROPERTIES
    INTERFACE_LINK_LIBRARIES "${rebot_interfaces_TARGETS}")
endif()
