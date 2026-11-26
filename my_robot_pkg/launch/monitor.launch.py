from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    params = PathJoinSubstitution([
        FindPackageShare('my_robot_pkg'), 'config', 'params.yaml'])

    threshold_arg = DeclareLaunchArgument(
        'threshold', default_value='85.0',
        description='Temperature alarm threshold (C)')
    rqt_arg = DeclareLaunchArgument(
        'rqt', default_value='false',
        description='true to also open rqt_graph')

    publisher = Node(
        package='my_robot_pkg',
        executable='temp_publisher',
        name='temp_publisher',     # must match the key in params.yaml
        parameters=[params],
        output='screen',
    )

    # params.yaml is loaded first, then the command-line threshold overrides it
    monitor = Node(
        package='my_robot_pkg',
        executable='temp_monitor',
        name='temp_monitor',
        parameters=[
            params,
            {'threshold': ParameterValue(LaunchConfiguration('threshold'), value_type=float)},
        ],
        output='screen',
    )

    motor = Node(
        package='my_robot_pkg',
        executable='motor_service',
        name='motor_service',
        output='screen',
    )

    rqt_graph = Node(
        package='rqt_graph',
        executable='rqt_graph',
        name='rqt_graph',
        condition=IfCondition(LaunchConfiguration('rqt')),
    )

    return LaunchDescription([
        threshold_arg, rqt_arg,
        publisher, monitor, motor, rqt_graph,
    ])
