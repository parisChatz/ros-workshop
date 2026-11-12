# ---------------------------------------------------------------------------
# EXERCISE 1: scan_listener  -  reading a sensor
#
# GOAL:
#   Print the distance to the closest obstacle seen by the robot's lidar.
#   (You can read the finished version in scan_listener.py if you get stuck.)
#
# YOUR TASK: complete the 3 TODOs below. The rest of the code is already written.
#
# HOW TO RUN:
#   Terminal 1 - start the simulation:     tb3world
#   Terminal 2 - build and run your node:  cb                      (builds and sources)
#                                          ros2 run lecture_demo exercise_scan_listener
#   Because we build with --symlink-install, after the first build you only need to
#   restart the node (Ctrl+C, run it again) when you change this file.
#
# HOW TO KNOW IT WORKS:
#   You see lines like "closest obstacle: 0.48 m". Drive the robot closer to a wall
#   (ros2 run turtlebot3_teleop teleop_keyboard) and the number gets smaller.
#
# (The "flake8: noqa" line below only silences the code-style checker, which would complain
#  about names you have not used yet. You can delete it once you finished.)
# ---------------------------------------------------------------------------

# flake8: noqa

import math

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan


class ExerciseScanListener(Node):
    """Print the distance to the closest obstacle (exercise version)."""

    def __init__(self):
        super().__init__("exercise_scan_listener")

        # TODO 1: Subscribe to the lidar topic.
        #   Use:  self.create_subscription(message_type, topic_name, callback, qos_profile)
        #     * message_type (already imported above)
        #     * topic_name
        #     * callback     : self.on_scan             (the function defined below)
        #     * qos_profile  : qos_profile_sensor_data  (sensors need this "best effort" QoS)
        #   Write your line here:

    def on_scan(self, msg: LaserScan):
        """Run every time a new lidar message arrives."""
        # msg.ranges is a list of distances in metres, one per laser beam.
        # Some values are NOT usable: 'inf' or 'nan' (the beam hit nothing) and values
        # smaller than msg.range_min (too close to measure).

        # TODO 2: Keep only the usable distances.
        #   Replace the empty list with a list comprehension:
        #       valid = [r for r in msg.ranges if <condition>]
        #   A distance r is usable when BOTH are true:
        #       math.isfinite(r)      and      r > msg.range_min
        valid = []

        if not valid:
            return  # nothing usable (this is what happens until you finish TODO 2)

        # TODO 3: Find the smallest usable distance and print it.
        #   * The closest obstacle is the smallest distance
        #   * Print it with:  self.get_logger().info(f'closest obstacle: {closest:.2f} m')
        #   * Optional: add  throttle_duration_sec=1.0  inside info(...) to print once per second.
        #   * Can do also with simple Python print
        #   Write your lines here:


def main(args=None):
    """Start ROS 2, run the node until Ctrl+C, then shut down cleanly."""
    rclpy.init(args=args)
    node = ExerciseScanListener()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        # Ctrl+C in the terminal (or `ros2 launch` stopping us): quit quietly
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
