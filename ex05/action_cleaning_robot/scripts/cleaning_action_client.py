#!/usr/bin/env python3
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
import sys
import os

try:
    from action_cleaning_robot.action import CleaningTask
    print("SUCCESS: Imported CleaningTask action")
except ImportError as e:
    print(f"ERROR: Could not import CleaningTask: {e}")
    print("Searching for module...")
    for root, dirs, files in os.walk('/home/ezhsluny/ros2_ws/install'):
        if 'action_cleaning_robot' in root and 'rosidl_generator_py' in root:
            print(f"Found module at: {root}")
            sys.path.insert(0, root)
    try:
        from action_cleaning_robot.action import CleaningTask
        print("SUCCESS: Imported after path adjustment")
    except ImportError:
        print("FATAL: Could not import CleaningTask even after path adjustment")
        sys.exit(1)

class CleaningClient(Node):
    def __init__(self):
        super().__init__('cleaning_action_client')
        self._action_client = ActionClient(self, CleaningTask, 'CleaningTask')

    def send_goal(self, task_type, area_size=0.0, target_x=0.0, target_y=0.0):
        goal_msg = CleaningTask.Goal()
        goal_msg.task_type = task_type
        goal_msg.area_size = area_size
        goal_msg.target_x = target_x
        goal_msg.target_y = target_y

        self._action_client.wait_for_server()
        self._send_goal_future = self._action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback)
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected')
            return
        self.get_logger().info('Goal accepted')
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        result = future.result().result
        self.get_logger().info(f'Result: {result.success}, Cleaned Points: {result.cleaned_points}, Total Distance: {result.total_distance:.2f}m')
        rclpy.shutdown()

    def feedback_callback(self, feedback_msg):
        self.get_logger().info(
            f'Progress: {feedback_msg.feedback.progress_percent}%, '
            f'Cleaned Points: {feedback_msg.feedback.current_cleaned_points}, '
            f'Position: ({feedback_msg.feedback.current_x:.2f}, {feedback_msg.feedback.current_y:.2f})')

def main():
    rclpy.init()
    client = CleaningClient()

    # Отправляем задачу на уборку квадрата
    client.send_goal("clean_square", 3.0)

    # Отправляем задачу на возврат домой
    client.send_goal("return_home", 0.0, 5.5, 5.5)

    rclpy.spin(client)

if __name__ == '__main__':
    main()
