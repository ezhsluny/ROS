#!/usr/bin/env python3
import rclpy
from rclpy.action import ActionServer
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose as TurtlePose
import math
import time
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
        sys.exit()

class CleaningServer(Node):
    def __init__(self):
        super().__init__('cleaning_action_server')

        # Публикатор для управления черепахой
        self.cmd_vel_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)

        # Подписчик для получения позиции черепахи
        self.pose_subscriber = self.create_subscription(
            TurtlePose, '/turtle1/pose', self.pose_callback, 10)

        # Action сервер
        self._action_server = ActionServer(
            self,
            CleaningTask,
            'CleaningTask',
            self.execute_callback)

        self.current_pose = None
        self.get_logger().info('Cleaning Action Server started')

    def pose_callback(self, msg):
        """Обновляем текущую позицию черепахи"""
        self.current_pose = msg

    def execute_callback(self, goal_handle):
        self.get_logger().info(f'Executing goal: {goal_handle.request.task_type}')

        # Ждем данные о позиции
        while self.current_pose is None:
            self.get_logger().info('Waiting for pose data...')
            time.sleep(0.1)

        result = CleaningTask.Result()
        feedback_msg = CleaningTask.Feedback()

        if goal_handle.request.task_type == "clean_square":
            self.get_logger().info(f'Cleaning square {goal_handle.request.area_size}x{goal_handle.request.area_size}m')
            success, cleaned_points, total_distance = self.clean_square_proper(
                goal_handle, feedback_msg, goal_handle.request.area_size)

        elif goal_handle.request.task_type == "return_home":
            self.get_logger().info(f'Returning home to ({goal_handle.request.target_x}, {goal_handle.request.target_y})')
            success, cleaned_points, total_distance = self.return_home_proper(
                goal_handle, feedback_msg,
                goal_handle.request.target_x, goal_handle.request.target_y)

        else:
            self.get_logger().error(f'Unknown task type: {goal_handle.request.task_type}')
            success = False
            cleaned_points = 0
            total_distance = 0.0

        result.success = success
        result.cleaned_points = cleaned_points
        result.total_distance = total_distance

        if success:
            self.get_logger().info(f'Task completed! Points: {cleaned_points}, Distance: {total_distance:.2f}m')
        else:
            self.get_logger().error('Task failed!')

        goal_handle.succeed()
        return result

    def clean_square_proper(self, goal_handle, feedback_msg, side_length):
        """Уборка квадратной области"""
        print("=== STARTING SQUARE MOVEMENT ===")
        print(f"Square size: {side_length}x{side_length}m")

        cleaned_points = 0
        total_distance = 0.0

        for side in range(4):
            if goal_handle.is_cancel_requested:
                self.get_logger().info('Goal canceled')
                return False, cleaned_points, total_distance

            print(f"Side {side + 1}/4: Moving forward {side_length}m")

            distance_moved = self.move_straight_distance(side_length)
            total_distance += distance_moved

            if side < 3:
                print(f"Turning 90 degrees at corner {side + 1}")
                self.turn_degrees(90)

            cleaned_points += 1

            progress = int((side + 1) / 4 * 100)
            feedback_msg.progress_percent = progress
            feedback_msg.current_cleaned_points = cleaned_points
            if self.current_pose:
                feedback_msg.current_x = self.current_pose.x
                feedback_msg.current_y = self.current_pose.y
            goal_handle.publish_feedback(feedback_msg)

            print(f'Square progress: {progress}% - Side: {side + 1}/4 completed')

        print("SQUARE COMPLETED: 4 sides, 3 turns (90 degrees each)")
        return True, cleaned_points, total_distance

    def return_home_proper(self, goal_handle, feedback_msg, home_x, home_y):
        """Возврат в начальную точку"""
        print("=== STARTING RETURN HOME ===")
        print(f"Target: ({home_x}, {home_y})")

        cleaned_points = 0
        total_distance = 0.0

        if not self.current_pose:
            self.get_logger().error('No pose data available')
            return False, 0, 0.0

        current_x = self.current_pose.x
        current_y = self.current_pose.y

        dx = home_x - current_x
        dy = home_y - current_y
        distance_to_home = math.sqrt(dx**2 + dy**2)
        target_angle = math.atan2(dy, dx)

        print(f"Current position: ({current_x:.2f}, {current_y:.2f})")
        print(f"Distance to home: {distance_to_home:.2f}m")
        print(f"Target angle: {math.degrees(target_angle):.1f} degrees")

        self.turn_to_angle(target_angle)

        distance_moved = self.move_straight_distance(distance_to_home)
        total_distance += distance_moved

        cleaned_points = 3

        feedback_msg.progress_percent = 100
        feedback_msg.current_cleaned_points = cleaned_points
        if self.current_pose:
            feedback_msg.current_x = self.current_pose.x
            feedback_msg.current_y = self.current_pose.y
        goal_handle.publish_feedback(feedback_msg)

        print("RETURN HOME COMPLETED")
        return True, cleaned_points, total_distance

    def move_straight_distance(self, distance, speed=1.0):
        """Движение прямо на указанное расстояние"""
        print(f"Moving straight: {distance}m at {speed}m/s")

        twist = Twist()
        twist.linear.x = speed

        move_time = distance / speed
        start_time = time.time()

        while time.time() - start_time < move_time:
            self.cmd_vel_pub.publish(twist)
            time.sleep(0.1)

        twist.linear.x = 0.0
        self.cmd_vel_pub.publish(twist)
        time.sleep(0.5)

        print(f"Movement completed: {distance}m")
        return distance

    def turn_degrees(self, degrees, speed=1.0):
        """Поворот на указанное количество градусов"""
        print(f"Turning: {degrees} degrees at {speed}rad/s")

        twist = Twist()
        twist.angular.z = speed if degrees > 0 else -speed

        turn_time = abs(degrees) * (math.pi / 180) / speed
        start_time = time.time()

        while time.time() - start_time < turn_time:
            self.cmd_vel_pub.publish(twist)
            time.sleep(0.1)

        twist.angular.z = 0.0
        self.cmd_vel_pub.publish(twist)
        time.sleep(0.5)

        print(f"Turn completed: {degrees} degrees")

    def turn_to_angle(self, target_angle_rad):
        """Поворот к указанному углу (в радианах)"""
        if not self.current_pose:
            return

        current_angle = self.current_pose.theta
        angle_diff = target_angle_rad - current_angle

        while angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        while angle_diff < -math.pi:
            angle_diff += 2 * math.pi

        print(f"Turning from {math.degrees(current_angle):.1f} to {math.degrees(target_angle_rad):.1f} degrees")
        print(f"Angle difference: {math.degrees(angle_diff):.1f} degrees")

        self.turn_degrees(math.degrees(angle_diff))

def main():
    rclpy.init()
    server = CleaningServer()

    try:
        rclpy.spin(server)
    except KeyboardInterrupt:
        print('Server stopped by user')
    finally:
        server.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
