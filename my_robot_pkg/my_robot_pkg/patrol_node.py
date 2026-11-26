"""Day 7: factory patrol robot.

Loops through the waypoints with Nav2 (NavigateToPose action). A waypoint that fails is retried
max_retries times, then skipped.

  ros2 service call /patrol/enable std_srvs/srv/SetBool "{data: false}"   # stop
  ros2 service call /patrol/enable std_srvs/srv/SetBool "{data: true}"    # resume
  ros2 topic echo /patrol/status                                          # status
"""
import math

import rclpy
from action_msgs.msg import GoalStatus
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import String
from std_srvs.srv import SetBool


class PatrolNode(Node):
    def __init__(self):
        super().__init__('patrol_node')
        # flattened patrol waypoints: [x, y, yaw_radians, x, y, yaw, ...] in the map frame
        self.declare_parameter('waypoints', [
            4.0, 0.0, 0.0,
            4.0, 4.0, 1.57,
            -4.0, 4.0, 3.14,
            -4.0, -4.0, -1.57,
        ])
        self.declare_parameter('frame_id', 'map')
        self.declare_parameter('max_retries', 2)

        flat = list(self.get_parameter('waypoints').value)
        if len(flat) < 3 or len(flat) % 3 != 0:
            raise ValueError('waypoints length must be a multiple of 3: [x, y, yaw, ...]')
        self.waypoints = [flat[i:i + 3] for i in range(0, len(flat), 3)]
        self.frame_id = self.get_parameter('frame_id').value
        self.max_retries = int(self.get_parameter('max_retries').value)

        self.index = 0
        self.lap = 1
        self.retries = 0
        self.enabled = True
        self.goal_active = False
        self.goal_handle = None

        self.client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self.status_pub = self.create_publisher(String, 'patrol/status', 10)
        self.create_service(SetBool, 'patrol/enable', self.on_enable)
        self.create_timer(1.0, self.loop)
        self.get_logger().info(f'Patrol ready: {len(self.waypoints)} waypoints')

    # ---------- inputs ----------
    def on_enable(self, req, res):
        self.enabled = req.data
        if not self.enabled:
            self.cancel_goal()
        res.success = True
        res.message = f'Patrol {"ON" if self.enabled else "OFF"}'
        self.get_logger().info(res.message)
        self.publish_status(res.message)
        return res

    # ---------- helpers ----------
    def publish_status(self, text):
        self.status_pub.publish(String(data=text))

    def cancel_goal(self):
        if self.goal_handle is not None:
            self.goal_handle.cancel_goal_async()

    def make_pose(self, x, y, yaw):
        p = PoseStamped()
        p.header.frame_id = self.frame_id
        p.header.stamp = self.get_clock().now().to_msg()
        p.pose.position.x = float(x)
        p.pose.position.y = float(y)
        p.pose.orientation.z = math.sin(yaw / 2.0)
        p.pose.orientation.w = math.cos(yaw / 2.0)
        return p

    def advance(self):
        self.retries = 0
        self.index = (self.index + 1) % len(self.waypoints)
        if self.index == 0:
            self.lap += 1
            self.get_logger().info(f'===== Starting lap {self.lap} =====')

    def send_goal(self, x, y, yaw):
        goal = NavigateToPose.Goal()
        goal.pose = self.make_pose(x, y, yaw)
        self.goal_active = True
        self.client.send_goal_async(goal).add_done_callback(self.on_accepted)

    # ---------- main loop (1 Hz) ----------
    def loop(self):
        if not self.enabled or self.goal_active:
            return
        if not self.client.wait_for_server(timeout_sec=1.0):
            self.get_logger().warn('Waiting for Nav2 action server...')
            return

        x, y, yaw = self.waypoints[self.index]
        self.get_logger().info(f'--> Waypoint {self.index + 1}: ({x}, {y})')
        self.publish_status(f'GOING {self.index + 1} lap {self.lap}')
        self.send_goal(x, y, yaw)

    # ---------- results from Nav2 ----------
    def on_accepted(self, future):
        handle = future.result()
        if not handle.accepted:
            self.get_logger().error('Nav2 rejected the goal')
            self.goal_active = False
            return
        self.goal_handle = handle
        # disabled while waiting for Nav2 to accept -> cancel right away
        if not self.enabled:
            handle.cancel_goal_async()
        handle.get_result_async().add_done_callback(self.on_result)

    def on_result(self, future):
        status = future.result().status
        self.goal_handle = None
        self.goal_active = False

        n = self.index + 1
        if status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info(f'[OK] Reached waypoint {n} (lap {self.lap})')
            self.publish_status(f'REACHED {n} lap {self.lap}')
            self.advance()
        elif status == GoalStatus.STATUS_CANCELED:
            self.get_logger().warn(f'Goal for waypoint {n} canceled, will retry when patrol is enabled')
        else:
            self.retries += 1
            if self.retries > self.max_retries:
                self.get_logger().error(f'Waypoint {n} failed {self.retries} times, skipping')
                self.publish_status(f'SKIPPED {n}')
                self.advance()
            else:
                self.get_logger().warn(
                    f'Waypoint {n} failed (status={status}), retry {self.retries}/{self.max_retries}')


def main(args=None):
    rclpy.init(args=args)
    node = PatrolNode()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
