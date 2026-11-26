"""Day 5/7 - Drop an extra obstacle box into a running Gazebo.

  ros2 launch my_robot_description spawn_obstacle.launch.py x:=1.5 y:=0.0
  ros2 launch my_robot_description spawn_obstacle.launch.py name:=box2 x:=-4.0 y:=1.0 size:=0.6

Remove: gz service -s /world/factory/remove --reqtype gz.msgs.Entity \
          --reptype gz.msgs.Boolean --timeout 2000 --req 'name: "box1" type: MODEL'
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def _spawn(context):
    name = LaunchConfiguration('name').perform(context)
    size = float(LaunchConfiguration('size').perform(context))
    x = LaunchConfiguration('x').perform(context)
    y = LaunchConfiguration('y').perform(context)
    sdf = f"""<?xml version="1.0"?>
<sdf version="1.10">
  <model name="{name}">
    <static>true</static>
    <link name="link">
      <collision name="c"><geometry><box><size>{size} {size} 1.0</size></box></geometry></collision>
      <visual name="v">
        <geometry><box><size>{size} {size} 1.0</size></box></geometry>
        <material><ambient>0.8 0.1 0.1 1</ambient><diffuse>0.8 0.1 0.1 1</diffuse></material>
      </visual>
    </link>
  </model>
</sdf>"""
    return [Node(
        package='ros_gz_sim', executable='create',
        arguments=['-world', 'factory', '-name', name, '-string', sdf,
                   '-x', x, '-y', y, '-z', '0.5'],
        output='screen',
    )]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('name', default_value='box1'),
        DeclareLaunchArgument('x', default_value='1.5'),
        DeclareLaunchArgument('y', default_value='0.0'),
        DeclareLaunchArgument('size', default_value='0.5'),
        OpaqueFunction(function=_spawn),
    ])
