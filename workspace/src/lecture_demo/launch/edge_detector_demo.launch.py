"""
Demo 3: edge_detector - PROCESSING camera images with OpenCV.

What this launch file starts:
  1. Gazebo with the TurtleBot3 world
  2. edge_detector - reads the camera image (/camera/image_raw), finds edges with the
     Canny algorithm and publishes the result as a new image (/camera/edges)
  3. rqt_image_view - a small window that shows the edge image

Run it with:
    ros2 launch lecture_demo edge_detector_demo.launch.py
    ros2 launch lecture_demo edge_detector_demo.launch.py low_threshold:=30 high_threshold:=100

What to try:
  * In the rqt_image_view window, use the drop-down to switch between
    /camera/image_raw (what the robot sees) and /camera/edges (the result).
  * Drive the robot towards the walls and the coloured pillars to see more edges
    (open a SECOND terminal:  ros2 run turtlebot3_teleop teleop_keyboard).
    An empty view (just floor and sky) only shows the horizon line.
  * Lower thresholds -> more edges (and more noise). Higher -> fewer edges.

Things to know:
  * Only the 'waffle' robot models have a camera (not 'burger'). Check with: echo $TURTLEBOT3_MODEL
  * The camera is large (1920x1080), so expect a low frame rate in the simulator.

Code to read: lecture_demo/edge_detector.py
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    tb3_gazebo = get_package_share_directory('turtlebot3_gazebo')

    # Launch arguments: Canny uses two thresholds. Pixels with a strong brightness
    # change (above 'high') are edges; weak ones (below 'low') are dropped.
    # Values typed on the command line arrive as TEXT, but the node's parameters are
    # integers, so we wrap them in ParameterValue(..., value_type=int) to convert them.
    low = ParameterValue(LaunchConfiguration('low_threshold'), value_type=int)
    high = ParameterValue(LaunchConfiguration('high_threshold'), value_type=int)

    world = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(tb3_gazebo, 'launch', 'turtlebot3_world.launch.py')
        )
    )

    edge_detector = Node(
        package='lecture_demo',
        executable='edge_detector',
        parameters=[
            {
                'low_threshold': low,
                'high_threshold': high,
                'use_sim_time': True,
            }
        ],
        output='screen',
    )

    # A ready-made ROS tool (not our code) that displays an image topic.
    # The argument tells it which topic to show first.
    image_viewer = Node(
        package='rqt_image_view',
        executable='rqt_image_view',
        arguments=['/camera/edges'],
    )

    return LaunchDescription(
        [
            # Declare the arguments with default values and descriptions
            # (shown by: ros2 launch lecture_demo edge_detector_demo.launch.py --show-args).
            DeclareLaunchArgument(
                'low_threshold',
                default_value='50',
                description='Canny lower threshold (0-255)',
            ),
            DeclareLaunchArgument(
                'high_threshold',
                default_value='150',
                description='Canny upper threshold (0-255)',
            ),
            world,
            edge_detector,
            image_viewer,
        ]
    )
