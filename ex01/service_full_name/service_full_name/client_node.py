#!/usr/bin/env python3

import sys
import rclpy
from rclpy.node import Node
from full_name_pkg.srv import FullNameSumService

class FullNameClient(Node):
    def __init__(self, last_name, name, first_name):
        super().__init__('client_name')
        self.client = self.create_client(FullNameSumService, 'SummFullName')
        self.last_name = last_name
        self.name = name
        self.first_name = first_name
        
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service SummFullName not available, waiting...')
        
        self.send_request()

    def send_request(self):
        request = FullNameSumService.Request()
        request.last_name = self.last_name
        request.name = self.name
        request.first_name = self.first_name
        
        self.get_logger().info(
            f'Sending request to SummFullName service:\n'
            f'  Last name: {self.last_name}\n'
            f'  Name: {self.name}\n'
            f'  First name: {self.first_name}'
        )
        
        self.future = self.client.call_async(request)
        self.future.add_done_callback(self.service_callback)

    def service_callback(self, future):
        try:
            response = future.result()
            self.get_logger().info(
                f'Service call successful!\n'
                f'Generated full name: "{response.full_name}"'
            )
        except Exception as e:
            self.get_logger().error(f'Service call failed: {e}')

def main():
    rclpy.init()
    
    # Check command line arguments
    if len(sys.argv) != 4:
        print('Usage: ros2 run full_name_pkg client_name <last_name> <name> <first_name>')
        print('Example: ros2 run full_name_pkg client_name Иванов Иван Иванович')
        return 1
    
    last_name = sys.argv[1]
    name = sys.argv[2]
    first_name = sys.argv[3]
    
    client = FullNameClient(last_name, name, first_name)
    
    try:
        rclpy.spin(client)
    except KeyboardInterrupt:
        pass
    finally:
        client.destroy_node()
        rclpy.shutdown()
    
    return 0

if __name__ == '__main__':
    main()
