"""Day 3 - QoS trap demo.

Two nodes share this file:
  qos_pub : publishes /qos_demo/data, reliability set by parameter
  qos_sub : subscribes to /qos_demo/data, reliability set by parameter

Publisher BEST_EFFORT + subscriber RELIABLE  -> receives NOTHING, and no error is reported.
Publisher RELIABLE  + subscriber BEST_EFFORT -> works normally.
"""
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import QoSDurabilityPolicy, QoSProfile, QoSReliabilityPolicy
from std_msgs.msg import Int32

TOPIC = 'qos_demo/data'


def make_qos(reliability: str) -> QoSProfile:
    policy = {
        'reliable': QoSReliabilityPolicy.RELIABLE,
        'best_effort': QoSReliabilityPolicy.BEST_EFFORT,
    }.get(reliability.lower())
    if policy is None:
        raise ValueError(f"reliability must be 'reliable' or 'best_effort', got '{reliability}'")
    return QoSProfile(
        depth=10,
        reliability=policy,
        durability=QoSDurabilityPolicy.VOLATILE)


class QosPub(Node):
    def __init__(self):
        super().__init__('qos_pub')
        self.declare_parameter('reliability', 'best_effort')
        rel = self.get_parameter('reliability').value
        self.pub = self.create_publisher(Int32, TOPIC, make_qos(rel))
        self.count = 0
        self.timer = self.create_timer(0.5, self.tick)
        self.get_logger().info(f'qos_pub reliability = {rel}')

    def tick(self):
        self.count += 1
        self.pub.publish(Int32(data=self.count))
        self.get_logger().info(f'sent {self.count}')


class QosSub(Node):
    def __init__(self):
        super().__init__('qos_sub')
        self.declare_parameter('reliability', 'reliable')
        rel = self.get_parameter('reliability').value
        self.sub = self.create_subscription(Int32, TOPIC, self.on_msg, make_qos(rel))
        self.received = 0
        # Report periodically so it is obvious when no data arrives
        self.watchdog = self.create_timer(2.0, self.report)
        self.get_logger().info(f'qos_sub reliability = {rel}')

    def on_msg(self, msg: Int32):
        self.received += 1
        self.get_logger().info(f'received {msg.data}')

    def report(self):
        if self.received == 0:
            self.get_logger().warn(
                'No messages received yet! Check: ros2 topic info /qos_demo/data -v')


def _run(node_cls, args=None):
    rclpy.init(args=args)
    node = node_cls()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


def main_pub(args=None):
    _run(QosPub, args)


def main_sub(args=None):
    _run(QosSub, args)
