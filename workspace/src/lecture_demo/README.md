# lecture_demo

Demo nodes, launch files and exercises for the ROS 2 lecture (TurtleBot3 in Gazebo).

## Layout

This is a standard ROS 2 Python (`ament_python`) package, the same layout that
`ros2 pkg create --build-type ament_python` generates:

```
lecture_demo/
├── package.xml                  # package name, dependencies, maintainer, license
├── setup.py                     # how to install it + the `ros2 run` commands (entry_points)
├── setup.cfg                    # tells ROS 2 where to put the executables (leave as is)
├── resource/lecture_demo        # marker file so ROS 2 can find the package (leave empty)
├── lecture_demo/                # the Python code: one file per node
│   ├── __init__.py
│   ├── scan_listener.py         # DEMO 1: subscriber (lidar)
│   ├── square_driver.py         # DEMO 2: publisher (drive in a square)
│   ├── edge_detector.py         # DEMO 3: subscriber + publisher (camera image processing)
│   ├── yolo_detector.py         # DEMO 4: object detection with a neural network (YOLO)
│   ├── exercise_scan_listener.py   # demos 1-3 with TODOs for you to complete
│   ├── exercise_square_driver.py
│   └── exercise_edge_detector.py
├── launch/                      # launch files: start the simulation and nodes together
│   ├── scan_listener_demo.launch.py
│   ├── square_driver_demo.launch.py
│   ├── edge_detector_demo.launch.py
│   ├── complete_initial_demo.launch.py
│   └── ambulance_world.launch.py
├── worlds/                      # Gazebo worlds (ambulance_world.sdf)
└── test/                        # automatic code-style checks
```

## Build

In the Docker container:

```bash
cd ~/workspace
colcon build --symlink-install      # shortcut: cb
source install/setup.bash
```

Rebuild after adding a new file, a new launch file or a new `entry_points` line. Changes to an
existing Python file only need a restart of the node (thanks to `--symlink-install`).

## Run a demo

```bash
ros2 launch lecture_demo scan_listener_demo.launch.py
ros2 launch lecture_demo square_driver_demo.launch.py side_length:=1.0
ros2 launch lecture_demo edge_detector_demo.launch.py
ros2 launch lecture_demo complete_initial_demo.launch.py     # everything together
ros2 launch lecture_demo ambulance_world.launch.py           # empty world + ambulance + walking person + waffle (needs internet on 1st run)
```

The YOLO demo (`yolo_detector`) has no launch file: start the simulation, then run the node
(inside Docker: `ros2 run lecture_demo yolo_detector`; on your own Ubuntu see below).

## Do an exercise

Open `lecture_demo/exercise_<name>.py`, complete the `TODO`s, then:

```bash
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py # terminal 1: the simulation
ros2 run lecture_demo exercise_scan_listener # run your node
```

If you are stuck, the finished version is the file without the `exercise_` prefix.

## Install on your own Ubuntu 24.04 (without Docker)

The Docker image already has everything; skip this section if you use it.

With [ROS 2 Jazzy installed](https://docs.ros.org/en/jazzy/Installation.html), let `rosdep`
install every dependency listed in `package.xml` (Gazebo, TurtleBot3, Nav2, OpenCV, ...), then
build:

```bash
source /opt/ros/jazzy/setup.bash
cd ~/ros-workshop/workspace
sudo rosdep init        # first time only (ignore "already initialized")
rosdep update
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

### The YOLO demo needs a Python environment (uv)

`torch` and `ultralytics` cannot be installed by `rosdep`; without them `yolo_detector` fails
with `ModuleNotFoundError: No module named 'ultralytics'`. The other demos do not need this. Create
the environment once:

```bash
# 1. Install uv, then open a new terminal
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Libraries that ultralytics uses, from apt
sudo apt install -y python3-scipy python3-matplotlib python3-yaml python3-pil \
    python3-requests python3-psutil

# 3. Environment that can also see the ROS/apt Python packages (cv_bridge, OpenCV...).
#    --python /usr/bin/python3 makes uv use the system Python, which ROS 2 requires.
uv venv --system-site-packages --python /usr/bin/python3 ~/.venvs/yolo

# 4. CPU-only PyTorch and ultralytics. The constraint keeps the NumPy version that apt
#    installed: cv_bridge is compiled for it and breaks with NumPy 2.
python3 -c "import numpy; print('numpy==' + numpy.__version__)" > /tmp/constraints.txt
uv pip install --python ~/.venvs/yolo -c /tmp/constraints.txt \
    --index-url https://download.pytorch.org/whl/cpu torch torchvision
uv pip install --python ~/.venvs/yolo -c /tmp/constraints.txt --no-deps \
    ultralytics==8.4.210 ultralytics-thop polars
```

Do not use a plain `uv pip install ultralytics`: it would install `opencv-python`, which hides
the system OpenCV that `cv_bridge` needs, and the CUDA build of PyTorch (several GB).

Then, in every terminal where you want to run YOLO (with ROS sourced and the simulation
running), activate the environment and run the file with `python3`:

```bash
cd ~/ros-workshop/workspace
source ~/.venvs/yolo/bin/activate
python3 src/lecture_demo/lecture_demo/yolo_detector.py
```

Use `python3`, not `ros2 run`: `ros2 run` starts nodes with the system Python, which cannot see
the environment. Add options after the file name, e.g. `--ros-args -p conf:=0.5 -p model:=yolo26n.pt`.
The first run downloads the model (`yolo26s.pt`, 20 MB, internet needed) into
`~/.local/share/lecture_demo/models/`; later runs reuse it. Type `deactivate` to leave the environment.
