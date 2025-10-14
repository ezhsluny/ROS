#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from action_cleaning_robot.action import CleaningTask
from rclpy.action import ActionClient

class CleaningActionClient(Node):
    def __init__(self):
        super().__init__('cleaning_action_client')
        self._client = ActionClient(self, CleaningTask, 'CleaningTask')

    def send_goal(self, task_type, area_size=0.0, target_x=0.0, target_y=0.0):
        goal_message = CleaningTask.Goal()
        goal_message.task_type = task_type
        goal_message.area_size = area_size
        goal_message.target_x = target_x
        goal_message.target_y = target_y

        self._client.wait_for_server()

        self._goal_future = self._client.send_goal_async(goal_message, feedback_callback=self.feedback_handler)
        self._goal_future.add_done_callback(self.response_handler)

    def response_handler(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal request was rejected!')
            return
        self.get_logger().info('Goal request accepted successfully')

        self._result_future = goal_handle.get_result_async()
        self._result_future.add_done_callback(self.result_handler)

    def feedback_handler(self, feedback_msg):
        feedback_data = feedback_msg.feedback
        self.get_logger().info(f'Current progress: {feedback_data.progress_percent}%, ' +
                               f'Areas cleaned: {feedback_data.current_cleaned_points}, ' +
                               f'Current position: ({feedback_data.current_x:.2f}, {feedback_data.current_y:.2f})')

    def result_handler(self, future):
        result_data = future.result().result
        self.get_logger().info(f'Task completed - success: {result_data.success}, points cleaned: {result_data.cleaned_points}')
        rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)
    action_client = CleaningActionClient()

    action_client.send_goal('clean_square', area_size=1.0)

    rclpy.spin(action_client)


if __name__ == '__main__':
    main()