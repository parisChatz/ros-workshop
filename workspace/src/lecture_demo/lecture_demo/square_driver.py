# ---------------------------------------------------------------------------
# DEMO 2: square_driver  -  MOVING the robot (a "publisher" node)
#
# What it does:
#   Drives the TurtleBot3 in a square: go forward, turn 90 degrees, repeat.
#   To move the robot we PUBLISH velocity commands on the topic /cmd_vel.
#
# How it works:
#   A timer calls tick() 20 times per second. The node is always in one of two
#   "states": 'forward' or 'turn'. In each state it publishes the right velocity, and
#   when the state has lasted long enough it switches to the other one.
#   This is "open loop" control: we only use time, we never check where the robot really
#   is, so the square will not be perfect (wheels slip, the simulator is not exact...).
#
# ROS 2 ideas used here:
#   * Publisher  - sends messages on a topic
#   * Timer      - calls a function again and again at a fixed rate
#   * Parameter  - a setting of the node that can be changed without editing the code
#   * Message    - TwistStamped = a velocity (linear + angular) with a timestamp
#
# NOTE: on ROS 2 Jazzy the TurtleBot3 simulation listens to geometry_msgs/TwistStamped on
# /cmd_vel. Older ROS 2 versions and older tutorials use plain Twist (no header).
#
# Run it (with the simulation running):
#   ros2 run lecture_demo square_driver --ros-args -p side_length:=0.5 -p use_sim_time:=true
# Or everything at once:   ros2 launch lecture_demo square_driver_demo.launch.py
# Try the exercise version: exercise_square_driver.py
# ---------------------------------------------------------------------------

import math

from geometry_msgs.msg import TwistStamped
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node


class SquareDriver(Node):
    """Publish velocity commands that make the robot drive in a square."""

    def __init__(self):
        super().__init__('square_driver')

        # Parameters: settings with a default value. You can change them when starting the
        # node:  ros2 run lecture_demo square_driver --ros-args -p side_length:=1.0
        self.declare_parameter('side_length', 1.0)    # metres
        self.declare_parameter('linear_speed', 0.2)   # metres per second
        self.declare_parameter('angular_speed', 0.5)  # radians per second

        # Create the publisher. Arguments: message type, topic name, queue size.
        # (The queue size is how many messages may wait if a subscriber is slow.)
        self.pub = self.create_publisher(TwistStamped, 'cmd_vel', 10)

        # State machine: what are we doing right now, and since when?
        self.state = 'forward'
        self.state_start = self.get_clock().now()

        # Call self.tick every 0.05 s (= 20 times per second).
        self.create_timer(0.05, self.tick)

    def tick(self):
        """Run 20 times per second: publish a command and switch state when it is time."""
        # Read the current parameter values.
        side = self.get_parameter('side_length').value
        v = self.get_parameter('linear_speed').value
        w = self.get_parameter('angular_speed').value

        # How long should the current state last?
        #   forward: time = distance / speed      -> side / v
        #   turn:    time = angle / angular speed -> (90 degrees = pi/2 radians) / w
        duration = side / v if self.state == 'forward' else (math.pi / 2) / w

        # How long have we been in this state? (nanoseconds -> seconds)
        elapsed = (self.get_clock().now() - self.state_start).nanoseconds / 1e9

        # Time is up: switch between 'forward' and 'turn' and restart the stopwatch.
        if elapsed >= duration:
            self.state = 'turn' if self.state == 'forward' else 'forward'
            self.state_start = self.get_clock().now()

        # Build the velocity command.
        msg = TwistStamped()
        msg.header.stamp = self.get_clock().now().to_msg()  # "when was this command made"
        msg.header.frame_id = 'base_link'                   # the robot's own coordinate frame
        if self.state == 'forward':
            msg.twist.linear.x = v    # drive forward (x axis points forward), no rotation
        else:
            msg.twist.angular.z = w   # rotate left around the vertical (z) axis, no driving

        # Send it! The simulator receives it and moves the robot.
        self.pub.publish(msg)


def main(args=None):
    """Start ROS 2, run the node until Ctrl+C, then shut down cleanly."""
    rclpy.init(args=args)
    node = SquareDriver()
    try:
        rclpy.spin(node)        # keep running: the timer keeps calling tick()
    except (KeyboardInterrupt, ExternalShutdownException):
        # Ctrl+C in the terminal (or `ros2 launch` stopping us): quit quietly
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
