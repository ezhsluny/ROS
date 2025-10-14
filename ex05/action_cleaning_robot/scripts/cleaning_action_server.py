#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from rclpy.action import ActionServer
import math

from action_cleaning_robot.action import CleaningTask

class CleaningActionServer(Node):
    def __init__(self):
        super().__init__('cleaning_action_server')
        self._action_server = ActionServer(
            self,
            CleaningTask,
            'CleaningTask',
            self.processing_callback)
        self.current_pose = None
        self.velocity_publisher = self.create_publisher(Twist, 'turtle1/cmd_vel', 10)
        self.pose_subscriber = self.create_subscription(Pose, 'turtle1/pose', self.pose_update, 10)
        self.get_logger().info('Cleaning Action Server initialized and running')

    def pose_update(self, msg):
        self.current_pose = msg

    def adjust_angle(self, angle):
        while angle > math.pi:
            angle -= 2 * math.pi
        while angle < -math.pi:
            angle += 2 * math.pi
        return angle

    def processing_callback(self, goal_handle):
        while self.current_pose is None and rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0.1)
        start_position_x = self.current_pose.x
        start_position_y = self.current_pose.y
        start_angle = self.current_pose.theta

        velocity_command = Twist()
        movement_speed = 1.0
        rotation_speed = 2.0
        cleaning_resolution = 0.03

        def rotate_to_desired_angle(target_angle):
            while rclpy.ok():
                angle_difference = self.adjust_angle(target_angle - self.current_pose.theta)
                if abs(angle_difference) > 0.01:
                    velocity_command.linear.x = 0.0
                    velocity_command.angular.z = rotation_speed * angle_difference
                else:
                    velocity_command.linear.x = 0.0
                    velocity_command.angular.z = 0.0
                    self.velocity_publisher.publish(velocity_command)
                    break
                self.velocity_publisher.publish(velocity_command)
                rclpy.spin_once(self, timeout_sec=0.01)

        def navigate_to_destination(target_x, target_y):
            delta_x = target_x - self.current_pose.x
            delta_y = target_y - self.current_pose.y
            desired_angle = math.atan2(delta_y, delta_x)
            rotate_to_desired_angle(desired_angle)
            while rclpy.ok():
                distance = math.hypot(self.current_pose.x - target_x, self.current_pose.y - target_y)
                if distance > 0.015:
                    direction = math.atan2(target_y - self.current_pose.y, target_x - self.current_pose.x)
                    angle_error = self.adjust_angle(direction - self.current_pose.theta)
                    velocity_command.linear.x = movement_speed
                    velocity_command.angular.z = rotation_speed * angle_error
                else:
                    velocity_command.linear.x = 0.0
                    velocity_command.angular.z = 0.0
                    self.velocity_publisher.publish(velocity_command)
                    break
                self.velocity_publisher.publish(velocity_command)
                rclpy.spin_once(self, timeout_sec=0.01)

        processed_areas = 0
        cleaning_size = goal_handle.request.area_size
        operation_mode = goal_handle.request.task_type
        final_result = CleaningTask.Result()

        if operation_mode == "clean_square":
            if cleaning_size <= 0.1:
                goal_handle.abort()
                self.get_logger().info('Invalid cleaning area size provided')
                final_result.success = False
                return final_result

            cleaning_lines = int(cleaning_size / cleaning_resolution)
            for line_index in range(cleaning_lines + 1):
                current_y = start_position_y + line_index * cleaning_resolution
                if current_y > start_position_y + cleaning_size:
                    break
                if line_index % 2 == 0:
                    navigate_to_destination(start_position_x + cleaning_size, current_y)
                else:
                    navigate_to_destination(start_position_x, current_y)
                processed_areas += 1
                completion_percentage = int((line_index + 1) / (cleaning_lines + 1) * 100)
                goal_handle.publish_feedback(CleaningTask.Feedback(
                    progress_percent=completion_percentage,
                    current_cleaned_points=processed_areas,
                    current_x=self.current_pose.x,
                    current_y=self.current_pose.y
                ))

            velocity_command.linear.x = 0.0
            velocity_command.angular.z = 0.0
            self.velocity_publisher.publish(velocity_command)

            navigate_to_destination(start_position_x, start_position_y)
            rotate_to_desired_angle(start_angle)
            velocity_command.linear.x = 0.0
            velocity_command.angular.z = 0.0
            self.velocity_publisher.publish(velocity_command)

            final_result.success = True
            final_result.cleaned_points = processed_areas
            final_result.total_distance = cleaning_size * cleaning_lines
            goal_handle.succeed()
            return final_result

        elif operation_mode == "return_home":
            home_position_x = goal_handle.request.target_x
            home_position_y = goal_handle.request.target_y
            navigate_to_destination(home_position_x, home_position_y)
            rotate_to_desired_angle(start_angle)
            velocity_command.linear.x = 0.0
            velocity_command.angular.z = 0.0
            self.velocity_publisher.publish(velocity_command)

            final_result.success = True
            final_result.cleaned_points = 0
            final_result.total_distance = math.hypot(self.current_pose.x - home_position_x, self.current_pose.y - home_position_y)
            goal_handle.succeed()

            goal_handle.publish_feedback(CleaningTask.Feedback(
                progress_percent=100,
                current_cleaned_points=0,
                current_x=self.current_pose.x,
                current_y=self.current_pose.y
            ))

            return final_result

        else:
            self.get_logger().info('Unknown operation mode specified')
            goal_handle.abort()
            final_result.success = False
            return final_result

def main(args=None):
    rclpy.init(args=args)
    action_server = CleaningActionServer()
    rclpy.spin(action_server)
    rclpy.shutdown()

if __name__ == '__main__':
    main()