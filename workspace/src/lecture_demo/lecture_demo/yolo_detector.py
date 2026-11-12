# ---------------------------------------------------------------------------
# DEMO 4: yolo_detector  -  OBJECT DETECTION with a neural network (YOLO)
#
# What it does:
#   Looks at the robot's camera image and finds OBJECTS in it ("person", "chair", "bus"...),
#   telling you WHAT each object is, WHERE it is (a box around it) and how SURE the
#   network is (a score between 0 and 1).
#
#   /camera/image_raw --->  [ yolo_detector ]  --->  /yolo/image       (image with boxes drawn)
#                                              --->  /yolo/detections  (the results as data)
#
# What is YOLO?
#   "You Only Look Once" is a family of neural networks that detect objects in a single pass
#   over the image, so it is fast. We use the `ultralytics` Python package and by default its
#   model YOLO26s ("small", about 20 MB; `-p model:=yolo26n.pt` is the smaller, faster "nano"),
#   which was trained on the COCO dataset: it knows 80 everyday classes (person, car, bus,
#   chair, bottle, cat, laptop, ...).
#   Edge detection (demo 3) is a hand-written recipe; YOLO has LEARNED what objects look like.
#
# ROS 2 ideas used here:
#   * Load the model ONCE in __init__ (loading is slow), then reuse it for every image.
#   * QoS depth 1: if YOLO is slower than the camera, we skip old images instead of falling
#     further and further behind.
#   * Standard message: vision_msgs/Detection2DArray is the ROS 2 way to publish 2D detections,
#     so any other node (a tracker, a "follow the person" controller...) can use them.
#
# NOTE: the default TurtleBot3 Gazebo world only has walls and pillars, no real everyday
# objects. YOLO is not perfect: it may "see" things that are not there, usually with a LOW
# score (e.g. "refrigerator 0.45" for a pillar). That is normal for neural networks. Raise the
# `conf` parameter (e.g. -p conf:=0.6) to keep only the detections it is sure about, or show it
# an image with real objects (publish a photo on /camera/image_raw, or add objects to Gazebo).
#
# Run it (with the simulation running):   ros2 run lecture_demo yolo_detector
#   (on your own Ubuntu, outside Docker, see the README: activate the uv environment, then
#    python3 src/lecture_demo/lecture_demo/yolo_detector.py)
# See the result:                        ros2 run rqt_image_view rqt_image_view
#                                         (choose /yolo/image in the drop-down list)
# See the data:                           ros2 topic echo /yolo/detections
# ---------------------------------------------------------------------------

from pathlib import Path

from cv_bridge import CvBridge
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import Image
from ultralytics import YOLO
from vision_msgs.msg import Detection2D, Detection2DArray, ObjectHypothesisWithPose

# Folders where model files ("weights") are kept: the Docker image ships some in /opt/models;
# on your own computer they live in your home folder (downloaded there on the first run).
DOCKER_MODELS = Path("/opt/models")
USER_MODELS = Path.home() / ".local" / "share" / "lecture_demo" / "models"


def find_model(name):
    """Turn a model name such as 'yolo26s.pt' into the file to load."""
    if Path(name).parent != Path("."):
        return str(Path(name).expanduser())  # a path was given: use it as it is
    for folder in (DOCKER_MODELS, USER_MODELS):
        if (folder / name).exists():
            return str(folder / name)
    # Not found anywhere: ultralytics downloads it (internet needed) into this folder,
    # which you are always allowed to write to.
    return str(USER_MODELS / name)


