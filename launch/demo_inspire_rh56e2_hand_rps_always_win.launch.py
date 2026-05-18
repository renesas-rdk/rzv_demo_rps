# *********************************************************************************************************************
#  Copyright (C) 2026 Renesas Electronics Corporation and/or its licensors.
#  SPDX-License-Identifier: AGPL-3.0-only
# *********************************************************************************************************************

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    OpaqueFunction,
    SetEnvironmentVariable,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def launch_setup(context, *args, **kwargs):
    """
    Launch low-latency always-win RPS mode with Inspire RH56E2 hand control.

    Pipeline:
    camera -> object detection -> rps controller(always-win) -> hand gesture interpreter
      -> ros2_control position controller -> joint_state_broadcaster -> urdf visualization

    Response mapping:
    - User paper -> robot scissor
    - User rock -> robot paper
    - User scissor -> robot rock

    Detector selection (via 'detector' argument):
    - yolov8 (default): executable=yolov8_object_detection, model_type=yolov8_rps
    - yolox:            executable=yolox_rps_detection,     model_type=yolox_s_rps
    """
    use_mock_hardware_value = LaunchConfiguration("use_mock_hardware").perform(context)
    hand_side_value = LaunchConfiguration("hand_side").perform(context)
    serial_port_value = LaunchConfiguration("serial_port").perform(context)
    hand_speed_value = LaunchConfiguration("hand_speed").perform(context)
    video_device = LaunchConfiguration("video_device")
    detector_value = LaunchConfiguration("detector").perform(context)

    # Select AI model based on 'detector' argument
    detector_configs = {
        "yolov8": {"executable": "yolov8_object_detection", "model_type": "yolov8_rps"},
        "yolox":  {"executable": "yolox_rps_detection",      "model_type": "yolox_s_rps"},
    }
    if detector_value not in detector_configs:
        raise RuntimeError(
            f"Unknown detector '{detector_value}'. Valid options: {list(detector_configs.keys())}"
        )
    detector_cfg = detector_configs[detector_value]

    foxglove_keypoint_pkg_dir = get_package_share_directory(
        "foxglove_keypoint_publisher"
    )
    rzv_demo_rps_dir = get_package_share_directory("rzv_demo_rps")

    hand_config_path = os.path.join(
        rzv_demo_rps_dir, "config/hand/inspire_rh56e2.yaml"
    )

    nodes = []

    nodes.append(SetEnvironmentVariable("TVM_NUM_THREADS", "2"))

    inspire_rh56e2_hand_bringup_pkg = get_package_share_directory(
        "inspire_rh56e2_hand_bringup"
    )

    robot_bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                inspire_rh56e2_hand_bringup_pkg,
                "launch",
                "inspire_rh56e2_hand_joint_position_control.launch.py",
            )
        ),
        launch_arguments={
            "hand_side": hand_side_value,
            "use_mock_hardware": use_mock_hardware_value,
            "serial_port": serial_port_value,
            "hand_speed": hand_speed_value,
        }.items(),
    )
    nodes.append(robot_bringup_launch)

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

    object_detection_node = Node(
        package="rzv_object_detection",
        executable=detector_cfg["executable"],
        name="object_detection",
        parameters=[
            {
                "model_type": detector_cfg["model_type"],
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

    rps_controller_node = Node(
        package="rzv_demo_rps",
        executable="rps_controller",
        name="rps_controller",
        output="screen",
        parameters=[{"always_win_mode": True}],
        remappings=[("/hand_pose", "/object_detection/rps_hand_detect")],
    )
    nodes.append(rps_controller_node)

    hand_gesture_interpreter_node = Node(
        package="arm_hand_control",
        executable="hand_gesture_interpreter",
        name="hand_gesture_interpreter",
        output="screen",
        parameters=[
            {
                "config_file": hand_config_path,
                "auto_demo_enabled": False,
                "gesture_duration": 0.2,
                "transition_duration": 0.15,
            }
        ],
        remappings=[
            (
                "/position_controller_command",
                "/inspire_rh56e2_hand_joint_position_controller/commands",
            ),
        ],
    )
    nodes.append(hand_gesture_interpreter_node)

    return nodes


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "serial_port",
                default_value="/dev/ttyUSB0",
                description="Serial port for the physical DexHand",
            ),
            DeclareLaunchArgument(
                "hand_speed",
                default_value="1000",
                description="Target motor speed for all joints (0-1000, 1000 = max speed)",
            ),
            DeclareLaunchArgument(
                "hand_side",
                default_value="left",
                description="Which hand to control: left or right",
            ),
            DeclareLaunchArgument(
                "use_mock_hardware",
                default_value="true",
                description="Use mock hardware in ros2_control",
            ),
            DeclareLaunchArgument(
                "video_device",
                default_value="/dev/video0",
                description="Video device path for camera input",
            ),
            DeclareLaunchArgument(
                "detector",
                default_value="yolov8",
                description="AI detector to use: 'yolov8' (yolov8_rps model) or 'yolox' (yolox_s_rps model)",
            ),
            OpaqueFunction(function=launch_setup),
        ]
    )
