# RZ/V Demo Rock-Paper-Scissor (RPS)

This ROS 2 package enables hand using rock-paper-scissors gesture recognition. It captures hand gestures through a vision-based recognition system and translates them into control commands to interact with games. Beside that, also providing launch files and configurations for demonstrating Rock-Paper-Scissor on Renesas RZ/V platforms.
## Overview

This package provides node for controlling robotic hands. It supports:
- Rock-Paper-Scissors Controller: Detects rock–paper–scissors gestures in real time, executes the game logic, and sends commands to control the robotic hand accordingly.
- Compatible with the Inspire RH56, Inspire RH56E2, and Ruiyan RH2 robotic hands.

The RZ/V Demo Rock-Paper-Scissor package enables:
- RPS Object detection and interpretation
- Simultaneous control of virtual and physical dexterous hands
- Support visualization through Foxglove Studio

## RPS game play
  1. Similar to the traditional game.
  2. The user initiates a game by showing the "HI" pose (scissors gesture) in front of the camera.
  3. The robotic hand performs a 1-2-3 countdown to signal the start of the round.
  4. When the countdown is finished, the player must show their chosen gesture (rock, paper, or scissors) within 2 seconds. If no gesture is detected in this time, the game is aborted.
  5. In case players give the choice, the robotic hand randomly selects and displays rock, paper, or scissors.
  6. After that, the game result is displayed by the robotic hand using the following gestures: `OK` – Draw, `Victory` – You lose, `Thumbs Up` – You win.
  6. Wait 2 seconds after the result is shown to start a new game.

## Nodes

### Rock-Paper-Scissor Controller (`rps_controller_node`)

Subscribes to string-based RPS pose topics, processes them through the game logic, and sends commands to control the robotic hand.
- **Subscriptions**:
  - `hand_pose` (std_msgs/String) - Receives RPS poses: `"rock"`, `"scissor"`, `"paper"`.
- **Action client**:
  - `execute_gesture` (arm_hand_control/action/ExecuteGesture) - Sends a goal containing gesture_name to command the robotic hand to perform the corresponding pose for interacting with the player.


## RZ/V ROS2 Package Dependencies

## Base Packages
| Package Name | Description |
|---------------|-------------|
| `arm_hand_control` | Receive goal to control the dexterous hand for interacting with player. |
| `foxglove_keypoint_publisher` | Publishes bounding boxif for visualization in Foxglove Studio. |
| `rzv_demo_rps` | Main demo package integrating DexHand functionalities on RZ/V platform. |

## Model Zoo

### Base Models
| Package Name | Description |
|---------------|-------------|
| `rzv_model` | AI model abstractions and implementations for RZ/V MPU platforms. |
| `rzv_model_utils_ros2` | Collection of helper functions for integrating AI models into ROS 2 applications. |

### Hand Models
| Package Name | Description |
|---------------|-------------|
| `rzv_yolov8` | YOLOv8 object detection models optimized for RZ/V processors with DRP-AI acceleration. |

### Application
| Package Name | Description |
|---------------|-------------|
| `rzv_object_detection` | Object detection capabilities and ROS2 node to publish detection topics for demos. |

### Inspire RH56 Hand Packages

| Package Name | Description |
|--------------|-------------|
| `inspire_rh56_hand_description` | URDF and mesh models for the Inspire RH56 dexterous hand. |
| `inspire_rh56_hand_ros2_control` | ros2_control configuration and hardware interface for the Inspire RH56 hand. |
| `inspire_rh56_hand_bringup` | Launch files to start the Inspire RH56 hand system, including controllers and visualization. |

### Inspire RH56E2 Hand Packages

| Package Name | Description |
|--------------|-------------|
| `inspire_rh56e2_hand_description` | URDF and mesh models for the Inspire RH56E2 dexterous hand. |
| `inspire_rh56e2_hand_ros2_control` | ros2_control configuration and hardware interface for the Inspire RH56E2 hand. |
| `inspire_rh56e2_hand_bringup` | Launch files to start the Inspire RH56E2 hand system, including controllers and visualization. |

### Ruiyan RH2 DexHand Demo
| Package Name | Description |
|--------------|-------------|
| `ruiyan_rh2_hand_description` | URDF and mesh models for the Ruiyan RH2 dexterous hand. |
| `ruiyan_rh2_hand_ros2_control` | ros2_control configuration and hardware interface for the Ruiyan RH2 hand. |
| `ruiyan_rh2_hand_bringup` | Launch files to start the Ruiyan RH2 hand system, including controllers and visualization. |

