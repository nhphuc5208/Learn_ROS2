"""Day 5 + 6 - Gazebo Harmonic + robot + bridge.

  ros2 launch my_robot_description sim.launch.py
  ros2 launch my_robot_description sim.launch.py rviz:=true
  ros2 launch my_robot_description sim.launch.py x:=-3.0 y:=0.0 yaw:=0.0
  ros2 launch my_robot_description sim.launch.py headless:=true   # no Gazebo GUI (lighter on resources)
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (AppendEnvironmentVariable, DeclareLaunchArgument,
                            IncludeLaunchDescription)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (Command, LaunchConfiguration, PythonExpression)
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg = get_package_share_directory('my_robot_description')
    pkg_ros_gz = get_package_share_directory('ros_gz_sim')

    xacro_file = os.path.join(pkg, 'urdf', 'my_robot.urdf.xacro')
    bridge_cfg = os.path.join(pkg, 'config', 'bridge.yaml')
    rviz_cfg = os.path.join(pkg, 'rviz', 'sim.rviz')

    world = LaunchConfiguration('world')
    headless = LaunchConfiguration('headless')

    robot_description = ParameterValue(
        Command(['xacro ', xacro_file]), value_type=str)

    # lets Gazebo find meshes or models if you add them later
    set_res = AppendEnvironmentVariable(
        'GZ_SIM_RESOURCE_PATH', os.path.join(pkg, '..'))

    # -r: run immediately, -v4: verbose log, -s: server only (headless)
    gz_args = PythonExpression([
        "'-r -v4 ' + ('-s ' if '", headless, "' == 'true' else '') + '", world, "'"])

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz, 'launch', 'gz_sim.launch.py')),
        launch_arguments={'gz_args': gz_args, 'on_exit_shutdown': 'true'}.items(),
    )

    rsp = Node(
        package='robot_state_publisher', executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description,
                     'use_sim_time': True}],
        output='screen',
    )

    spawn = Node(
        package='ros_gz_sim', executable='create',
        arguments=['-topic', 'robot_description',
                   '-name', 'my_robot',
                   '-x', LaunchConfiguration('x'),
                   '-y', LaunchConfiguration('y'),
                   '-z', '0.15',
                   '-Y', LaunchConfiguration('yaw')],
        output='screen',
    )

    bridge = Node(
        package='ros_gz_bridge', executable='parameter_bridge',
        parameters=[{'config_file': bridge_cfg, 'use_sim_time': True}],
        output='screen',
    )

    rviz = Node(
        package='rviz2', executable='rviz2', arguments=['-d', rviz_cfg],
        parameters=[{'use_sim_time': True}],
        condition=IfCondition(LaunchConfiguration('rviz')),
        output='screen',
    )

    return LaunchDescription([
        DeclareLaunchArgument('world', default_value=os.path.join(pkg, 'worlds', 'factory.sdf'),
                              description='Path to the world .sdf file'),
        DeclareLaunchArgument('rviz', default_value='false', description='Open RViz2'),
        DeclareLaunchArgument('headless', default_value='false',
                              description='true: run the Gazebo server only, no GUI'),
        DeclareLaunchArgument('x', default_value='0.0'),
        DeclareLaunchArgument('y', default_value='0.0'),
        DeclareLaunchArgument('yaw', default_value='0.0'),
        set_res, gazebo, rsp, spawn, bridge, rviz,
    ])
