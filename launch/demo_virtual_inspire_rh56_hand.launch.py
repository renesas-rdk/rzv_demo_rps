# *********************************************************************************************************************
# Copyright [2025] Renesas Electronics Corporation and/or its licensors. All Rights Reserved.
#
# The contents of this file (the "contents") are proprietary and confidential to Renesas Electronics Corporation
# and/or its licensors ("Renesas") and subject to statutory and contractual protections.
#
# Unless otherwise expressly agreed in writing between Renesas and you: 1) you may not use, copy, modify, distribute,
# display, or perform the contents; 2) you may not use any name or mark of Renesas for advertising or publicity
# purposes or in connection with your use of the contents; 3) RENESAS MAKES NO WARRANTY OR REPRESENTATIONS ABOUT THE
# SUITABILITY OF THE CONTENTS FOR ANY PURPOSE; THE CONTENTS ARE PROVIDED "AS IS" WITHOUT ANY EXPRESS OR IMPLIED
# WARRANTY, INCLUDING THE IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND
# NON-INFRINGEMENT; AND 4) RENESAS SHALL NOT BE LIABLE FOR ANY DIRECT, INDIRECT, SPECIAL, OR CONSEQUENTIAL DAMAGES,
# INCLUDING DAMAGES RESULTING FROM LOSS OF USE, DATA, OR PROJECTS, WHETHER IN AN ACTION OF CONTRACT OR TORT, ARISING
# OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THE CONTENTS. Third-party contents included in this file may
# be subject to different terms.
# *********************************************************************************************************************

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.actions import SetEnvironmentVariable
from launch.launch_description_sources import FrontendLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument

