from setuptools import setup
import os
from glob import glob

package_name = 'gazebo_robot_circle'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ezhsluny',
    maintainer_email='y.basova@g.nsu.ru',
    description='TODO: Package description',
    license='TODO: License declaration',
    entry_points={
        'console_scripts': [
            'circle_movement = gazebo_robot_circle.circle_movement:main',
        ],
    },
)
