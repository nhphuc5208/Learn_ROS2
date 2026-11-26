"""Day 3 - Static TF + RViz2.

Hand-built TF tree (no URDF yet, URDF comes on Day 4):
  odom -> base_footprint -> base_link -> lidar_link
                                      -> camera_link
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def static_tf(parent, child, x=0.0, y=0.0, z=0.0, roll=0.0, pitch=0.0, yaw=0.0):
    return Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name=f'tf_{parent}_to_{child}',
        arguments=[
            '--x', str(x), '--y', str(y), '--z', str(z),
            '--roll', str(roll), '--pitch', str(pitch), '--yaw', str(yaw),
            '--frame-id', parent, '--child-frame-id', child,
        ],
    )


def generate_launch_description():
    rviz_cfg = PathJoinSubstitution([
        FindPackageShare('my_robot_pkg'), 'rviz', 'day3.rviz'])

    rviz_arg = DeclareLaunchArgument(
        'rviz', default_value='true', description='Open RViz2')

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_cfg],
        condition=IfCondition(LaunchConfiguration('rviz')),
        output='screen',
    )

    return LaunchDescription([
        rviz_arg,
        static_tf('odom', 'base_footprint'),
        static_tf('base_footprint', 'base_link', z=0.10),
        static_tf('base_link', 'lidar_link', x=0.10, z=0.15),
        static_tf('base_link', 'camera_link', x=0.20, z=0.08, pitch=0.2),
        rviz,
    ])
