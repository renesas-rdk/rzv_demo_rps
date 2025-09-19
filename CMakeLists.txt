cmake_minimum_required(VERSION 3.8)
project(rzv_demo_rps)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()


# Find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_action REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(yaml-cpp REQUIRED)
find_package(ament_index_cpp REQUIRED)
find_package(arm_hand_control REQUIRED)

# Include directories
include_directories(include)

# Executables
# RPS game controller
add_executable(rps_controller src/rps_controller.cpp)
ament_target_dependencies(rps_controller
  rclcpp
  rclcpp_action
  sensor_msgs
  std_msgs
  arm_hand_control
  ament_index_cpp
)
target_link_libraries(rps_controller
  "${cpp_typesupport_target}"
)

# Installation
install(TARGETS
  rps_controller
  DESTINATION lib/${PROJECT_NAME}
)

# Install launch files
install(DIRECTORY
  launch
  DESTINATION share/${PROJECT_NAME}/
)

# Install config files
install(DIRECTORY
  config
  DESTINATION share/${PROJECT_NAME}/
)

ament_package()
