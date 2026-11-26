import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_srvs.srv import SetBool


class MotorService(Node):
    def __init__(self):
        super().__init__('motor_service')
        self.motor_on = False
        self.srv = self.create_service(SetBool, 'set_motor', self.handle_request)

    def handle_request(self, request, response):
        self.motor_on = request.data
        state = 'ON' if self.motor_on else 'OFF'
        response.success = True
        response.message = f'Motor is {state}'
        self.get_logger().info(response.message)
        return response


def main(args=None):
    rclpy.init(args=args)
    node = MotorService()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
