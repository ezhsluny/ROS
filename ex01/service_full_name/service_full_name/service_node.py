#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from full_name_pkg.srv import FullNameSumService

class FullNameService(Node):
    def __init__(self):
        super().__init__('service_name')
        self.srv = self.create_service(
            FullNameSumService, 
            'SummFullName', 
            self.full_name_callback
        )
        self.get_logger().info('Service SummFullName is ready and waiting for requests...')

    def full_name_callback(self, request, response):
        full_name = f"{request.last_name} {request.name} {request.first_name}"
        response.full_name = full_name
        
        self.get_logger().info(
            f'Received request:\n'
            f'  Last name: {request.last_name}\n'
            f'  Name: {request.name}\n'
            f'  First name: {request.first_name}\n'
            f'Generated full name: "{response.full_name}"'
        )
        
        return response

def main():
    rclpy.init()
    
    service = FullNameService()
    
    try:
        rclpy.spin(service)
    except KeyboardInterrupt:
        pass
    finally:
        service.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
