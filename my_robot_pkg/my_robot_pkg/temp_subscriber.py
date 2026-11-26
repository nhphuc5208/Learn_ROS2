import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import Float32


class TempSubscriber(Node):
    def __init__(self):
        super().__init__('temp_subscriber')
        self.sub = self.create_subscription(
            Float32, 'temperature', self.callback, 10)

    def callback(self, msg):
        if msg.data > 30.0:
            self.get_logger().warn(f'High temperature: {msg.data} °C')
        else:
            self.get_logger().info(f'Received: {msg.data} °C')


def main(args=None):
    rclpy.init(args=args)
    node = TempSubscriber()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
