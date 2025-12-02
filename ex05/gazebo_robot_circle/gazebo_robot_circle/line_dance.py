#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import math


class DanceLineMovement(Node):
    def __init__(self):
        super().__init__('dance_line_movement')
        
        # Параметры
        self.declare_parameter('forward_distance', 3.0)  # расстояние вперед в метрах
        self.declare_parameter('backward_distance', 3.0)  # расстояние назад в метрах
        self.declare_parameter('linear_speed', 0.4)  # скорость движения вперед/назад
        self.declare_parameter('rotation_speed', 0.5)  # скорость вращения для танца
        self.declare_parameter('dance_cycles', 3)  # количество циклов танца
        self.declare_parameter('dance_angle', math.radians(60))  # угол вращения
        
        self.forward_distance = self.get_parameter('forward_distance').value
        self.backward_distance = self.get_parameter('backward_distance').value
        self.linear_speed = self.get_parameter('linear_speed').value
        self.rotation_speed = self.get_parameter('rotation_speed').value
        self.dance_cycles = int(self.get_parameter('dance_cycles').value)
        self.dance_angle = math.radians(self.get_parameter('dance_angle').value)
        
        self.state = "INIT"
        self.phase = 0  # 0=вперед, 1=танец, 2=разворот, 3=назад, 4=танец
        self.last_time = self.get_clock().now()
        self.start_time = self.get_clock().now()
        
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        
        timer_period = 0.05
        self.timer = self.create_timer(timer_period, self.state_machine_callback)
        
        self.get_logger().info(f"Starting dance line movement:")
        self.get_logger().info(f"  Forward distance: {self.forward_distance} m")
        self.get_logger().info(f"  Backward distance: {self.backward_distance} m")
        self.get_logger().info(f"  Linear speed: {self.linear_speed} m/s")
        self.get_logger().info(f"  Dance cycles: {self.dance_cycles}")
        self.get_logger().info(f"  Dance angle: {math.degrees(self.dance_angle):.1f}°")
        
    def state_machine_callback(self):
        current_time = self.get_clock().now()
        elapsed = (current_time - self.last_time).nanoseconds / 1e9
        total_elapsed = (current_time - self.start_time).nanoseconds / 1e9
        
        msg = Twist()
        
        if self.state == "INIT":
            if elapsed > 0.2:
                self.state = "MOVE_FORWARD"
                self.phase = 0
                self.last_time = current_time
                self.start_time = current_time
                self.get_logger().info("Starting forward movement...")
        
        elif self.state == "MOVE_FORWARD":
            msg.linear.x = self.linear_speed
            self.publisher_.publish(msg)
            
            forward_time = self.forward_distance / self.linear_speed
            
            if total_elapsed >= forward_time:
                self.state = "DANCE"
                self.last_time = current_time
                self.start_time = current_time
                self.phase = 1
                self.get_logger().info("Reached point, starting dance...")

                stop_msg = Twist()
                self.publisher_.publish(stop_msg)
        
        elif self.state == "DANCE":
            dance_cycle_duration = (2 * self.dance_angle) / self.rotation_speed
            total_dance_duration = self.dance_cycles * dance_cycle_duration
            
            if total_elapsed < total_dance_duration:
                cycle_time = total_elapsed % dance_cycle_duration
                
                if cycle_time < (self.dance_angle / self.rotation_speed):
                    # Поворот в одну сторону
                    msg.angular.z = self.rotation_speed
                else:
                    # Поворот в другую сторону
                    msg.angular.z = -self.rotation_speed
            else:
                if self.phase == 1:
                    self.state = "TURN_AROUND"
                    self.last_time = current_time
                    self.start_time = current_time
                    self.get_logger().info("Dance completed, turning around...")
                else:
                    self.state = "COMPLETE"
                    self.last_time = current_time
                    self.start_time = current_time
                    self.get_logger().info("Final dance completed!")
                
                stop_msg = Twist()
                self.publisher_.publish(stop_msg)
            
            self.publisher_.publish(msg)
        
        elif self.state == "TURN_AROUND":
            msg.angular.z = self.rotation_speed
            self.publisher_.publish(msg)
            
            turn_time = math.pi / self.rotation_speed
            
            if total_elapsed >= turn_time:
                self.state = "MOVE_BACKWARD"
                self.last_time = current_time
                self.start_time = current_time
                self.phase = 3
                self.get_logger().info("Turn completed, moving backward...")

                stop_msg = Twist()
                self.publisher_.publish(stop_msg)
        
        elif self.state == "MOVE_BACKWARD":
            msg.linear.x = -self.linear_speed
            self.publisher_.publish(msg)
            
            backward_time = self.backward_distance / self.linear_speed
            
            if total_elapsed >= backward_time:
                self.state = "DANCE"
                self.last_time = current_time
                self.start_time = current_time
                self.phase = 4
                self.get_logger().info("Reached starting point, starting final dance...")

                stop_msg = Twist()
                self.publisher_.publish(stop_msg)
        
        elif self.state == "COMPLETE":
            # Остановка и пауза перед началом нового цикла
            msg.linear.x = 0.0
            msg.angular.z = 0.0
            self.publisher_.publish(msg)
            
            if total_elapsed > 0.2:
                # Начинаем новый цикл
                self.state = "INIT"
                self.last_time = current_time
                self.start_time = current_time
                self.get_logger().info("Starting new cycle...")
        
        else:
            # Неизвестное состояние
            self.state = "INIT"
            self.last_time = current_time
            self.start_time = current_time


def main(args=None):
    rclpy.init(args=args)
    node = DanceLineMovement()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Keyboard interrupt, shutting down...')
    finally:
        msg = Twist()
        node.publisher_.publish(msg)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()