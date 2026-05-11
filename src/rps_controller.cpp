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
#include "rzv_demo_rps/rps_controller.hpp"

#include <ament_index_cpp/get_package_share_directory.hpp>
#include <boost/algorithm/string.hpp>
#include <chrono>
#include <filesystem>
#include <functional>
#include <thread>

using std::placeholders::_1;
namespace rzv_demo_rps
{
RPSGameController::RPSGameController()
: Node("rps_game_controller"),
  pose_detected_(false),
  always_win_mode_(false),
  state_(GameState::READY),
  check_count_(0),
  goal_active_(false),
  game_started_(false),
  current_gesture_idx_(0)
{
  always_win_mode_ = this->declare_parameter<bool>("always_win_mode", false);

  auto qos = rclcpp::QoS(rclcpp::KeepLast(1)).best_effort().durability_volatile();

  hand_pose_trigger_sub_ = create_subscription<std_msgs::msg::String>(
    "hand_pose", qos, std::bind(&RPSGameController::trigger_game_start, this, _1));

  client_ptr_ = rclcpp_action::create_client<ExecuteGesture>(this, "execute_gesture");

  game_info_pub_ = this->create_publisher<rzv_demo_rps::msg::GameStatus>("game_status", 10);

  // Publish initial status
  publish_status(always_win_mode_ ? "ALWAYS_WIN" : "Ready", "-", "-", "-");
}

// Publish game status
void RPSGameController::publish_status(
  const std::string & game_status, const std::string & user_detect,
  const std::string & computer_detect, const std::string & result)
{
  RCLCPP_INFO(this->get_logger(), "Publish status");
  auto msg = rzv_demo_rps::msg::GameStatus();
  msg.game_status = game_status;
  msg.user_detect = user_detect;
  msg.computer_detect = computer_detect;
  msg.result = result;

  game_info_pub_->publish(msg);
}

// ===== RPS STATE =====

// State: IDLE
//    Handle the "scissor" gesture to trigger game start.
//    Start gameplay timer to control the state machine.
void RPSGameController::trigger_game_start(const std_msgs::msg::String::SharedPtr msg)
{
  // Trim the incoming message
  std::string data = boost::algorithm::trim_copy(msg->data);
  if (!is_valid_rps_pose(data)) {
    return;
  }

  if (always_win_mode_) {
    handle_always_win_pose(data);
    return;
  }

  RCLCPP_INFO(this->get_logger(), "Detected valid pose: %s", data.c_str());

  // Store the user choice
  latest.data = data;
  start_capture_ = std::chrono::high_resolution_clock::now();

  // Check if the game has started
  if (!game_started_) {
    // Use "scissor" gesture to signal the start of the game
    // scissor for signal startgame
    if (data == "scissor") {
      // Start timer to drive state machine transitions during gameplay
      gameplay_timer_ = this->create_wall_timer(
        std::chrono::milliseconds(100),
        std::bind(&RPSGameController::process_gameplay_state, this));

      // Switch state machine to START
      RCLCPP_INFO(this->get_logger(), "Game started");
      set_state(GameState::START);
      publish_status("PLAYING", "-", "-", "-");
      game_started_ = true;
      gestures_.clear();
    }
  }
}

bool RPSGameController::is_valid_rps_pose(const std::string & pose) const
{
  return pose == "rock" || pose == "paper" || pose == "scissor";
}

std::string RPSGameController::get_winning_rps_choice(const std::string & user) const
{
  if (user == "rock") {
    return "paper";
  }
  if (user == "paper") {
    return "scissor";
  }
  if (user == "scissor") {
    return "rock";
  }
  return "";
}

void RPSGameController::handle_always_win_pose(const std::string & user_pose)
{
  const std::string robot_choice = get_winning_rps_choice(user_pose);
  if (robot_choice.empty()) {
    return;
  }

  if (goal_active_) {
    RCLCPP_DEBUG_THROTTLE(
      this->get_logger(), *this->get_clock(), 500,
      "Skipping always-win update while a gesture is still executing");
    return;
  }

  if (robot_choice == last_always_win_robot_choice_) {
    return;
  }

  user_choice_.data = user_pose;
  computer_choice_ = robot_choice;
  result_game_ = "victory";

  RCLCPP_INFO(
    this->get_logger(), "Always-win response: user=%s robot=%s", user_choice_.data.c_str(),
    computer_choice_.c_str());

  publish_status("ALWAYS_WIN", user_choice_.data, computer_choice_, result_game_);
  send_goal(computer_choice_);
  last_always_win_robot_choice_ = computer_choice_;
}

// State:: START
//    Check for user pose with 2s timeout.
//    If no pose is detected within timeout, cancel the game.
std::vector<std::string> RPSGameController::signal_start_game()
{
  return {
    // Counting gestures
    "loose_fist", "one", "two", "three", "loose_fist"};
}

//    Handle the "scissor" gesture to trigger game start.
//    Start gameplay timer to control the state machine.
void RPSGameController::handle_start_state()
{
  // Set goal to "start game" and wait until it finishes
  // Initialize gestures if not already
  if (gestures_.empty()) {
    gestures_ = signal_start_game();
    current_gesture_idx_ = 0;
  }

  // If no goal is currently active → send next gesture
  if (!goal_active_) {
    auto current_gesture = gestures_[current_gesture_idx_];
    RCLCPP_INFO(this->get_logger(), "Preparing the game: %s", current_gesture.c_str());

    send_goal(current_gesture);
    current_gesture_idx_++;
  }
  // finish signal start game move to next state
  if (current_gesture_idx_ >= gestures_.size()) {
    RCLCPP_INFO(this->get_logger(), "Game prepare complete, moving to next stage");

    // Transition to WAIT state for user pose
    set_state(GameState::PLAYING);

    // 20 × 100 ms = 2000 ms (2 seconds)
    check_count_ = 20;

    // Reset flags
    pose_detected_ = false;
    user_choice_ = std_msgs::msg::String();  // Reset user choice
    computer_choice_ = std::string();
  }
}

// State:: PLAYING
//    Get a random choice for the opponent and determine game result
void RPSGameController::handle_playing_state()
{
  // Wait for the goal to finish
  if (goal_active_) return;

  // Get random choice for computer
  computer_choice_ = get_random_rps_choice();
  RCLCPP_INFO(this->get_logger(), "Computer choice: %s", computer_choice_.c_str());

  //send goal to action
  send_goal(computer_choice_);

  // Transition to WAIT state
  set_state(GameState::WAIT);
}

// State:: WAIT
//    Check for user pose with 2s timeout.
//    If no pose is detected within timeout, cancel the game.
void RPSGameController::handle_wait_state()
{
  // if (goal_active_) return;
  RCLCPP_DEBUG(this->get_logger(), "Waiting for user pose (2s)...");

  // Decrement countdown timer (100 ms per step)
  if (check_count_ > 0) {
    --check_count_;
  }

  // Timeout check
  if (check_count_ == 0 && !pose_detected_) {
    RCLCPP_WARN(this->get_logger(), "Timeout waiting for valid hand pose.");
    user_choice_.data = "unknown";
    result_game_ = "unknown";
    set_state(GameState::RESULT);
    publish_status("PLAYING", user_choice_.data, computer_choice_, "TIMEOUT");
    return;
  }

  // No pose detected yet
  if (latest.data.empty()) {
    RCLCPP_DEBUG(this->get_logger(), "No valid pose detected yet.");
    return;
  }

  // Check timing of latest pose
  end_capture_ = std::chrono::high_resolution_clock::now();
  auto elapsed_ms =
    std::chrono::duration_cast<std::chrono::milliseconds>(end_capture_ - start_capture_).count();

  if (elapsed_ms <= 200) {
    RCLCPP_INFO(this->get_logger(), "User choice detected within 500ms");
    user_choice_.data = latest.data;
    pose_detected_ = true;

    // Determine winner
    result_game_ = determine_winner(user_choice_.data, computer_choice_);
    RCLCPP_INFO(this->get_logger(), "Game result: %s", result_game_.c_str());
    set_state(GameState::RESULT);
    publish_status("PLAYING", user_choice_.data, computer_choice_, result_game_);
  }
}

// State:: RESULT
//    Get a random choice for the opponent and determine game result
void RPSGameController::handle_result_state()
{
  if (result_game_ == "unknown") {
    RCLCPP_DEBUG(this->get_logger(), "No valid pose detected. Round skipped.");
    set_state(GameState::READY);
    return;
  }
  if (result_game_ == "ok") {
    RCLCPP_DEBUG(this->get_logger(), "It's a draw!");
  } else if (result_game_ == "victory") {
    RCLCPP_DEBUG(this->get_logger(), "Computer win! ");
  } else if (result_game_ == "thumbs_up") {
    RCLCPP_DEBUG(this->get_logger(), "You wins! ");
  }
  if (!goal_active_) {
    rclcpp::sleep_for(std::chrono::seconds(1));

    send_goal(result_game_);
    // Transition to READY state
    set_state(GameState::READY);
  }
}

// Get a random RPS choice
std::string RPSGameController::get_random_rps_choice()
{
  static const std::vector<std::string> choices = {"rock", "paper", "scissor"};

  static std::random_device rd;
  static std::mt19937 gen(rd());
  std::uniform_int_distribution<> dist(0, choices.size() - 1);

  return choices[dist(gen)];
}

// Determine the winner of the game
std::string RPSGameController::determine_winner(std::string user, std::string computer)
{
  if (user == computer) return "ok";

  if (
    (user == "rock" && computer == "scissor") || (user == "paper" && computer == "rock") ||
    (user == "scissor" && computer == "paper")) {
    return "thumbs_up";
  }

  return "victory";
}

//===== Helper function to control state machine =====
void RPSGameController::set_state(GameState state) { state_ = state; }

void RPSGameController::process_gameplay_state()
{
  switch (state_) {
    case GameState::START:
      handle_start_state();
      break;

    case GameState::PLAYING:
      handle_playing_state();
      break;

    case GameState::WAIT:
      handle_wait_state();
      break;

    case GameState::RESULT:
      handle_result_state();
      break;
    case GameState::READY:
      gameplay_timer_->cancel();  // Stop timer safely
      game_started_ = false;

      rclcpp::sleep_for(std::chrono::seconds(3));  // wait for a while before resetting the game
      publish_status("READY", "-", "-", "-");
      RCLCPP_INFO(this->get_logger(), "Game reset after 3 seconds");
      break;
    default:
      RCLCPP_ERROR(get_logger(), "Invalid game state!");
      break;
  }
}

//===== Action Server Methods =====
void RPSGameController::send_goal(std::string gesture)
{
  if (!this->client_ptr_->wait_for_action_server(std::chrono::seconds(10))) {
    RCLCPP_INFO(this->get_logger(), "Action server not available");
    rclcpp::shutdown();
    return;
  }
  auto goal_msg = ExecuteGesture::Goal();

  // Map RPS gestures to robot gestures
  if (gesture == "rock") {
    goal_msg.gesture_name = "fist_bump";
  } else if (gesture == "scissor") {
    goal_msg.gesture_name = "peace";
  } else if (gesture == "paper") {
    goal_msg.gesture_name = "five";
  } else if (gesture == "victory") {
    goal_msg.gesture_name = "spider_man";
  } else {
    goal_msg.gesture_name = gesture;
  }

  goal_active_ = true;
  RCLCPP_INFO(this->get_logger(), "Sending goal: %s", goal_msg.gesture_name.c_str());

  auto send_goal_options = rclcpp_action::Client<ExecuteGesture>::SendGoalOptions();
  send_goal_options.feedback_callback = std::bind(
    &RPSGameController::feedback_callback, this, std::placeholders::_1, std::placeholders::_2);
  send_goal_options.result_callback =
    std::bind(&RPSGameController::result_callback, this, std::placeholders::_1);

  auto goal_handle_future = this->client_ptr_->async_send_goal(goal_msg, send_goal_options);
}

void RPSGameController::feedback_callback(
  GoalHandleExecuteGesture::SharedPtr,
  const std::shared_ptr<const ExecuteGesture::Feedback> feedback)
{
  std::stringstream ss;
  ss << "Gesture completion: " << static_cast<int>(feedback->percentage_complete * 100.0) << "%";
  RCLCPP_DEBUG(this->get_logger(), "%s", ss.str().c_str());
}

void RPSGameController::result_callback(const GoalHandleExecuteGesture::WrappedResult & result)
{
  switch (result.code) {
    case rclcpp_action::ResultCode::SUCCEEDED:
      goal_active_ = false;  // goal finished
      RCLCPP_INFO(this->get_logger(), "Goal was finished");
      break;
    case rclcpp_action::ResultCode::ABORTED:
      goal_active_ = false;
      last_always_win_robot_choice_.clear();
      RCLCPP_ERROR(this->get_logger(), "Goal was aborted");
      break;
    case rclcpp_action::ResultCode::CANCELED:
      goal_active_ = false;
      last_always_win_robot_choice_.clear();
      RCLCPP_ERROR(this->get_logger(), "Goal was canceled");
      break;
    default:
      goal_active_ = false;
      last_always_win_robot_choice_.clear();
      RCLCPP_ERROR(this->get_logger(), "Unknown result code");
      break;
  }
}
};  // namespace rzv_demo_rps

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<rzv_demo_rps::RPSGameController>());
  rclcpp::shutdown();
  return 0;
}
