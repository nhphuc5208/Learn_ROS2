import os
from glob import glob

from setuptools import find_packages, setup

package_name = 'my_robot_description'


def files(folder, pattern='*'):
    return [f for f in glob(os.path.join(folder, pattern)) if os.path.isfile(f)]


setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'urdf'), files('urdf')),
        (os.path.join('share', package_name, 'launch'), files('launch', '*launch.py')),
        (os.path.join('share', package_name, 'rviz'), files('rviz', '*.rviz')),
        (os.path.join('share', package_name, 'worlds'), files('worlds')),
        (os.path.join('share', package_name, 'config'), files('config', '*.yaml')),
        (os.path.join('share', package_name, 'maps'), files('maps')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='nhp',
    maintainer_email='nhp@todo.todo',
    description='URDF, Gazebo, bridge, SLAM, Nav2 for a two-wheeled robot',
    license='Apache-2.0',
    entry_points={'console_scripts': []},
)
