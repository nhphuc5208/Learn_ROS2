import random

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node

from my_robot_interfaces.msg import MachineStatus


class MachineStatusPublisher(Node):
    def __init__(self):
        super().__init__('machine_status_publisher')
        self.declare_parameter('machine_id', 'MACHINE_01')
        self.pub = self.create_publisher(MachineStatus, 'machine_status', 10)
        self.timer = self.create_timer(1.0, self.publish_status)

    def publish_status(self):
        msg = MachineStatus()
        msg.machine_id = self.get_parameter('machine_id').value
        msg.temperature = round(random.uniform(50.0, 90.0), 2)
        msg.pressure = round(random.uniform(1.0, 6.0), 2)
        msg.is_running = random.random() > 0.1
        self.pub.publish(msg)
        self.get_logger().info(
            f'[{msg.machine_id}] T={msg.temperature:.2f} °C, '
            f'P={msg.pressure:.2f} bar, running={msg.is_running}')


def main(args=None):
    rclpy.init(args=args)
    node = MachineStatusPublisher()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
