# *********************************************************************************************************************
#  Copyright (C) 2026 Renesas Electronics Corporation and/or its licensors.
#  SPDX-License-Identifier: AGPL-3.0-only
# *********************************************************************************************************************

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import (
    IncludeLaunchDescription,
    DeclareLaunchArgument,
    OpaqueFunction,
    SetEnvironmentVariable,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def launch_setup(context, *args, **kwargs):
    """
    Launch camera-based hand tracking with virtual hand control.

    Pipeline:
    camera →object detection  → rps game controller → ros2_control prosition controller → joint_state_broadcaster → urdf visualization

    Topic flow:
    - Camera: publishes /image_raw
    - Object detection: subscribes to /image_raw
      publishes /object_detection/bounding_box, /object_detection/rps_hand_detect
    - Visualization: subscribes to /object_detection/bounding_box and publishes visualization markers
    - RPS Game Controller: subscribes to /object_detection/rps_hand_detect
      sends action goal to: /execute_gesture/goal
    - Hand gesture interpreter: subscribes to /hand_landmark_estimation/hand_landmarks
      publishes /ruiyan_rh2_hand_joint_position_controller/commands (alternative, mutually exclusive)
    - ros2_control position controller: subscribes to /ruiyan_rh2_hand_joint_position_controller/commands
    - joint_state_broadcaster: publishes /joint_states
    - URDF publishers: subscribe to /joint_states for hand visualization (from ros2_control)

    """
    # Create LaunchConfiguration objects for customizable parameters
    use_mock_hardware_value = LaunchConfiguration("use_mock_hardware").perform(context)
    hand_side_value = LaunchConfiguration("hand_side").perform(context)
    can_interface_value = LaunchConfiguration("can_interface").perform(context)
    hand_speed_value = LaunchConfiguration("hand_speed").perform(context)
    video_device = LaunchConfiguration("video_device")

    # Define package directories
    foxglove_keypoint_pkg_dir = get_package_share_directory(
        "foxglove_keypoint_publisher"
    )
    rzv_demo_rps_dir = get_package_share_directory("rzv_demo_rps")

    # Shared hand config path used by both interpreter nodes
    hand_config_path = os.path.join(rzv_demo_rps_dir, "config/hand/ruiyan_rh2.yaml")

    # Accumulate all nodes/nodes to return
    nodes = []

    # Set TVM_NUM_THREADS environment variable for hand landmark estimation performance
    set_tvm_threads = SetEnvironmentVariable("TVM_NUM_THREADS", "2")
    nodes.append(set_tvm_threads)

    # 1. Robot bringup launch file
    ruiyan_rh2_hand_bringup_pkg = get_package_share_directory("ruiyan_rh2_hand_bringup")
    ruiyan_rh2_hand_bringup_launch_file = (
        "ruiyan_rh2_hand_joint_position_control.launch.py"
    )

    robot_bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                ruiyan_rh2_hand_bringup_pkg,
                "launch",
                ruiyan_rh2_hand_bringup_launch_file,
            )
        ),
        launch_arguments={
            "hand_side": hand_side_value,
            "use_mock_hardware": use_mock_hardware_value,
            "can_interface": can_interface_value,
            "hand_speed": hand_speed_value,
        }.items(),
    )
    nodes.append(robot_bringup_launch)

    # 2. Camera node
    # PUBLISHES: /image_raw
    camera_node = Node(
        package="v4l2_camera",
        executable="v4l2_camera_node",
        name="v4l2_camera",
        parameters=[
            {
                "video_device": video_device,
                "output_encoding": "yuv422_yuy2",
                "image_size": [640, 480],
            }
        ],
    )
    nodes.append(camera_node)

    # 3. Object detection node
    # SUBSCRIBES: /image_raw
    # PUBLISHES: /object_detection/bounding_box, /object_detection/rps_hand_detect
    object_detection_node = Node(
        package="rzv_object_detection",
        executable="yolov8_object_detection",
        name="object_detection",
        parameters=[
            {
                "model_type": "yolov8_rps",
                "processing_queue_size": 1,
                "confidence_threshold": 0.8,
                "iou_threshold": 0.3,
            }
        ],
        remappings=[
            ("/image_raw", "/image_raw"),
            ("/bounding_box", "/object_detection/bounding_box"),
            ("/object_detect", "/object_detection/rps_hand_detect"),
        ],
        output="screen",
        arguments=["--ros-args", "--log-level", "INFO"],
    )
    nodes.append(object_detection_node)

    # 4. Visualization nodes for Foxglove Studio
    # SUBSCRIBES: /object_detection/bounding_box
    # PUBLISHES: bbox_visualization
    bbox_config_path = os.path.join(
        foxglove_keypoint_pkg_dir, "config/poses/bounding_box.yaml"
    )
    foxglove_hand_bbox_publisher_node = Node(
        package="foxglove_keypoint_publisher",
        executable="foxglove_keypoint_publisher_node",
        name="foxglove_hand_bbox_publisher",
        parameters=[{"config_file": bbox_config_path}],
        remappings=[
            ("/keypoint_poses", "/object_detection/bounding_box"),
            ("/keypoint_visualization", "/bbox_visualization"),
        ],
        output="screen",
    )
    nodes.append(foxglove_hand_bbox_publisher_node)

    # 5. Interpreter for controlling hands

    # 5.1 Rock-Paper-Scissors game controller
    # SUBSCRIBES TO: /object_detection/rps_hand_detect
    # ACTION CLIENT: /execute_gesture/goal
    rps_controller_node = Node(
        package="rzv_demo_rps",
        executable="rps_controller",
        name="rps_controller",
        output="screen",
        remappings=[("/hand_pose", "/object_detection/rps_hand_detect")],
    )
    nodes.append(rps_controller_node)

    # 4.2 Hand gesture interpreter
    # ACTION SERVER: /execute_gesture/goal
    # PUBLISHES:  /ruiyan_rh2_hand_joint_position_controller/commands
    hand_gesture_interpreter_node = Node(
        package="arm_hand_control",
        executable="hand_gesture_interpreter",
        name="hand_gesture_interpreter",
        output="screen",
        parameters=[
            {
                "config_file": hand_config_path,
                "auto_demo_enabled": False,
                "gesture_duration": 1.0,
                "transition_duration": 0.5,
            }
        ],
        remappings=[
            (
                "/position_controller_command",
                "/ruiyan_rh2_hand_joint_position_controller/commands",
            ),
        ],
    )
    nodes.append(hand_gesture_interpreter_node)

    return nodes


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "use_mock_hardware",
                default_value="false",
                description="Use mock hardware for testing (true/false)",
            ),
            DeclareLaunchArgument(
                "hand_side",
                default_value="left",
                description="Which hand to control: left or right",
            ),
            DeclareLaunchArgument(
                "can_interface",
                default_value="can2",
                description="CAN interface for hand hardware communication (e.g., can0, can1, can2)",
            ),
            DeclareLaunchArgument(
                "hand_speed", default_value="1500", description="Hand motor speed"
            ),
            DeclareLaunchArgument(
                "video_device",
                default_value="/dev/video0",
                description="Video device path for camera input",
            ),
            OpaqueFunction(function=launch_setup),
        ]
    )