class YoloDetector(Node):
    """Detect objects in the camera image with YOLO and publish the results."""

    def __init__(self):
        super().__init__("yolo_detector")

        # Parameters (settings you can change, e.g.
        #   ros2 run lecture_demo yolo_detector --ros-args -p conf:=0.5 -p imgsz:=320)
        # A full path loads that file. A bare name such as 'yolov8n.pt' (careful: with a
        # 'v') is looked up in /opt/models (Docker), then in ~/.local/share/lecture_demo/models,
        # and downloaded into the second folder the first time (internet needed).
        # A misspelt name cannot be downloaded and gives an error.
        self.declare_parameter("model", "yolo26s.pt")
        # Minimum score (0-1) for a detection to be kept. Higher = fewer, surer detections.
        self.declare_parameter("conf", 0.25)
        # The image is shrunk to this size (in pixels) before going into the network.
        # Smaller = faster but misses small objects. Try 320 if your computer is slow.
        self.declare_parameter("imgsz", 640)

        # Load the neural network ONCE (this takes a second or two).
        model_path = find_model(self.get_parameter("model").value)
        self.get_logger().info(f"Loading YOLO model: {model_path}")
        try:
            self.model = YOLO(model_path)
        except (FileNotFoundError, PermissionError):
            # Ultralytics tries to download missing models; if that fails (typo in the
            # name, no internet, a folder you cannot write to) it ends up here with a
            # confusing message.
            raise RuntimeError(
                f"Could not find or download the model '{model_path}'. Check the spelling "
                "(real names: yolov8n.pt, yolo11n.pt, yolo26n.pt, yolo26s.pt ... note the "
                "'v' in yolov8), your internet connection, and that you can write to the "
                "folder."
            ) from None

        # Converts between ROS Image messages and OpenCV images.
        self.bridge = CvBridge()

        # Publishers: the annotated image (for humans) and the detections (for other nodes).
        self.image_pub = self.create_publisher(Image, "yolo/image", 10)
        self.detections_pub = self.create_publisher(
            Detection2DArray, "yolo/detections", 10
        )

        # Camera QoS: "best effort" like the camera, but keep only the NEWEST image (depth 1).
        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )
        self.create_subscription(Image, "camera/image_raw", self.on_image, qos)
        self.get_logger().info("Ready: waiting for images on camera/image_raw")

    def on_image(self, msg: Image):
        """Run for every camera image: detect objects and publish the results."""
        conf = self.get_parameter("conf").value
        imgsz = self.get_parameter("imgsz").value

        # 1. ROS image message -> OpenCV image (3 colour channels, the order YOLO expects)
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")

        # 2. Run the neural network. It returns one result per image; we gave it one image.
        #    device='cpu': no graphics card needed. verbose=False: no printing per frame.
        result = self.model(frame, imgsz=imgsz, conf=conf, device="cpu", verbose=False)[
            0
        ]

        # The network takes a while. If you pressed Ctrl+C meanwhile, ROS is already shutting
        # down and publishing would raise an error, so just stop here.
        if not rclpy.ok():
            return

        # 3. Turn every detected object into a vision_msgs/Detection2D.
        #    result.boxes holds, for each object: the box (x_center, y_center, width, height
        #    in pixels), the class number and the confidence score.
        detections = Detection2DArray()
        detections.header = msg.header  # same timestamp and frame as the image
        found = []
        for box, class_id, score in zip(
            result.boxes.xywh.tolist(),
            result.boxes.cls.tolist(),
            result.boxes.conf.tolist(),
        ):
            x_center, y_center, width, height = box
            name = result.names[
                int(class_id)
            ]  # class number -> name, e.g. 0 -> 'person'

            detection = Detection2D()
            detection.header = msg.header
            # What is it, and how sure are we?
            hypothesis = ObjectHypothesisWithPose()
            hypothesis.hypothesis.class_id = name
            hypothesis.hypothesis.score = float(score)
            detection.results.append(hypothesis)
            # Where is it? (the box, in pixels)
            detection.bbox.center.position.x = x_center
            detection.bbox.center.position.y = y_center
            detection.bbox.size_x = width
            detection.bbox.size_y = height

            detections.detections.append(detection)
            found.append(f"{name} {score:.2f}")

        self.detections_pub.publish(detections)

        # 4. Publish an image with the boxes and labels drawn on it (result.plot() does it).
        annotated = self.bridge.cv2_to_imgmsg(result.plot(), encoding="bgr8")
        annotated.header = msg.header
        self.image_pub.publish(annotated)

        # 5. Tell the user what we saw (at most once per second).
        self.get_logger().info(
            "detected: " + (", ".join(found) if found else "nothing"),
            throttle_duration_sec=1.0,
        )


def main(args=None):
    """Start ROS 2, run the node until Ctrl+C, then shut down cleanly."""
    rclpy.init(args=args)
    node = YoloDetector()
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
