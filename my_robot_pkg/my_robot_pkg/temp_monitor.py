import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import Float32
from std_srvs.srv import Trigger


class TempMonitor(Node):
    def __init__(self):
        super().__init__('temp_monitor')
        self.declare_parameter('threshold', 85.0)
        self.alarm_count = 0

        self.sub = self.create_subscription(
            Float32, 'compressor/temperature', self.on_temp, 10)
        self.reset_srv = self.create_service(
            Trigger, 'temp_monitor/reset_alarm', self.on_reset)

        self.get_logger().info(f'Alarm threshold: {self.threshold()} C')

    def threshold(self):
        # Re-read every time so `ros2 param set` takes effect immediately
        return float(self.get_parameter('threshold').value)

    def on_temp(self, msg: Float32):
        limit = self.threshold()
        if msg.data > limit:
            self.alarm_count += 1
            self.get_logger().warn(
                f'OVERHEAT {msg.data} C (> {limit}) - alarm #{self.alarm_count}')
        else:
            self.get_logger().info(f'OK {msg.data} C')

    def on_reset(self, request, response):
        self.alarm_count = 0
        response.success = True
        response.message = 'alarm_count = 0'
        self.get_logger().info('alarm_count reset')
        return response


def main(args=None):
    rclpy.init(args=args)
    node = TempMonitor()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
