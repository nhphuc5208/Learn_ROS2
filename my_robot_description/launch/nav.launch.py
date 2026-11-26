"""Day 6 - Nav2 drives to a goal autonomously.

Two modes:
  1) SLAM + Nav2 (no prior map needed - default):
       ros2 launch my_robot_description nav.launch.py
  2) Saved map + AMCL (save a map first with slam.launch.py):
       ros2 launch my_robot_description nav.launch.py \
           map:=$HOME/ros2_ws/src/my_robot_description/maps/factory_map.yaml
     -> remember to click "2D Pose Estimate" in RViz2 before setting a goal.

In RViz2 click "Nav2 Goal" (2D Goal Pose), then click on the map.
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, GroupAction,
                            IncludeLaunchDescription, TimerAction)
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory('my_robot_description')
    slam_pkg = get_package_share_directory('slam_toolbox')
    nav2_pkg = get_package_share_directory('nav2_bringup')

    slam_params = os.path.join(pkg, 'config', 'slam_params.yaml')
    nav2_params = os.path.join(pkg, 'config', 'nav2_params.yaml')
    rviz_cfg = os.path.join(pkg, 'rviz', 'nav.rviz')

    map_yaml = LaunchConfiguration('map')
    use_map = IfCondition(PythonExpression(["'", map_yaml, "' != ''"]))
    use_slam = UnlessCondition(PythonExpression(["'", map_yaml, "' != ''"]))

    # GroupAction(scoped=True): keeps the 'rviz:=false' passed to sim.launch.py from
    # leaking back into this file (if it leaked, Nav2's RViz would be turned off too).
    sim = GroupAction(scoped=True, actions=[IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg, 'launch', 'sim.launch.py')),
        launch_arguments={'rviz': 'false',
                          'headless': LaunchConfiguration('headless')}.items(),
    )])

    # --- Mode 1: SLAM builds the map while Nav2 runs ---
    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(slam_pkg, 'launch', 'online_async_launch.py')),
        launch_arguments={'slam_params_file': slam_params,
                          'use_sim_time': 'true'}.items(),
        condition=use_slam,
    )

    # --- Mode 2: map_server + AMCL on a saved map ---
    localization = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_pkg, 'launch', 'localization_launch.py')),
        launch_arguments={'map': map_yaml,
                          'use_sim_time': 'true',
                          'params_file': nav2_params}.items(),
        condition=use_map,
    )

    navigation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_pkg, 'launch', 'navigation_launch.py')),
        launch_arguments={'use_sim_time': 'true',
                          'params_file': nav2_params}.items(),
    )

    rviz = Node(
        package='rviz2', executable='rviz2', arguments=['-d', rviz_cfg],
        parameters=[{'use_sim_time': True}],
        condition=IfCondition(LaunchConfiguration('rviz')),
        output='screen',
    )

    return LaunchDescription([
        DeclareLaunchArgument('map', default_value='',
                              description='Path to map .yaml; leave empty to use SLAM'),
        DeclareLaunchArgument('rviz', default_value='true'),
        DeclareLaunchArgument('headless', default_value='false'),
        sim,
        # wait for Gazebo + bridge before starting SLAM/Nav2 so TF and /clock already exist
        TimerAction(period=5.0, actions=[slam, localization, navigation]),
        rviz,
    ])