def generate_launch_description():
    """
    Launch camera-based hand tracking with virtual hand control.

    Pipeline:
    camera → object detection  → rps game controller → hand gesture interpreters → urdf visualization

    Topic flow:
    - Camera: publishes /image_raw
    - Object detection: subscribes to /image_raw
      publishes /object_detection/bounding_box, /object_detection/rps_hand_detect
    - Visualization: subscribes to /object_detection/bounding_box and publishes visualization markers
    - RPS Game Controller: subscribes to /object_detection/rps_hand_detect
      sends action goal to: /execute_gesture/goal
    - Hand gesture interpreter:  receives action goal from: /execute_gesture/goal
      publishes /joint_states (alternative control method)
    - URDF publishers: subscribe to /joint_states for hand visualization
    """
    # Create LaunchConfiguration objects for customizable parameters
    video_device = LaunchConfiguration('video_device', default='/dev/video0')

    # Define parameter declarations
    video_device_arg = DeclareLaunchArgument(
        'video_device',
        default_value='/dev/video0',
        description='Video device path for camera input'
    )


    # Define package directories
    inspire_pkg_dir = get_package_share_directory('inspire_rh56_urdf')
    inspire_rh56_config_pkg_dir = get_package_share_directory('inspire_rh56_dexhand')
    foxglove_keypoint_pkg_dir = get_package_share_directory('foxglove_keypoint_publisher')

    # Set TVM_NUM_THREADS environment variable for hand landmark estimation
    set_tvm_threads = SetEnvironmentVariable('TVM_NUM_THREADS', '2')

    # 1. Camera node
    # PUBLISHES: /image_raw
    camera_node = Node(
        package='v4l2_camera',
        executable='v4l2_camera_node',
        name='v4l2_camera',
        parameters=[{
            'video_device': video_device,
            'output_encoding': 'yuv422_yuy2',
            'image_size': [640, 480]
        }]
    )

    # 2. Object detection node
    # SUBSCRIBES: /image_raw
    # PUBLISHES: /object_detection/bounding_box, /object_detection/rps_hand_detect
    object_detection_node = Node(
        package='rzv_object_detection',
        executable='yolov8_object_detection',
        name='object_detection',
        parameters=[{
            'model_type': 'yolov8_rps',
            'processing_queue_size': 1,
            'confidence_threshold': 0.8,
            'iou_threshold': 0.3,
        }],
        remappings=[
            ('/image_raw', '/image_raw'),
            ('/bounding_box', '/object_detection/bounding_box'),
            ('/rps_hand_detect', '/object_detection/rps_hand_detect')
        ],
        output='screen',
        arguments=['--ros-args', '--log-level', 'INFO']
    )

    # 3. Visualization nodes for Foxglove Studio
    # 3.1 Bounding box visualization
    # SUBSCRIBES: /object_detection/bounding_box
    # PUBLISHES: bbox_visualization
    bbox_config_path = os.path.join(foxglove_keypoint_pkg_dir, 'config/poses/bounding_box.yaml')
    foxglove_hand_bbox_publisher_node = Node(
        package='foxglove_keypoint_publisher',
        executable='foxglove_keypoint_publisher_node',
        name='foxglove_hand_bbox_publisher',
        parameters=[{'config_file': bbox_config_path}],
        remappings=[
            ('/keypoint_poses', '/object_detection/bounding_box'),
            ('/keypoint_visualization', '/bbox_visualization')
        ],
        output='screen'
    )

    # 4. Interpreter for controlling hands

    # 4.1 Rock-Paper-Scissors game controller
    # SUBSCRIBES TO: /object_detection/rps_hand_detect
    # ACTION CLIENT: /execute_gesture/goal
    hand_config_path = os.path.join(inspire_rh56_config_pkg_dir, 'config/inspire_rh56.yaml')
    rps_controller_node = Node(
        package='rzv_demo_rps',
        executable='rps_controller',
        name='rps_controller',
        output='screen',
        remappings=[
            ('/hand_pose', '/object_detection/rps_hand_detect')
        ]
    )

    # 4.2 Hand gesture interpreter
    # ACTION SERVER: /execute_gesture/goal
    # PUBLISHES: /joint_states
    hand_gesture_interpreter = Node(
        package='arm_hand_control',
        executable='hand_gesture_interpreter',
        name='hand_gesture_interpreter',
        output='screen',
        parameters=[{
            'config_file': hand_config_path,
            'auto_demo_enabled': False,
            'gesture_duration': 1.0,
            'transition_duration': 0.5
        }],
    )

    # 5. URDF state publishers for visualization
    # 5.1 Right hand URDF publisher
    # SUBSCRIBES: /joint_states
    # PUBLISHES: /tf, /tf_static (for right hand visualization)
    right_hand_urdf = os.path.join(inspire_pkg_dir, 'urdf', 'inspire_hand_right.urdf')
    with open(right_hand_urdf, 'r') as file:
        right_hand_description = file.read()

    right_hand_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='right_hand_state_publisher',
        output='screen',
        parameters=[
            {'robot_description': right_hand_description},
            {'frame_prefix': 'right_hand/'}
        ],
        remappings=[
            ('/robot_description', '/right_hand/robot_description')
        ]
    )

    # 5.2 Left hand URDF publisher
    # SUBSCRIBES: /joint_states
    # PUBLISHES: /tf, /tf_static (for left hand visualization)
    left_hand_urdf = os.path.join(inspire_pkg_dir, 'urdf', 'inspire_hand_left.urdf')
    with open(left_hand_urdf, 'r') as file:
        left_hand_description = file.read()

    left_hand_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='left_hand_state_publisher',
        output='screen',
        parameters=[
            {'robot_description': left_hand_description},
            {'frame_prefix': 'left_hand/'}
        ],
        remappings=[
            ('/robot_description', '/left_hand/robot_description')
        ]
    )

    # 6. Foxglove bridge for visualization in Foxglove Studio
    # BRIDGES: All relevant topics for visualization in Foxglove Studio
    foxglove_bridge_launch = IncludeLaunchDescription(
        FrontendLaunchDescriptionSource(
            os.path.join(get_package_share_directory('foxglove_bridge'), 'launch', 'foxglove_bridge_launch.xml')
        )
    )

    # Return all nodes in execution order with proper grouping
    return LaunchDescription([
        # 1. Launch Arguments - Parameter configuration
        video_device_arg,                     # Camera device configuration

        # 2. Environment configuration
        set_tvm_threads,                      # Set TVM_NUM_THREADS environment variable

        # 3. Pipeline nodes - in processing order
        camera_node,                          # Image source
        object_detection_node,            # Hand RPS pose detection

        # 4. Visualization nodes
        foxglove_hand_bbox_publisher_node,    # Bounding box visualization

        # 5. Control nodes
        rps_controller_node,       # Controls game logic using hand RPS pose
        hand_gesture_interpreter,       # Interprets hand gestures to control the hand

        # 6. Robot state publisher nodes
        right_hand_publisher,                 # Virtual right hand visualization
        left_hand_publisher,                  # Virtual left hand visualization

        # 7. Visualization tools
        foxglove_bridge_launch,               # Visualization bridge
    ])
