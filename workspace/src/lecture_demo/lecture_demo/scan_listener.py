# ---------------------------------------------------------------------------
# DEMO 1: scan_listener  -  READING a sensor (a "subscriber" node)
#
# What it does:
#   The TurtleBot3 has a lidar: a spinning laser that measures the distance to
#   obstacles in all directions. The simulator publishes those measurements on the
#   topic /scan. This node SUBSCRIBES to that topic and prints the distance to the
#   closest obstacle.
#
# ROS 2 ideas used here:
#   * Node          - a program that talks to other programs through ROS 2
#   * Topic         - a named channel (here: /scan) that nodes publish/subscribe to
#   * Subscription  - "call my function every time a new message arrives on this topic"
#   * Callback      - that function (here: on_scan)
#   * QoS           - settings that describe how messages are delivered
#
# Run it (with the simulation running):   ros2 run lecture_demo scan_listener
# Or everything at once:                  ros2 launch lecture_demo scan_listener_demo.launch.py
# Try the exercise version:               exercise_scan_listener.py
# ---------------------------------------------------------------------------

import math

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan


class ScanListener(Node):
    """Subscribe to the lidar and log the distance to the closest obstacle."""

    def __init__(self):
        # Every node needs a name. It shows up in `ros2 node list`.
        super().__init__('scan_listener')

        # Subscribe to the lidar topic. Arguments:
        #   1. the message type       -> LaserScan (distances measured by the lidar)
        #   2. the topic name         -> 'scan' (the full name is /scan)
        #   3. the callback function  -> self.on_scan runs for every new message
        #   4. the QoS profile        -> sensors publish "best effort" (no re-sending of lost
        #                                messages), so we must ask for the matching profile.
        #                                With the default profile we would receive nothing!
        self.create_subscription(
            LaserScan, 'scan', self.on_scan, qos_profile_sensor_data)

    def on_scan(self, msg: LaserScan):
        """Run every time a new lidar message arrives."""
        # msg.ranges is a list of distances in metres, one number per laser beam.
        # Not every number is usable:
        #   * inf / nan             -> the beam did not hit anything within range
        #   * smaller than range_min -> too close for the sensor to measure
        # So we keep only the finite readings that are bigger than range_min.
        valid = [r for r in msg.ranges if math.isfinite(r) and r > msg.range_min]

        if valid:
            # min() gives the smallest distance = the closest obstacle.
            closest = min(valid)
            # throttle_duration_sec=1.0 means "print at most once per second",
            # otherwise the terminal would be flooded (the lidar publishes many times a second).
            self.get_logger().info(
                f'closest obstacle: {closest:.2f} m', throttle_duration_sec=1.0)


def main(args=None):
    """Start ROS 2, run the node until Ctrl+C, then shut down cleanly."""
    rclpy.init(args=args)       # start ROS 2 communication
    node = ScanListener()       # create our node
    try:
        rclpy.spin(node)        # keep the node alive: callbacks run while we "spin"
    except (KeyboardInterrupt, ExternalShutdownException):
        # Ctrl+C in the terminal (or `ros2 launch` stopping us): quit quietly
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


# This lets you also run the file directly with `python3 scan_listener.py`.
if __name__ == '__main__':
    main()
