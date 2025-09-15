# Copyright 2016 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import rclpy
from rclpy.node import Node

from std_msgs.msg import String


class CommandPublisher(Node):

    def __init__(self):
        super().__init__('command_publisher')
        self.publisher_ = self.create_publisher(String, 'cmd_text', 10)
        timer_period = 2.0  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0
        self.commands = ['move_forward', 'turn_left', 'move_forward', 'turn_right', 'move_backward']

    def timer_callback(self):
        if self.i < len(self.commands):
            msg = String()
            msg.data = self.commands[self.i]
            self.publisher_.publish(msg)
            self.get_logger().info('Publishing: "%s"' % msg.data)
            self.i += 1
        else:
            self.timer.cancel()
            self.get_logger().info('All commands sent')


def main(args=None):
    rclpy.init(args=args)

    command_publisher = CommandPublisher()

    rclpy.spin(command_publisher)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    command_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()