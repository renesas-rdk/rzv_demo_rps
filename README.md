# RZ/V Demo Rock-Paper-Scissor (RPS)

This ROS 2 package enables hand using rock-paper-scissors gesture recognition. It captures hand gestures through a vision-based recognition system and translates them into control commands to interact with games. Beside that, also providing launch files and configurations for demonstrating Rock-Paper-Scissor on Renesas RZ/V platforms.
## Overview

This package provides node for controlling robotic hands. It supports:
- Rock-Paper-Scissors Controller: Detects rock–paper–scissors gestures in real time, executes the game logic, and sends commands to control the robotic hand accordingly.
- Compatible with the Inspire RH56 Dexhand and Ruiyan RH2 robotic hands.

The RZ/V Demo Rock-Paper-Scissor package enables:
- Hand RPS estimation and interpretation
- Simultaneous control of virtual and physical dexterous hands
- Visualization through Foxglove Studio

## RPS game play
  1. Similar to the traditional game.
  2. The user initiates a game by showing the "HI" pose (scissors gesture) in front of the camera.
  3. The robotic hand performs a 1-2-3 countdown to signal the start of the round.
  4. When the countdown is finished, the player must show their chosen gesture (rock, paper, or scissors) within 2 seconds. If no gesture is detected in this time, the game is aborted.
  5. In case players give the choice, the robotic hand randomly selects and displays rock, paper, or scissors.
  6. After that, the game result is displayed by the robotic hand using the following gestures: `OK` – Draw, `Thumbs Down` – You lose, `Victory` – You win.
  6. Wait 2 seconds after the result is shown to start a new game.

## Nodes

### Rock-Paper-Scissor Controller (`rps_controller_node`)

Subscribes to string-based RPS pose topics, processes them through the game logic, and sends commands to control the robotic hand.
- **Subscriptions**:
  - `hand_pose` (std_msgs/String) - Receives RPS poses: `"rock"`, `"scissor"`, `"paper"`.
- **Action client**:
  - `execute_gesture` (arm_hand_control/action/ExecuteGesture) - Sends a goal containing gesture_name to command the robotic hand to perform the corresponding pose for interacting with the player.

## Package Dependencies

### Vision and Perception
- `rzv_pose_estimation`: Provides rps pose estimation capabilities on Renesas RZ/V platforms
- `v4l2_camera`: Camera interface for video capture
- `foxglove_keypoint_publisher`: Publishes keypoints for visualization

### Hand Control and Visualization
- `arm_hand_control`: Receive goal to control the dexterous hand for interacting with player
- `inspire_rh56_urdf`: URDF models for the Inspire RH56 dexterous hand
- `robot_state_publisher`: Publishes TF information based on joint states
- `tf2_ros`: Transform library for coordinate frames

### Visualization Bridge
- `foxglove_bridge`: Bridges ROS 2 to Foxglove Studio for visualization

