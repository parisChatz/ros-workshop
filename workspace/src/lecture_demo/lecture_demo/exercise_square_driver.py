# ---------------------------------------------------------------------------
# EXERCISE 2: square_driver  -  moving the robot
#
# GOAL:
#   Make the robot drive in a square: forward, turn 90 degrees, repeat.
#   (You can read the finished version in square_driver.py if you get stuck.)
#
# YOUR TASK: complete the 4 TODOs below. The rest of the code is already written:
#   a timer calls tick() 20 times per second, and the node switches between the states
#   'forward' and 'turn' when the current state has lasted long enough.
#
# HOW TO RUN:
#   Terminal 1 - start the simulation:     tb3world
#   Terminal 2 - build and run your node:  cb
#                                          ros2 run lecture_demo exercise_square_driver
#   After the first build, just restart the node when you change this file.
#
# HOW TO KNOW IT WORKS:
#   The robot drives a square. Look at what you publish with:  ros2 topic echo /cmd_vel
#   Try other sizes:  ros2 run lecture_demo exercise_square_driver --ros-args -p side_length:=0.5
#
# REMEMBER: on ROS 2 Jazzy the robot listens to TwistStamped (a velocity WITH a timestamp).
#
# (The "flake8: noqa" line below only silences the code-style checker, which would complain
#  about names you have not used yet. You can delete it once you finished.)
# ---------------------------------------------------------------------------

# flake8: noqa

import math

from geometry_msgs.msg import TwistStamped
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node


class ExerciseSquareDriver(Node):
    """Publish velocity commands that make the robot drive in a square (exercise version)."""

    def __init__(self):
        super().__init__("exercise_square_driver")

        # Parameters (settings you can change when starting the node).
        self.declare_parameter("side_length", 1.0)  # metres
        self.declare_parameter("linear_speed", 0.2)  # metres per second
        self.declare_parameter("angular_speed", 0.5)  # radians per second

        # TODO 1: Create the publisher that sends velocity commands to the robot.
        #   Use:  self.create_publisher(message_type, topic_name, queue_size)
        #     * message_type (already imported above)
        #     * topic_name
        #     * queue_size   : 10
        #   Replace the None below with your call:
        self.pub = None

        # State machine: what are we doing right now, and since when?
        self.state = "forward"
        self.state_start = self.get_clock().now()

        # Call self.tick 20 times per second.
        self.create_timer(0.05, self.tick)

    def tick(self):
        """Run 20 times per second: publish a command and switch state when it is time."""
        side = self.get_parameter("side_length").value
        v = self.get_parameter("linear_speed").value
        w = self.get_parameter("angular_speed").value

        # TODO 2: How long (in seconds) should the current state last?
        #   * Going forward:  time = distance / speed          ->  side / v
        #   * Turning 90 deg: time = angle / angular speed     ->  (math.pi / 2) / w
        #   Use an if/else on self.state, e.g.
        #       if self.state == 'forward':
        #           duration = ...
        #       else:
        #           duration = ...
        duration = 0.0

        # How long have we been in this state? (nanoseconds -> seconds)
        elapsed = (self.get_clock().now() - self.state_start).nanoseconds / 1e9

        # Time is up: switch between 'forward' and 'turn' and restart the stopwatch.
        if elapsed >= duration:
            self.state = "turn" if self.state == "forward" else "forward"
            self.state_start = self.get_clock().now()

        # Build the velocity command (the header with the timestamp is already filled in).
        msg = TwistStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "base_link"

        # TODO 3: Fill in the velocity.
        #   * 'forward' state: drive forward -> msg.twist.linear.x = v
        #   * 'turn' state:    rotate        -> msg.twist.angular.z = w
        #   (anything you do not set stays 0, so the robot does not do that movement)

        # TODO 4: Send the command to the robot.
        #   Use the publisher from TODO 1:  self.pub.publish(msg)


def main(args=None):
    """Start ROS 2, run the node until Ctrl+C, then shut down cleanly."""
    rclpy.init(args=args)
    node = ExerciseSquareDriver()
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
