"""Day 6 - Mapping: Gazebo + SLAM Toolbox + RViz2 in one command.

  ros2 launch my_robot_description slam.launch.py
  # another terminal: ros2 run teleop_twist_keyboard teleop_twist_keyboard
  # save the map: ros2 run nav2_map_server map_saver_cli -f ~/ros2_ws/src/my_robot_description/maps/factory_map
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory('my_robot_description')
    slam_pkg = get_package_share_directory('slam_toolbox')

    slam_params = os.path.join(pkg, 'config', 'slam_params.yaml')
    rviz_cfg = os.path.join(pkg, 'rviz', 'nav.rviz')

    # scoped=True: keeps 'rviz:=false' from leaking back out, otherwise the RViz below is turned off
    sim = GroupAction(scoped=True, actions=[IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg, 'launch', 'sim.launch.py')),
        launch_arguments={'rviz': 'false',
                          'headless': LaunchConfiguration('headless')}.items(),
    )])

    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(slam_pkg, 'launch', 'online_async_launch.py')),
        launch_arguments={'slam_params_file': slam_params,
                          'use_sim_time': 'true'}.items(),
    )

    rviz = Node(
        package='rviz2', executable='rviz2', arguments=['-d', rviz_cfg],
        parameters=[{'use_sim_time': True}],
        condition=IfCondition(LaunchConfiguration('rviz')),
        output='screen',
    )

    return LaunchDescription([
        DeclareLaunchArgument('rviz', default_value='true'),
        DeclareLaunchArgument('headless', default_value='false'),
        sim, slam, rviz,
    ])
