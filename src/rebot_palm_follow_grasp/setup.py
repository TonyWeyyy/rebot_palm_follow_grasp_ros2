from setuptools import setup, find_packages
from glob import glob
import os

package_name = 'rebot_palm_follow_grasp'

setup(
    name=package_name,
    version='2.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
         ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'config'), glob('config/*.json')),
        (os.path.join('share', package_name, 'config'), glob('config/*.task')),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='rebot',
    maintainer_email='tony@localhost.localdomain',
    description='reBot Arm B601-RS palm following + pinch grasping (ROS2 port)',
    license='MIT',
    entry_points={
        'console_scripts': [
            'vision_node = rebot_palm_follow_grasp.vision_node:main',
            'servo_node = rebot_palm_follow_grasp.servo_node:main',
        ],
    },
)
