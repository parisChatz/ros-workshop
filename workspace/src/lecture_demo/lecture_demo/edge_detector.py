# ---------------------------------------------------------------------------
# DEMO 3: edge_detector  -  PROCESSING images (subscriber + publisher)
#
# What it does:
#   Takes the robot's camera image, finds the edges in it (places where the brightness
#   changes a lot, like the border of a wall) and publishes the result as a new image.
#
#   /camera/image_raw  --->  [ edge_detector ]  --->  /camera/edges
#     (colour image)                                  (black image, edges in white)
#
# ROS 2 ideas used here:
#   * A node can subscribe AND publish: it is a "processing step" between two topics.
#   * cv_bridge  - converts between ROS image messages and OpenCV images (NumPy arrays)
#   * OpenCV     - a library of image-processing functions (cv2)
#
# The image processing recipe (the "Canny" edge detector):
#   colour image -> grayscale -> blur (removes noise) -> Canny (finds the edges)
#
# NOTE: only the 'waffle' TurtleBot3 models have a camera (not 'burger').
#
# Run it (with the simulation running):   ros2 run lecture_demo edge_detector
# See the result:                         ros2 run rqt_image_view rqt_image_view
# Or everything at once:                  ros2 launch lecture_demo edge_detector_demo.launch.py
# Try the exercise version:               exercise_edge_detector.py
# ---------------------------------------------------------------------------

import cv2
from cv_bridge import CvBridge
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image


class EdgeDetector(Node):
    """Detect edges in the camera image and publish them as a new image."""

    def __init__(self):
        super().__init__('edge_detector')

        # Parameters you can change while the node is running, e.g.
        #   ros2 param set /edge_detector low_threshold 30
        # Canny keeps strong brightness changes (> high_threshold) as edges, drops weak
        # ones (< low_threshold). Lower values -> more edges, but also more noise.
        self.declare_parameter('low_threshold', 50)
        self.declare_parameter('high_threshold', 150)
        self.declare_parameter('blur_kernel', 5)  # blur size in pixels, must be odd

        # The "bridge" converts ROS Image messages <-> OpenCV images.
        self.bridge = CvBridge()

        # Publisher for the result (arguments: type, topic name, queue size).
        self.pub = self.create_publisher(Image, 'camera/edges', 10)

        # Subscribe to the camera. Like the lidar, cameras publish "best effort", so we
        # need the matching QoS profile or no images will arrive.
        self.create_subscription(
            Image, 'camera/image_raw', self.on_image, qos_profile_sensor_data)

    def on_image(self, msg: Image):
        """Run for every camera image: find the edges and publish them."""
        # Read the current parameter values.
        low = self.get_parameter('low_threshold').value
        high = self.get_parameter('high_threshold').value
        k = self.get_parameter('blur_kernel').value | 1  # "| 1" makes the number odd

        # 1. ROS image message -> OpenCV image ('bgr8' = 3 colour channels, 8 bits each)
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        # 2. Colour -> grayscale (edges only need brightness, not colour)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 3. Blur a little, otherwise tiny details and noise would show up as edges
        blurred = cv2.GaussianBlur(gray, (k, k), 0)

        # 4. Find the edges. The result is a black image with white edge lines.
        edges = cv2.Canny(blurred, low, high)

        # 5. OpenCV image -> ROS image message ('mono8' = one grey channel)
        out = self.bridge.cv2_to_imgmsg(edges, encoding='mono8')
        # Keep the original timestamp and frame, so other nodes know which camera image
        # this result belongs to.
        out.header = msg.header

        # 6. Publish the result on /camera/edges
        self.pub.publish(out)


def main(args=None):
    """Start ROS 2, run the node until Ctrl+C, then shut down cleanly."""
    rclpy.init(args=args)
    node = EdgeDetector()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        # Ctrl+C in the terminal (or `ros2 launch` stopping us): quit quietly
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
