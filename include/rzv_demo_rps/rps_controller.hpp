// ********************************************************************************************************************
// Copyright [2025] Renesas Electronics Corporation and/or its licensors. All Rights Reserved.
//
// The contents of this file (the "contents") are proprietary and confidential to Renesas Electronics Corporation
// and/or its licensors ("Renesas") and subject to statutory and contractual protections.
//
// Unless otherwise expressly agreed in writing between Renesas and you: 1) you may not use, copy, modify, distribute,
// display, or perform the contents; 2) you may not use any name or mark of Renesas for advertising or publicity
// purposes or in connection with your use of the contents; 3) RENESAS MAKES NO WARRANTY OR REPRESENTATIONS ABOUT THE
// SUITABILITY OF THE CONTENTS FOR ANY PURPOSE; THE CONTENTS ARE PROVIDED "AS IS" WITHOUT ANY EXPRESS OR IMPLIED
// WARRANTY, INCLUDING THE IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND
// NON-INFRINGEMENT; AND 4) RENESAS SHALL NOT BE LIABLE FOR ANY DIRECT, INDIRECT, SPECIAL, OR CONSEQUENTIAL DAMAGES,
// INCLUDING DAMAGES RESULTING FROM LOSS OF USE, DATA, OR PROJECTS, WHETHER IN AN ACTION OF CONTRACT OR TORT, ARISING
// OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THE CONTENTS. Third-party contents included in this file may
// be subject to different terms.
// ********************************************************************************************************************
#pragma once

#include <yaml-cpp/yaml.h>

#include <chrono>
#include <geometry_msgs/msg/pose_array.hpp>
#include <map>
#include <memory>
#include <random>
#include <rclcpp/rclcpp.hpp>
#include <rclcpp_action/rclcpp_action.hpp>
#include <sensor_msgs/msg/joint_state.hpp>
#include <std_msgs/msg/string.hpp>
#include <string>
#include <vector>

// Include the generated action
#include "arm_hand_control/action/execute_gesture.hpp"
#include "rzv_demo_rps/msg/game_status.hpp"

enum class GameState
{
  READY,
  START,
  WAIT,
  PLAYING,
  RESULT,
};

namespace rzv_demo_rps
{

class RPSGameController : public rclcpp::Node
{
public:
  RPSGameController();
  virtual ~RPSGameController() = default;

private:
  // Action server type definitions
  using ExecuteGesture = arm_hand_control::action::ExecuteGesture;
  using GoalHandleExecuteGesture = rclcpp_action::ClientGoalHandle<ExecuteGesture>;

  // Action server methods
  void send_goal(std::string gesture);
  void feedback_callback(
    GoalHandleExecuteGesture::SharedPtr,
    const std::shared_ptr<const ExecuteGesture::Feedback> feedback);
  void result_callback(const GoalHandleExecuteGesture::WrappedResult & result);

  // ROS communication
  rclcpp_action::Client<ExecuteGesture>::SharedPtr client_ptr_;
  rclcpp::Subscription<std_msgs::msg::String>::SharedPtr hand_pose_trigger_sub_;
  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr user_hand_pose_pub_;
  rclcpp::Publisher<rzv_demo_rps::msg::GameStatus>::SharedPtr game_info_pub_;

  // Timers
  rclcpp::TimerBase::SharedPtr gameplay_timer_;  // control state machine game
  rclcpp::TimerBase::SharedPtr timer_;

  // Rock, Paper, Scissors state machine methods
  std::vector<std::string> signal_start_game();
  void process_gameplay_state();
  void trigger_game_start(const std_msgs::msg::String::SharedPtr msg);
  void handle_start_state();
  void handle_wait_state();
  void handle_playing_state();
  void handle_result_state();

  bool is_valid_rps_pose(const std::string & pose) const;
  void handle_always_win_pose(const std::string & user_pose);
  std::string get_winning_rps_choice(const std::string & user) const;
  std::string determine_winner(std::string user, std::string computer);
  std::string get_random_rps_choice();
  std_msgs::msg::String latest;  // Store the latest detected pose
  std_msgs::msg::String user_choice_;
  std::string computer_choice_;
  bool pose_detected_;
  std::string result_game_;
  bool always_win_mode_;
  std::string last_always_win_robot_choice_;

  //===== Helper function to control state machine =====
  void set_state(GameState state);
  void publish_status(
    const std::string & game_status, const std::string & user_detect,
    const std::string & computer_detect, const std::string & result);
  GameState state_;
  size_t check_count_;
  bool goal_active_;
  bool game_started_;
  std::vector<std::string> gestures_;
  size_t current_gesture_idx_;
  std::chrono::time_point<std::chrono::high_resolution_clock> start_capture_;
  std::chrono::time_point<std::chrono::high_resolution_clock> end_capture_;
};

}  // namespace rzv_demo_rps
