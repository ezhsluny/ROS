#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import math

class CircleMovement(Node):
    def __init__(self):
        super().__init__('circle_movement')
        
        # Параметры
        self.declare_parameter('linear_speed', 0.5)
        self.declare_parameter('angular_speed', 0.5)
        self.declare_parameter('radius', 1.0)
        self.declare_parameter('direction_of_rotation', 1.0)  # 1.0 или -1.0
        
        # Получаем параметры
        linear_speed = self.get_parameter('linear_speed').value
        angular_speed = self.get_parameter('angular_speed').value
        radius = self.get_parameter('radius').value
        direction = self.get_parameter('direction_of_rotation').value
        
        # Вычисляем скорости для движения по кругу
        # Для движения по кругу: v = linear_speed, omega = v / r
        self.linear_x = linear_speed
        self.angular_z = direction * (linear_speed / radius) if radius != 0 else 0.0
        
        self.get_logger().info(f'Linear: {self.linear_x}, Angular: {self.angular_z}')
        
        # Издатель
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # Таймер
        timer_period = 0.1  # 10 Hz
        self.timer = self.create_timer(timer_period, self.timer_callback)
        
    def timer_callback(self):
        msg = Twist()
        msg.linear.x = float(self.linear_x)
        msg.angular.z = float(self.angular_z)
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = CircleMovement()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()