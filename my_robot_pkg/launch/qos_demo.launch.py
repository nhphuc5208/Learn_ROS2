"""Day 3 - Deliberately cause a QoS mismatch, then fix it.

  Broken:  ros2 launch my_robot_pkg qos_demo.launch.py
           (pub best_effort, sub reliable -> sub receives nothing)
  Fixed :  ros2 launch my_robot_pkg qos_demo.launch.py pub_reliability:=reliable
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pub_arg = DeclareLaunchArgument('pub_reliability', default_value='best_effort')
    sub_arg = DeclareLaunchArgument('sub_reliability', default_value='reliable')

    pub = Node(
        package='my_robot_pkg',
        executable='qos_pub',
        name='qos_pub',
        parameters=[{'reliability': LaunchConfiguration('pub_reliability')}],
        output='screen',
    )
    sub = Node(
        package='my_robot_pkg',
        executable='qos_sub',
        name='qos_sub',
        parameters=[{'reliability': LaunchConfiguration('sub_reliability')}],
        output='screen',
    )

    return LaunchDescription([pub_arg, sub_arg, pub, sub])
