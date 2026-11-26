import random

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import Float32


class TempPublisher(Node):
    def __init__(self):
        super().__init__('temp_publisher')

        # Parameters can be changed from outside (CLI, launch, params.yaml)
        self.declare_parameter('rate_hz', 2.0)
        self.declare_parameter('machine_id', 'AC-01')

        self.machine_id = self.get_parameter('machine_id').value
        rate = float(self.get_parameter('rate_hz').value)

        self.pub = self.create_publisher(Float32, 'compressor/temperature', 10)
        self.timer = self.create_timer(1.0 / rate, self.tick)
        self.get_logger().info(
            f'Publisher started for {self.machine_id} at {rate} Hz')

    def tick(self):
        msg = Float32()
        msg.data = round(random.uniform(55.0, 95.0), 2)
        self.pub.publish(msg)
        self.get_logger().info(f'{self.machine_id} temp = {msg.data} C')


def main(args=None):
    rclpy.init(args=args)
    node = TempPublisher()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
