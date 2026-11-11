"""
Demo 1: scan_listener - READING a sensor (subscriber).

What this launch file starts:
  1. Gazebo with the TurtleBot3 world
  2. scan_listener - reads the lidar (/scan) and prints the distance to the
     closest obstacle once per second

Run it with:
    ros2 launch lecture_demo scan_listener_demo.launch.py

What to try:
  * Watch the "closest obstacle" numbers in this terminal.
  * Open a SECOND terminal and drive the robot towards a wall:
        ros2 run turtlebot3_teleop teleop_keyboard
    The number should shrink as you get closer.
  * See the raw data yourself:   ros2 topic echo /scan --once

Code to read: lecture_demo/scan_listener.py
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    tb3_gazebo = get_package_share_directory('turtlebot3_gazebo')

    # Start Gazebo + the simulated TurtleBot3 (provided by the turtlebot3_gazebo package).
    world = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(tb3_gazebo, 'launch', 'turtlebot3_world.launch.py')
        )
    )

    # Start our subscriber node.
    scan_listener = Node(
        package='lecture_demo',
        executable='scan_listener',
        # Follow Gazebo's clock (needed for anything that runs with the simulation).
        parameters=[{'use_sim_time': True}],
        # Print the node's log messages in this terminal.
        output='screen',
    )

    return LaunchDescription([world, scan_listener])
