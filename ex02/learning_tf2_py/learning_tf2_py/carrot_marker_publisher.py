import rclpy
from rclpy.node import Node
from visualization_msgs.msg import Marker
from geometry_msgs.msg import Point
import math


class CarrotMarkerPublisher(Node):
    def __init__(self):
        super().__init__('carrot_marker_publisher')
        self.marker_pub = self.create_publisher(Marker, '/carrot_marker', 10)
        self.timer = self.create_timer(0.1, self.publish_marker)
        
    def publish_marker(self):
        marker = Marker()
        marker.header.frame_id = "carrot1"
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = "carrot"
        marker.id = 0
        marker.type = Marker.SPHERE
        marker.action = Marker.ADD
        
        # Position (relative to carrot1 frame)
        marker.pose.position.x = 0.0
        marker.pose.position.y = 0.0
        marker.pose.position.z = 0.0
        marker.pose.orientation.x = 0.0
        marker.pose.orientation.y = 0.0
        marker.pose.orientation.z = 0.0
        marker.pose.orientation.w = 1.0
        
        # Size
        marker.scale.x = 0.3
        marker.scale.y = 0.3
        marker.scale.z = 0.3
        
        # Color (orange for carrot)
        marker.color.r = 1.0
        marker.color.g = 0.65
        marker.color.b = 0.0
        marker.color.a = 1.0
        
        self.marker_pub.publish(marker)


def main():
    rclpy.init()
    node = CarrotMarkerPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    rclpy.shutdown()


if __name__ == '__main__':
    main()