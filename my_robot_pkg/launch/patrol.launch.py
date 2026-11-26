"""Day 7 - Full-system launch: Gazebo + bridge + SLAM + Nav2 + RViz2 + patrol_node.

  ros2 launch my_robot_pkg patrol.launch.py
  ros2 launch my_robot_pkg patrol.launch.py headless:=true          # no Gazebo GUI
  ros2 launch my_robot_pkg patrol.launch.py map:=$HOME/ros2_ws/src/my_robot_description/maps/factory_map.yaml

Stop / resume:
  ros2 service call /patrol/enable std_srvs/srv/SetBool "{data: false}"
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    desc_pkg = get_package_share_directory('my_robot_description')
    my_pkg = get_package_share_directory('my_robot_pkg')

    # sim + (SLAM or AMCL) + Nav2 + RViz2 are already bundled in nav.launch.py
    nav = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(desc_pkg, 'launch', 'nav.launch.py')),
        launch_arguments={
            'map': LaunchConfiguration('map'),
            'rviz': LaunchConfiguration('rviz'),
            'headless': LaunchConfiguration('headless'),
        }.items(),
    )

    params = os.path.join(my_pkg, 'config', 'patrol.yaml')

    patrol = Node(
        package='my_robot_pkg', executable='patrol_node', name='patrol_node',
        parameters=[params, {'use_sim_time': True}],
        output='screen',
    )

    return LaunchDescription([
        DeclareLaunchArgument('map', default_value='',
                              description='map .yaml; leave empty to use SLAM'),
        DeclareLaunchArgument('rviz', default_value='true'),
        DeclareLaunchArgument('headless', default_value='false'),
        nav,
        # delay so Nav2 can activate all its lifecycle nodes
        # (patrol_node waits for the action server itself, so extra delay is harmless)
        TimerAction(period=20.0, actions=[patrol]),
    ])
