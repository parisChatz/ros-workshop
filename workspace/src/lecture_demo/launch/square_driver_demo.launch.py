"""
Demo 2: square_driver - MOVING the robot (publisher).

What this launch file starts:
  1. Gazebo with the TurtleBot3 world
  2. square_driver - publishes velocity commands on /cmd_vel so the robot
     drives forward, turns 90 degrees, and repeats (a square)

Run it with:
    ros2 launch lecture_demo square_driver_demo.launch.py
    ros2 launch lecture_demo square_driver_demo.launch.py side_length:=1.0

What to try:
  * Change side_length and see the square get bigger or smaller.
  * See the commands being sent:   ros2 topic echo /cmd_vel
  * Check the robot's estimated position:   ros2 topic echo /odom --field pose.pose.position
  * Note: the driver is "open loop" (it only uses timers, it never checks where the robot
    really is), so the square is not perfect. Can you improve it using /odom?

Code to read: lecture_demo/square_driver.py
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    tb3_gazebo = get_package_share_directory('turtlebot3_gazebo')

    # Launch argument: lets you write  side_length:=1.0  on the command line.
    side = LaunchConfiguration('side_length')

    world = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(tb3_gazebo, 'launch', 'turtlebot3_world.launch.py')
        )
    )

    square_driver = Node(
        package='lecture_demo',
        executable='square_driver',
        # Parameters are settings of the node. Here we pass the launch argument on to the
        # node's 'side_length' parameter (declared in square_driver.py).
        parameters=[{'side_length': side, 'use_sim_time': True}],
        output='screen',
    )

    return LaunchDescription(
        [
            # Declare the argument with a default value and a description
            # (shown by: ros2 launch lecture_demo square_driver_demo.launch.py --show-args).
            DeclareLaunchArgument(
                'side_length',
                default_value='0.5',
                description='Side of the square, in metres',
            ),
            world,
            square_driver,
        ]
    )
