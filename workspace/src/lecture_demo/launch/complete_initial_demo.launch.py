"""
Complete initial demo: runs ALL the example nodes together.

What this launch file starts:
  1. Gazebo with the TurtleBot3 world (the simulated robot and its environment)
  2. square_driver  - drives the robot in a square
  3. edge_detector  - detects edges in the camera image
  4. scan_listener  - prints the distance to the closest obstacle

Run it with:
    ros2 launch lecture_demo complete_initial_demo.launch.py
    ros2 launch lecture_demo complete_initial_demo.launch.py side_length:=1.0

Want to understand each piece on its own? See the other launch files in this folder:
    scan_listener_demo.launch.py, square_driver_demo.launch.py, edge_detector_demo.launch.py
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


# ROS 2 looks for this exact function name. It must return a LaunchDescription,
# which is simply a list of "things to start".
def generate_launch_description():
    # Find where the turtlebot3_gazebo package is installed on this computer.
    tb3_gazebo = get_package_share_directory('turtlebot3_gazebo')

    # A launch argument lets you change a value from the command line
    # (e.g. side_length:=1.0) without editing this file.
    # LaunchConfiguration is a placeholder that is filled in when the launch starts.
    side = LaunchConfiguration('side_length')

    # "Include" another launch file: this one starts Gazebo, spawns the robot
    # and the ROS <-> Gazebo bridges (so ROS topics like /scan and /cmd_vel work).
    world = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(tb3_gazebo, 'launch', 'turtlebot3_world.launch.py')
        )
    )

    return LaunchDescription(
        [
            # Declare the argument and give it a default value and a description
            # (shown by: ros2 launch lecture_demo complete_initial_demo.launch.py --show-args).
            DeclareLaunchArgument(
                'side_length',
                default_value='0.5',
                description='Side of the square, in metres',
            ),
            world,
            # Each Node(...) starts one of OUR programs. 'package' is the ROS package
            # it lives in and 'executable' is the name from entry_points in setup.py.
            Node(
                package='lecture_demo',
                executable='square_driver',
                # use_sim_time makes the node follow Gazebo's clock instead of the
                # computer's clock. Always set it when working with a simulation.
                parameters=[{'side_length': side, 'use_sim_time': True}],
                # 'screen' prints the node's log messages in this terminal.
                output='screen',
            ),
            Node(
                package='lecture_demo',
                executable='edge_detector',
                parameters=[{'use_sim_time': True}],
                output='screen',
            ),
            Node(
                package='lecture_demo',
                executable='scan_listener',
                parameters=[{'use_sim_time': True}],
                output='screen',
            ),
        ]
    )