## Prerequisites
### Hardware Requirements:
- [RZV2H-EVK Board](https://www.renesas.com/en/design-resources/boards-kits/rz-v2h-evk) - Renesas RZ/V platform
- USB camera for hand tracking
- Physical hand (hardware simulation is supported):
  - Ruiyan RH2 DexHand connected via can port
  - Inspire RH56 DexHand connected via serial port
- Network access (Ethernet)
- USB serial (optional for debugging)
- SD Card (using eSD boot) at least 16GB recommended
### Software requirements:
- A host machine running:
    - `Docker` – used for isolated and repeatable builds
    - `Git` – to clone repositories
    - `SSH` – for remote interaction and deployment to the target board
- Cross-Compiling scripts: A complete guide and supporting scripts for **Cross-Compiling ROS2 Projects for RZ/V2H Using Yocto SDK and Docker**.
- Prebuilt Yocto SDK for RZ/V2H with ROS 2 packages:
    - The prebuilt SDK (.sh installer) includes all the required ROS 2 packages for the Jazzy distribution, ready for cross-compilation.
    - `poky-glibc-*.target.manifest`: A list of available target-side packages installed in the target root filesystem.
- Ubuntu-based Root Filesystem Image
- ROS 2 workspace source code:
  ```bash
  arm_hand_control
  foxglove_keypoint_publisher
  rzv_demo_rps
  rzv_model
  rzv_pose_estimation

  # For Inspire RH56 Dexhand demo
  inspire_rh56_urdf
  inspire_rh56_dexhand

  # For Ruiyan RH2 Dexhand Demo
  ruiyan_rh2_controller
  ruiyan_rh2_urdf
  ruiyan_rh2_dexhand
  ```

**Note:**
> If you intend to run only the Inspire RH56 DexHand demo, you only need to focus on the `inspire_rh56_urdf` and `inspire_rh56_dexhand` folders,
> and ignore the `ruiyan_rh2_controller`, `ruiyan_rh2_urdf`, and `ruiyan_rh2_dexhand` folders.
> Conversely, if you intend to run only the RuiYan RH2 DexHand demo, focus on the RuiYan RH2 folders and ignore the Inspire RH56 ones.
>
> On the provided pure Ubuntu image for the RZ/V2H board, `ros-jazzy-ros-base` is already installed, so step `1. ROS 2 Jazzy Installation` can be skipped.
>
> Additionally, the demo packages were built during the cross-compilation process. Please refer to the `cross-build documentation` for instructions on how to compile them.

### 1. ROS 2 Jazzy Installation
Before installing the package dependencies, ensure you have ROS 2 Jazzy installed on your Ubuntu system:

```bash
# Update package index and install ROS 2 Jazzy base
sudo apt update
sudo apt install ros-jazzy-ros-base
```
For detailed installation instructions, follow the [official ROS2 Jazzy installation guide](https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html).

### 2. Demo Packages and Dependencies Installation

- Deploy the `install/` directory (from cross-compilation) to the board, typically under `/home/rz/ros2_ws/install`

- Use `rosdep` to install all required dependencies:
  ```bash
  # Initialize and update rosdep (only required once per system)
  sudo rosdep init
  rosdep update

  #Install dependencies for the following common packages
  rosdep install --from-paths /path/to/install/*/share -y -r --ignore-src
  ```

### 3. Load the workspace
You must source the setup script to make the packages visible to ROS:
```bash
# Source ROS2 in the current shell
source /opt/ros/jazzy/setup.bash

source <your_ros2_ws>/install/setup.bash
```

## Run the Rock-Paper-Scissor demo
### Connect and setup hardware
Connect both the USB camera and the physical DexHand to the USB ports on the board.

Based on the hardware currently in use: **Inspire RH56** or **Ruiyan RH2**, please run the following script to load the required kernel module or initialize hardware communication:

- **Inspire RH56**:
  `install/rzv_demo_dexhand/share/rzv_demo_dexhand/setup/inspire_rh56_init.sh`

- **Ruiyan RH2**:
  `install/rzv_demo_dexhand/share/rzv_demo_dexhand/setup/ruiyan_rh2_init.sh`

You only need to run this script once when you connect the hardware to the board.

If you are using different hardware, please create your own setup script accordingly.

### Run the Demo

To launch the virtual hands demo (without requiring hand hardware):

```bash
ros2 launch rzv_demo_rps demo_virtual_hand_rps.launch.py
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

#### demo_virtual_hands.launch.py

This launch file sets up a camera-based hand tracking system that controls virtual RuiYan RH2 hands:

```
PIPELINE:
camera → hand rps estimation  → rps controller → hand gesture interpreters → urdf visualization

Topic flow:
- Camera: publishes /image_raw
- Hand rps estimation: subscribes to /image_raw
  publishes /hand_rps_estimation/bounding_box, /hand_rps_estimation/hand_rps
- Visualization: subscribes to /hand_rps_estimation/bounding_box and publishes visualization markers
- RPS Controller: subscribes to /hand_rps_estimation/hand_rps
  sends action goal to: /execute_gesture/goal
- Hand gesture interpreter:  receives action goal from: /execute_gesture/goal
  publishes /joint_states (alternative control method)
- URDF publishers: subscribe to /joint_states for hand visualization
```

Components included in this launch file:
1. **Camera Node**: Captures video input for hand tracking
2. **Hand RPS Estimation**: Detects rock–paper–scissors hand poses
3. **Visualization Nodes**: Create visual representations for Foxglove Studio
4. **RPS Controller Node**: Converts detected hand poses to logic game
5. **Hand Gesture Interpreter**: Provides control through gesture commands.
6. **URDF State Publishers**: Visualize both right and left hands
7. **Foxglove Bridge**: Enables visualization through Foxglove Studio

#### demo_physical_inspire_rh56_hand_rps.launch.py

This launch file extends the virtual hand demo to also control a physical Inspire RH56 dexterous hand:

```
PIPELINE:
camera → hand rps estimation  → rps controller → hand gesture interpreters → urdf visualization + real hand control

Topic flow:
- Camera: publishes /image_raw
- Hand rps estimation: subscribes to /image_raw
  publishes /hand_rps_estimation/bounding_box, /hand_rps_estimation/hand_rps
- Visualization: subscribes to /hand_rps_estimation/bounding_box and publishes visualization markers
- RPS Controller: subscribes to /hand_rps_estimation/hand_rps
  sends action goal to: /execute_gesture/goal
- Hand gesture interpreter:  receives action goal from: /execute_gesture/goal
  publishes /joint_states (alternative control method)
- URDF publishers: subscribe to /joint_states for hand visualization
- Physical hand controller: subscribes to /joint_states to control the real DexHand
```

Components included in this launch file:
1. **Camera Node**: Captures video input for hand tracking
2. **Hand RPS Estimation**: Detects rock–paper–scissors hand poses
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
camera → hand rps estimation  → rps controller → hand gesture interpreters → urdf visualization + real hand control

Topic flow:
- Camera: publishes /image_raw
- Hand rps estimation: subscribes to /image_raw
  publishes /hand_rps_estimation/bounding_box, /hand_rps_estimation/hand_rps
- Visualization: subscribes to /hand_rps_estimation/bounding_box and publishes visualization markers
- RPS Controller: subscribes to /hand_rps_estimation/hand_rps
  sends action goal to: /execute_gesture/goal
- Hand gesture interpreter:  receives action goal from: /execute_gesture/goal
  publishes /joint_states (alternative control method)
- URDF publishers: subscribe to /joint_states for hand visualization
- Ryuyan RH2 DexHand: Perform message conversion: subscribes to /joint_states, publishes /ryhand6_cmd
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

## License
Apache License 2.0
