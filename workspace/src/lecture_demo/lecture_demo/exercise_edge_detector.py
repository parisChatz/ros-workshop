# ---------------------------------------------------------------------------
# EXERCISE 3: edge_detector  -  processing camera images
#
# GOAL:
#   Detect the edges in the robot's camera image and publish them as a new image.
#
#       /camera/image_raw  --->  [ your node ]  --->  /camera/edges
#
#   (You can read the finished version in edge_detector.py if you get stuck.)
#
# YOUR TASK: complete the 4 TODOs below. The publisher and the conversion between ROS
# images and OpenCV images (cv_bridge) are already written for you.
#
# HOW TO RUN (the camera only exists on the 'waffle' robot models, not 'burger'):
#   Terminal 1 - start the simulation:     tb3world
#   Terminal 2 - build and run your node:  cb
#                                          ros2 run lecture_demo exercise_edge_detector
#   Terminal 3 - look at the result:       ros2 run rqt_image_view rqt_image_view
#                (pick /camera/image_raw or /camera/edges in the drop-down list)
#   Tip: drive the robot towards the walls and pillars to see more edges:
#        ros2 run turtlebot3_teleop teleop_keyboard
#
# (The "flake8: noqa" line below only silences the code-style checker, which would complain
#  about names you have not used yet. You can delete it once you finished.)
# ---------------------------------------------------------------------------

# flake8: noqa

import cv2
from cv_bridge import CvBridge
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image


class ExerciseEdgeDetector(Node):
    """Detect edges in the camera image and publish them as a new image (exercise version)."""

    def __init__(self):
        super().__init__("exercise_edge_detector")

        # Canny edge detector settings: strong brightness changes (> high) are edges,
        # weak ones (< low) are dropped.
        self.declare_parameter("low_threshold", 50)
        self.declare_parameter("high_threshold", 150)

        # Converts between ROS image messages and OpenCV images.
        self.bridge = CvBridge()

        # Publisher for the result image (already written for you).
        self.pub = self.create_publisher(Image, "camera/edges", 10)

        # TODO 1: Subscribe to the camera.
        #   Use:  self.create_subscription(message_type, topic_name, callback, qos_profile)
        #     * message_type already imported above)
        #     * topic_name
        #     * callback     : self.on_image            (the function defined below)
        #     * qos_profile  : qos_profile_sensor_data  (cameras need this "best effort" QoS)
        #   Write your line here:

    def on_image(self, msg: Image):
        """Run for every camera image: find the edges and publish them."""
        low = self.get_parameter("low_threshold").value
        high = self.get_parameter("high_threshold").value

        # ROS image message -> OpenCV image ('bgr8' = 3 colour channels). Already written.
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")

        # TODO 2: Convert the colour image to grayscale (edges only need brightness).
        #   Use:  gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        #   Replace the None below with your call:
        gray = None

        # TODO 3: Blur the grayscale image a little, then find the edges.
        #   Blur  (removes noise):  blurred = cv2.GaussianBlur(image, (5, 5), 0)
        #   Edges (Canny):          edges = cv2.Canny(image, low, high)
        #   Replace the None below with your two lines (blur `gray`, then Canny the blurred one):
        edges = None

        if edges is None:
            self.get_logger().warn(
                "Exercise not finished yet: complete TODO 2 and TODO 3",
                throttle_duration_sec=5.0,
            )
            return

        # TODO 4: Publish the edge image.
        #   * OpenCV image -> ROS message:
        #         out = self.bridge.cv2_to_imgmsg(edges, encoding='mono8')
        #   * Copy the header of the camera image so the timestamp stays correct:
        #         out.header = msg.header
        #   * Publish it with the publisher created above
        #   Write your lines here:


def main(args=None):
    """Start ROS 2, run the node until Ctrl+C, then shut down cleanly."""
    rclpy.init(args=args)
    node = ExerciseEdgeDetector()
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
