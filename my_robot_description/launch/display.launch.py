"""Day 4 - View the robot in RViz2 (no Gazebo yet).

  ros2 launch my_robot_description display.launch.py
  ros2 launch my_robot_description display.launch.py use_arm:=true   # arm exercise
  ros2 launch my_robot_description display.launch.py gui:=false
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg = get_package_share_directory('my_robot_description')
    xacro_file = os.path.join(pkg, 'urdf', 'my_robot.urdf.xacro')
    rviz_cfg = os.path.join(pkg, 'rviz', 'display.rviz')

    use_arm = LaunchConfiguration('use_arm')
    gui = LaunchConfiguration('gui')

    robot_description = ParameterValue(
        Command(['xacro ', xacro_file, ' use_arm:=', use_arm]), value_type=str)

    return LaunchDescription([
        DeclareLaunchArgument('use_arm', default_value='false',
                              description='true: add a revolute arm'),
        DeclareLaunchArgument('gui', default_value='true',
                              description='true: open the joint_state_publisher_gui slider window'),

        Node(package='robot_state_publisher', executable='robot_state_publisher',
             parameters=[{'robot_description': robot_description,
                          'use_sim_time': False}],
             output='screen'),
        Node(package='joint_state_publisher_gui', executable='joint_state_publisher_gui',
             condition=IfCondition(gui)),
        Node(package='joint_state_publisher', executable='joint_state_publisher',
             condition=UnlessCondition(gui)),
        Node(package='rviz2', executable='rviz2', arguments=['-d', rviz_cfg],
             output='screen'),
    ])
