"""
Empty world with an ambulance and a walking person (from Gazebo Fuel) + a TurtleBot3 waffle.

Run it with:
    ros2 launch lecture_demo ambulance_world.launch.py
    ros2 launch lecture_demo ambulance_world.launch.py x_pose:=-1.0 y_pose:=0.5

The first start downloads the two models from fuel.gazebosim.org (about 30 MB), so it needs
internet and takes a little longer. They are cached in ~/.gz/fuel afterwards.

The robot is always the waffle, regardless of $TURTLEBOT3_MODEL.
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    AppendEnvironmentVariable,
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    SetEnvironmentVariable,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    tb3_gazebo = get_package_share_directory("turtlebot3_gazebo")
    ros_gz_sim = get_package_share_directory("ros_gz_sim")
    launch_dir = os.path.join(tb3_gazebo, "launch")
    world = os.path.join(
        get_package_share_directory("lecture_demo"), "worlds", "ambulance_world.sdf"
    )

    x_pose = LaunchConfiguration("x_pose")
    y_pose = LaunchConfiguration("y_pose")

    gz_server = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim, "launch", "gz_sim.launch.py")
        ),
        launch_arguments={
            "gz_args": ["-r -s -v2 ", world],
            "on_exit_shutdown": "true",
        }.items(),
    )
    gz_client = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim, "launch", "gz_sim.launch.py")
        ),
        launch_arguments={"gz_args": "-g -v2 "}.items(),
    )
    robot_state_publisher = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(launch_dir, "robot_state_publisher.launch.py")
        ),
        launch_arguments={"use_sim_time": "true"}.items(),
    )
    spawn_turtlebot = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(launch_dir, "spawn_turtlebot3.launch.py")
        ),
        launch_arguments={"x_pose": x_pose, "y_pose": y_pose}.items(),
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "x_pose", default_value="-10.0", description="Robot start x, in metres"
            ),
            DeclareLaunchArgument(
                "y_pose", default_value="0.0", description="Robot start y, in metres"
            ),
            # spawn_turtlebot3 and robot_state_publisher read this variable.
            SetEnvironmentVariable("TURTLEBOT3_MODEL", "waffle"),
            AppendEnvironmentVariable(
                "GZ_SIM_RESOURCE_PATH", os.path.join(tb3_gazebo, "models")
            ),
            gz_server,
            gz_client,
            spawn_turtlebot,
            robot_state_publisher,
        ]
    )
