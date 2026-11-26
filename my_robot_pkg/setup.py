import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'my_robot_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # the three entries below were added on Day 3
        (os.path.join('share', package_name, 'launch'),
            glob(os.path.join('launch', '*launch.py'))),
        (os.path.join('share', package_name, 'config'),
            glob(os.path.join('config', '*.yaml'))),
        (os.path.join('share', package_name, 'rviz'),
            glob(os.path.join('rviz', '*.rviz'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='mm',
    maintainer_email='mm@example.com',
    description='ROS 2 learning package',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'temp_publisher  = my_robot_pkg.temp_publisher:main',
            'temp_monitor    = my_robot_pkg.temp_monitor:main',
            'temp_subscriber = my_robot_pkg.temp_subscriber:main',
            'motor_service   = my_robot_pkg.motor_service:main',
            'machine_status_publisher = my_robot_pkg.machine_status_publisher:main',
            'qos_pub         = my_robot_pkg.qos_demo:main_pub',
            'qos_sub         = my_robot_pkg.qos_demo:main_sub',
            # Day 5
            'square_driver   = my_robot_pkg.square_driver:main',
            # Day 7
            'patrol_node     = my_robot_pkg.patrol_node:main',
        ],
    },
)