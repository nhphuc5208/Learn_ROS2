"""Day 5 - Exercise: publish /cmd_vel so the robot drives a square.

Uses /odom as feedback (closed loop), so it is more accurate than "drive 4 seconds, then turn".

  ros2 run my_robot_pkg square_driver --ros-args -p use_sim_time:=true
  ros2 run my_robot_pkg square_driver --ros-args -p use_sim_time:=true -p side:=1.5 -p laps:=2
"""
import math

import rclpy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node


def yaw_from_quat(q):
    return math.atan2(2.0 * (q.w * q.z + q.x * q.y), 1.0 - 2.0 * (q.y * q.y + q.z * q.z))


def angle_diff(a, b):
    """a - b, normalized to [-pi, pi]."""
    return math.atan2(math.sin(a - b), math.cos(a - b))


class SquareDriver(Node):
    def __init__(self):
        super().__init__('square_driver')
        self.declare_parameter('side', 2.0)        # m
        self.declare_parameter('linear_speed', 0.3)  # m/s
        self.declare_parameter('angular_speed', 0.6)  # rad/s
        self.declare_parameter('laps', 1)

        self.side = float(self.get_parameter('side').value)
        self.v = float(self.get_parameter('linear_speed').value)
        self.w = float(self.get_parameter('angular_speed').value)
        self.total_edges = 4 * int(self.get_parameter('laps').value)

        self.pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.create_subscription(Odometry, 'odom', self.on_odom, 10)
        self.timer = self.create_timer(0.05, self.step)

        self.pose = None          # current (x, y, yaw)
        self.start = None         # pose at the start of the current edge / turn
        self.state = 'WAIT_ODOM'  # WAIT_ODOM -> FORWARD -> TURN -> FORWARD ... -> DONE
        self.edges_done = 0
        self.get_logger().info(f'Square with {self.side} m sides, {self.total_edges // 4} lap(s)')

    def on_odom(self, msg: Odometry):
        p = msg.pose.pose
        self.pose = (p.position.x, p.position.y, yaw_from_quat(p.orientation))

    def stop(self):
        self.pub.publish(Twist())

    def step(self):
        if self.pose is None:
            return
        cmd = Twist()
        x, y, yaw = self.pose

        if self.state == 'WAIT_ODOM':
            self.start = self.pose
            self.state = 'FORWARD'
            self.get_logger().info(f'Edge 1 starting at ({x:.2f}, {y:.2f})')

        elif self.state == 'FORWARD':
            dist = math.hypot(x - self.start[0], y - self.start[1])
            remaining = self.side - dist
            if remaining <= 0.01:
                self.stop()
                self.start = self.pose
                self.state = 'TURN'
                return
            # slow down near the end, hold the initial heading
            cmd.linear.x = max(0.05, min(self.v, remaining * 1.5))
            cmd.angular.z = 2.0 * angle_diff(self.start[2], yaw)

        elif self.state == 'TURN':
            target = self.start[2] + math.pi / 2
            err = angle_diff(target, yaw)
            if abs(err) < 0.01:
                self.stop()
                self.edges_done += 1
                self.get_logger().info(f'Finished edge {self.edges_done}/{self.total_edges}')
                if self.edges_done >= self.total_edges:
                    self.state = 'DONE'
                    self.get_logger().info('Square complete!')
                else:
                    self.start = self.pose
                    self.state = 'FORWARD'
                return
            cmd.angular.z = math.copysign(max(0.1, min(self.w, abs(err) * 2.0)), err)

        elif self.state == 'DONE':
            self.stop()
            self.timer.cancel()
            return

        self.pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = SquareDriver()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        if rclpy.ok():
            node.stop()
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