## Prerequisites
### Hardware Requirements:
- USB camera for hand tracking
- Optional: Inspire RH56 DexHand (for physical hand demo)
- Optional: Inspire RH56E2 DexHand (for physical hand demo)
- Optional: RuiYan RH2 DexHand (for physical hand demo)

## Quick Setup Guide
### Build the Rock-Paper-Scissor demo application

Install the packages listed in [RZ/V ROS2 Package Dependencies](#rzv-ros2-package-dependencies) and refer to the **ROS2 Application Development/Cross-build the ROS2 Application** in the **RZ/V2H Robotic Development Kit User Manual** documentation to build and compile and deploy them.

Additionally, **native builds using `colcon`** are still supported.

For more details, please refer to the official ROS 2 guide: [Using colcon to build packages](https://docs.ros.org/en/jazzy/Tutorials/Beginner-Client-Libraries/Colcon-Tutorial.html)

### Install the package dependencies
After completing Step 2 above, deploy the `install` folder to the target board if you are using the cross-build method.

Use `rosdep` to install all required dependencies on the target board:
```bash
# Chane the directory to your ROS2 workspace
cd <your_ros2_ws>

# Install dependencies for the following common packages
rosdep install --from-paths install/*/share -y -r --ignore-src
```

### Load the workspace
You must source the setup script to make the packages visible to ROS:
```bash
# Source ROS2 in the current shell
source /opt/ros/jazzy/setup.bash

source install/setup.bash
```

## Run the Rock-Paper-Scissor demo
### Connect and setup hardware

Connect the USB camera to the RZ/V2H RDK board.

**Optional:** Connect the dexterous hand to the RZ/V2H RDK board if you want to control the real hand.

**Note**: Before running the demo application, please make sure to set up the hardware using the provided setup script.
For detailed instructions, refer to the corresponding dexhand package for each hand type.
### Run the Demo

To launch the virtual hands demo (without requiring hand hardware):

```bash
# For Inspire RH56 hand
ros2 launch rzv_demo_rps demo_inspire_rh56_hand_rps.launch.py use_mock_hardware:=true

# For Inspire RH56E2 hand
ros2 launch rzv_demo_rps demo_inspire_rh56e2_hand_rps.launch.py use_mock_hardware:=true

# For Ruiyan RH2 hand
ros2 launch rzv_demo_rps demo_ruiyan_rh2_hand_rps.launch.py use_mock_hardware:=true
```

To launch the physical Inspire RH56 hand control demo:

```bash
ros2 launch rzv_demo_rps demo_inspire_rh56_hand_rps.launch.py use_mock_hardware:=false video_device:=/dev/video0 serial_port:=/dev/ttyUSB0
```

To launch the low-latency always-win Inspire RH56 demo:

```bash
# With YOLOv8 (default)
ros2 launch rzv_demo_rps demo_inspire_rh56_hand_rps_always_win.launch.py use_mock_hardware:=false video_device:=/dev/video0 serial_port:=/dev/ttyUSB0

# With YOLOX
ros2 launch rzv_demo_rps demo_inspire_rh56_hand_rps_always_win.launch.py use_mock_hardware:=false video_device:=/dev/video0 serial_port:=/dev/ttyUSB0 detector:=yolox
```

To launch the physical Inspire RH56E2 hand control demo:

```bash
ros2 launch rzv_demo_rps demo_inspire_rh56e2_hand_rps.launch.py use_mock_hardware:=false video_device:=/dev/video0 serial_port:=/dev/ttyUSB0
```

To launch the low-latency always-win Inspire RH56E2 demo:

```bash
# With YOLOv8 (default)
ros2 launch rzv_demo_rps demo_inspire_rh56e2_hand_rps_always_win.launch.py use_mock_hardware:=false video_device:=/dev/video0 serial_port:=/dev/ttyUSB0

# With YOLOX
ros2 launch rzv_demo_rps demo_inspire_rh56e2_hand_rps_always_win.launch.py use_mock_hardware:=false video_device:=/dev/video0 serial_port:=/dev/ttyUSB0 detector:=yolox
```

To launch the physical RuiYan RH2 hand control demo:

```bash
ros2 launch rzv_demo_rps demo_ruiyan_rh2_hand_rps.launch.py use_mock_hardware:=false video_device:=/dev/video0 can_interface:=can2
```

To launch the low-latency always-win RuiYan RH2 demo:

```bash
# With YOLOv8 (default)
ros2 launch rzv_demo_rps demo_ruiyan_rh2_hand_rps_always_win.launch.py use_mock_hardware:=false video_device:=/dev/video0 can_interface:=can2

# With YOLOX
ros2 launch rzv_demo_rps demo_ruiyan_rh2_hand_rps_always_win.launch.py use_mock_hardware:=false video_device:=/dev/video0 can_interface:=can2 detector:=yolox
```

### Launch Arguments
- `video_device`: Specify the camera device (default: `/dev/video0`)
- `serial_port`: Serial port for the physical Inspire RH56 DexHand (default: `/dev/ttyUSB0`)
- `can_interface`: CAN interface for the physical RuiYan RH2 DexHand (default: `can2`)
- `hand_speed`: Target motor speed for all joints, 0-1000 (default: `1000`)
- `hand_side`: Which hand to control: `left` or `right` (default: `left`)
- `use_mock_hardware`: Set to `true` for simulation/testing without physical hardware
- `detector`: AI detector to use in always-win launch files: `yolov8` (default) or `yolox`

## Launch Files
 
### demo_inspire_rh56_hand_rps.launch.py
 
This launch file runs a Rock-Paper-Scissors game demo that controls a physical Inspire RH56 dexterous hand using camera-based hand pose detection:
 
```
PIPELINE:
camera → object detection → rps game controller → ros2_control position controller
  → joint_state_broadcaster → urdf visualization + real hand control
 
TOPIC FLOW:
- Camera publishes: /image_raw
- Object detection subscribes to: /image_raw
  publishes: /object_detection/bounding_box, /object_detection/rps_hand_detect
- Visualization node subscribes to: /object_detection/bounding_box
  publishes: /bbox_visualization
- RPS Controller subscribes to: /object_detection/rps_hand_detect
  sends action goal to: /execute_gesture/goal
- Hand gesture interpreter acts as action server on: /execute_gesture/goal
  publishes: /inspire_rh56_hand_joint_position_controller/commands
- ros2_control position controller subscribes to: /inspire_rh56_hand_joint_position_controller/commands
- joint_state_broadcaster publishes: /joint_states
- URDF publishers subscribe to: /joint_states for hand visualization
```
 
Components included in this launch file:
1. **Robot Bringup** (`inspire_rh56_hand_bringup`): Initializes ros2_control with the Inspire RH56 joint position controller and joint state broadcaster; connects to the physical hand via serial port
2. **Camera Node**: Captures video input for hand pose detection via V4L2
3. **Object Detection Node**: Detects rock–paper–scissors hand poses using YOLOv8
4. **Visualization Node**: Creates bounding box visual representation for Foxglove Studio
5. **RPS Controller Node**: Subscribes to detected hand poses and sends gesture action goals based on RPS game logic
6. **Hand Gesture Interpreter**: Acts as action server; executes gesture commands by publishing joint position commands

### demo_inspire_rh56_hand_rps_always_win.launch.py

This launch file runs the low-latency always-win mode for the Inspire RH56 hand. The RPS controller immediately responds with the gesture that beats the detected user pose. The AI detector is selectable at launch time via the `detector` argument:

- `detector:=yolov8` (default) — uses `yolov8_object_detection` with `yolov8_rps` model
- `detector:=yolox` — uses `yolox_rps_detection` with `yolox_s_rps` model

### demo_inspire_rh56e2_hand_rps.launch.py

This launch file runs a Rock-Paper-Scissors game demo that controls a physical Inspire RH56E2 dexterous hand using camera-based hand pose detection:

```
PIPELINE:
camera -> object detection -> rps game controller -> ros2_control position controller
  -> joint_state_broadcaster -> urdf visualization + real hand control

TOPIC FLOW:
- Camera publishes: /image_raw
- Object detection subscribes to: /image_raw
  publishes: /object_detection/bounding_box, /object_detection/rps_hand_detect
- Visualization node subscribes to: /object_detection/bounding_box
  publishes: /bbox_visualization
- RPS Controller subscribes to: /object_detection/rps_hand_detect
  sends action goal to: /execute_gesture/goal
- Hand gesture interpreter acts as action server on: /execute_gesture/goal
  publishes: /inspire_rh56e2_hand_joint_position_controller/commands
- ros2_control position controller subscribes to: /inspire_rh56e2_hand_joint_position_controller/commands
- joint_state_broadcaster publishes: /joint_states
- URDF publishers subscribe to: /joint_states for hand visualization
```

Components included in this launch file:
1. **Robot Bringup** (`inspire_rh56e2_hand_bringup`): Initializes ros2_control with the Inspire RH56E2 joint position controller and joint state broadcaster; connects to the physical hand via serial port
2. **Camera Node**: Captures video input for hand pose detection via V4L2
3. **Object Detection Node**: Detects rock–paper–scissors hand poses using YOLOv8
4. **Visualization Node**: Creates bounding box visual representation for Foxglove Studio
5. **RPS Controller Node**: Subscribes to detected hand poses and sends gesture action goals based on RPS game logic
6. **Hand Gesture Interpreter**: Acts as action server; executes gesture commands by publishing joint position commands

### demo_inspire_rh56e2_hand_rps_always_win.launch.py

This launch file runs the low-latency always-win mode for the Inspire RH56E2 hand. The RPS controller immediately responds with the gesture that beats the detected user pose:

- User `paper` -> robot `scissor`
- User `rock` -> robot `paper`
- User `scissor` -> robot `rock`

The AI detector is selectable at launch time via the `detector` argument:

- `detector:=yolov8` (default) — uses `yolov8_object_detection` with `yolov8_rps` model
- `detector:=yolox` — uses `yolox_rps_detection` with `yolox_s_rps` model

The controller publishes `ALWAYS_WIN` status on `/game_status`, and `config/foxglove/demo_rps_always_win.json` provides a separate Foxglove layout for inspecting detection, inference timing, game status, hand commands, and hand visualization across the supported hands. The original `demo_rps.json` layout is unchanged.
 
### demo_ruiyan_rh2_hand_rps.launch.py
 
This launch file runs a Rock-Paper-Scissors game demo that controls a physical RuiYan RH2 dexterous hand using camera-based hand pose detection:
 
```
PIPELINE:
camera → object detection → rps game controller → ros2_control position controller
  → joint_state_broadcaster → urdf visualization + real hand control
 
TOPIC FLOW:
- Camera publishes: /image_raw
- Object detection subscribes to: /image_raw
  publishes: /object_detection/bounding_box, /object_detection/rps_hand_detect
- Visualization node subscribes to: /object_detection/bounding_box
  publishes: /bbox_visualization
- RPS Controller subscribes to: /object_detection/rps_hand_detect
  sends action goal to: /execute_gesture/goal
- Hand gesture interpreter acts as action server on: /execute_gesture/goal
  publishes: /ruiyan_rh2_hand_joint_position_controller/commands
- ros2_control position controller subscribes to: /ruiyan_rh2_hand_joint_position_controller/commands
- joint_state_broadcaster publishes: /joint_states
- URDF publishers subscribe to: /joint_states for hand visualization
```
 
Components included in this launch file:
1. **Robot Bringup** (`ruiyan_rh2_hand_bringup`): Initializes ros2_control with the RuiYan RH2 joint position controller and joint state broadcaster; connects to the physical hand via CAN interface
2. **Camera Node**: Captures video input for hand pose detection via V4L2
3. **Object Detection Node**: Detects rock–paper–scissors hand poses using YOLOv8
4. **Visualization Node**: Creates bounding box visual representation for Foxglove Studio
5. **RPS Controller Node**: Subscribes to detected hand poses and sends gesture action goals based on RPS game logic
6. **Hand Gesture Interpreter**: Acts as action server; executes gesture commands by publishing joint position commands

### demo_ruiyan_rh2_hand_rps_always_win.launch.py

This launch file runs the low-latency always-win mode for the RuiYan RH2 hand. The RPS controller immediately responds with the gesture that beats the detected user pose. The AI detector is selectable at launch time via the `detector` argument:

- `detector:=yolov8` (default) — uses `yolov8_object_detection` with `yolov8_rps` model
- `detector:=yolox` — uses `yolox_rps_detection` with `yolox_s_rps` model

## Visualization with Foxglove Studio

The demo can be visualized using Foxglove Studio by connecting to the Foxglove Bridge websocket.

#### Using the Preset Layout

For the best visualization experience, a preset panel layout is provided:

1. Start Foxglove Studio
2. Connect to the Foxglove Bridge websocket (typically `ws://localhost:8765`)
3. Click on "Layouts" in the top menu
4. Select "Import layout from file"
5. Navigate to the `config/foxglove/demo_rps.json` file in the rzv_demo_rps package
6. Click "Open" to load the preset layout

For always-win mode, import `config/foxglove/demo_rps_always_win.json` instead.

The preset layout provides:
- Camera view with hand landmark overlays
- 3D visualization of the virtual hands
- Joint state monitoring panels
- Custom panels configured specifically for the dexterous hand demo

This layout ensures all the necessary visualization components are properly set up without manual configuration.

#### Troubleshooting

- Palm Orientation Matters: For optimal detection, make sure the front of the palm faces the camera directly and vertically. Angled hands may reduce accuracy.
- Image Lag in Foxglove Studio: If you experience lag or frozen image streams, simply restart Foxglove Studio.
- 3D Hand Model Not Showing: Sometimes, the 3D hand visualization may not appear properly. In such cases, restart the application (either the demo app or visualization tool).

## License
Apache License 2.0
