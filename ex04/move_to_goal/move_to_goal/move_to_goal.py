#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
import math
import sys

class MoveToGoal(Node):
    def __init__(self, target_x, target_y, target_theta):
        super().__init__('move_to_goal')
        
        self.target_x = target_x
        self.target_y = target_y
        self.target_theta = target_theta
        
        self.current_pose = None
        self.pose_subscription = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10)
        
        self.cmd_vel_publisher = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10)
        
        self.timer = self.create_timer(0.1, self.control_loop)
        
        self.get_logger().info(f'Moving turtle to goal: ({target_x}, {target_y}, {target_theta})')
        
    def pose_callback(self, msg):
        self.current_pose = msg
        
    def control_loop(self):
        if self.current_pose is None:
            return
            
        # Calculate distance to target
        dx = self.target_x - self.current_pose.x
        dy = self.target_y - self.current_pose.y
        distance = math.sqrt(dx**2 + dy**2)
        
        # Calculate angle to target
        target_angle = math.atan2(dy, dx)
        angle_error = target_angle - self.current_pose.theta
        
        # Normalize angle error to [-pi, pi]
        while angle_error > math.pi:
            angle_error -= 2 * math.pi
        while angle_error < -math.pi:
            angle_error += 2 * math.pi
            
        # Calculate final orientation error
        final_angle_error = self.target_theta - self.current_pose.theta
        while final_angle_error > math.pi:
            final_angle_error -= 2 * math.pi
        while final_angle_error < -math.pi:
            final_angle_error += 2 * math.pi
        
        cmd_vel = Twist()
        
        # Control logic
        if distance > 0.1:  # If far from target position
            # First, align with target
            if abs(angle_error) > 0.1:
                cmd_vel.angular.z = 0.5 * angle_error
            else:
                # Move forward while maintaining orientation
                cmd_vel.linear.x = 0.5 * distance
                cmd_vel.angular.z = 0.3 * angle_error
        else:  # If close to target position, adjust final orientation
            if abs(final_angle_error) > 0.05:
                cmd_vel.angular.z = 0.5 * final_angle_error
            else:
                cmd_vel.linear.x = 0.0
                cmd_vel.angular.z = 0.0
                self.get_logger().info('Goal reached!')
                self.timer.cancel()
                
        # Limit velocities
        cmd_vel.linear.x = max(min(cmd_vel.linear.x, 2.0), -2.0)
        cmd_vel.angular.z = max(min(cmd_vel.angular.z, 2.0), -2.0)
        
        self.cmd_vel_publisher.publish(cmd_vel)

def main(args=None):
    rclpy.init(args=args)
    
    if len(sys.argv) != 4:
        print("Usage: ros2 run move_to_goal_pkg move_to_goal_node <x> <y> <theta>")
        return
        
    try:
        target_x = float(sys.argv[1])
        target_y = float(sys.argv[2])
        target_theta = float(sys.argv[3])
    except ValueError:
        print("Error: All parameters must be numbers")
        return
        
    move_to_goal = MoveToGoal(target_x, target_y, target_theta)
    
    try:
        rclpy.spin(move_to_goal)
    except KeyboardInterrupt:
        pass
    finally:
        # Stop the turtle before exiting
        stop_cmd = Twist()
        move_to_goal.cmd_vel_publisher.publish(stop_cmd)
        move_to_goal.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
