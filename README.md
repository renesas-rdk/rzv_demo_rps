# RZ/V Demo Rock-Paper-Scissor (RPS)

This ROS 2 package enables hand using rock-paper-scissors gesture recognition. It captures hand gestures through a vision-based recognition system and translates them into control commands to interact with games. Beside that, also providing launch files and configurations for demonstrating Rock-Paper-Scissor on Renesas RZ/V platforms.
## Overview

This package provides node for controlling robotic hands. It supports:
- Rock-Paper-Scissors Controller: Detects rock–paper–scissors gestures in real time, executes the game logic, and sends commands to control the robotic hand accordingly.
- Compatible with the Inspire RH56 Dexhand and Ruiyan RH2 robotic hands.

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

| Category | Package Name | Description |
|-----------|---------------|-------------|
| **Base Packages** | `arm_hand_control` | Receive goal to control the dexterous hand for interacting with player. |
|  | `foxglove_keypoint_publisher` | Publishes bounding boxif for visualization in Foxglove Studio. |
|  | `rzv_demo_rps` | Main demo package integrating DexHand functionalities on RZ/V platform. |
|  | `rzv_model` | Contains model definitions and configuration files for the RZ/V system. |
|  | `rzv_object_detection` | Provides rps pose detection capabilities on Renesas RZ/V platforms. |
| **For Inspire RH56 DexHand Demo** | `inspire_rh56_urdf` | URDF models for the Inspire RH56 dexterous hand. |
|  | `inspire_rh56_dexhand` | Application and control logic for the Inspire RH56 hand. |
| **For Ruiyan RH2 DexHand Demo** | `ruiyan_rh2_controller` | Control package for the Ruiyan RH2 dexterous hand. |
|  | `ruiyan_rh2_urdf` | URDF models for the Ruiyan RH2 hand. |
|  | `ruiyan_rh2_dexhand` | Control node for the Ruiyan RH2 hand. |

## Prerequisites
### Hardware Requirements:
- USB camera for hand tracking
- Optional: Inspire RH56 DexHand (for physical hand demo)
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
ros2 launch rzv_demo_rps demo_virtual_inspire_rh56_hand.launch.py

# For Ruiyan RH2 hand
ros2 launch rzv_demo_rps demo_virtual_ruiyan_rh2_hand.launch.py
```

To launch the physical Inspire RH56 hand control demo:

```bash
ros2 launch rzv_demo_rps demo_physical_inspire_rh56_hand_rps.launch.py video_device:=/dev/video0 serial_port:=/dev/ttyUSB0
```

To launch the physical RuiYan RH2 hand control demo:

```bash
ros2 launch rzv_demo_rps demo_physical_ruiyan_rh2_hand_rps.launch.py video_device:=/dev/video0 can_port:=can2
```

### Launch Arguments
- `video_device`: Specify the camera device (default: `/dev/video0`)
- `serial_port`: Serial port for the physical Inspire RH56 DexHand (default: `/dev/ttyUSB0`, only for `demo_physical_hand.launch.py`)
- `can_port`: Can port for the physical RuiYan RH2 DexHand (default: `can2`, only for `demo_physical_ruiyan_rh2_hand.launch.py`)


## Launch Files

#### demo_virtual_inspire_rh56_hand.launch.py and demo_virtual_ruiyan_rh2_hand.launch.py

This launch file sets up a camera-based hand tracking system that controls virtual Inspire RH56 hands or Ruiyan RH2 hands:

```
PIPELINE:
camera → object detection  → rps controller → hand gesture interpreters → urdf visualization

Topic flow:
- Camera: publishes /image_raw
- Object detection: subscribes to /image_raw
  publishes /object_detection_node/bounding_box, /object_detection_node/rps_hand_detect
- Visualization: subscribes to /object_detection_node/bounding_box and publishes visualization markers
- RPS Controller: subscribes to /object_detection_node/rps_hand_detect
  sends action goal to: /execute_gesture/goal
- Hand gesture interpreter:  receives action goal from: /execute_gesture/goal
  publishes /joint_states (alternative control method)
- URDF publishers: subscribe to /joint_states for hand visualization
```

Components included in this launch file:
1. **Camera Node**: Captures video input for hand tracking
2. **Object Detection Node**: Detects rock–paper–scissors hand poses
3. **Visualization Nodes**: Create visual representations for Foxglove Studio
4. **RPS Controller Node**: Converts detected hand poses to logic game
5. **Hand Gesture Interpreter**: Provides control through gesture commands.
6. **URDF State Publishers**: Visualize both right and left hands
7. **Foxglove Bridge**: Enables visualization through Foxglove Studio

#### demo_physical_inspire_rh56_hand_rps.launch.py

This launch file extends the virtual hand demo to also control a physical Inspire RH56 dexterous hand:

```
PIPELINE:
camera → object detection  → rps controller → hand gesture interpreters → urdf visualization + real hand control

Topic flow:
- Camera: publishes /image_raw
- Object detection: subscribes to /image_raw
  publishes /object_detection_node/bounding_box, /object_detection_node/rps_hand_detect
- Visualization: subscribes to /object_detection_node/bounding_box and publishes visualization markers
- RPS Controller: subscribes to /object_detection_node/rps_hand_detect
  sends action goal to: /execute_gesture/goal
- Hand gesture interpreter:  receives action goal from: /execute_gesture/goal
  publishes /joint_states (alternative control method)
- URDF publishers: subscribe to /joint_states for hand visualization
- Physical hand controller: subscribes to /joint_states to control the real DexHand
```

Components included in this launch file:
1. **Camera Node**: Captures video input for hand tracking
2. **Object Detecction Node**: Detects rock–paper–scissors hand poses
3. **Visualization Nodes**: Create visual representations for Foxglove Studio
4. **RPS Controller Node**: Converts detected hand poses to logic game
5. **Hand Gesture Interpreter**: Provides control through gesture commands.
6. **URDF State Publishers**: Visualize both right and left hands
7. **Real Hand Control**: Controls physical Inspire RH56 DexHand via serial connection
8. **Foxglove Bridge**: Enables visualization through Foxglove Studio

#### demo_physical_ruiyan_rh2_hand_rps.launch.py

This launch file extends the virtual hand demo to also control a physical RuiYan RH2 dexterous hand:
```
Pipeline:
camera → object detection  → rps controller → hand gesture interpreters → urdf visualization + real hand control

Topic flow:
- Camera: publishes /image_raw
- Object detection: subscribes to /image_raw
  publishes /object_detection_node/bounding_box, /object_detection_node/rps_hand_detect
- Visualization: subscribes to /object_detection_node/bounding_box and publishes visualization markers
- RPS Controller: subscribes to /object_detection_node/rps_hand_detect
  sends action goal to: /execute_gesture/goal
- Hand gesture interpreter:  receives action goal from: /execute_gesture/goal
  publishes /joint_states (alternative control method)
- URDF publishers: subscribe to /joint_states for hand visualization
- Ruiyan RH2 DexHand: Perform message conversion: subscribes to /joint_states, publishes /ryhand6_cmd
- Physical hand controller: subscribes to /ryhand6_cmd to control the real DexHand
```
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
