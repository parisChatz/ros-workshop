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
│   ├── exercise_scan_listener.py   # the same demos with TODOs for you to complete
│   ├── exercise_square_driver.py
│   └── exercise_edge_detector.py
├── launch/                      # launch files: start the simulation and nodes together
│   ├── scan_listener_demo.launch.py
│   ├── square_driver_demo.launch.py
│   ├── edge_detector_demo.launch.py
│   └── complete_initial_demo.launch.py
└── test/                        # automatic code-style checks
```

## Build

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
```

## Do an exercise

Open `lecture_demo/exercise_<name>.py`, complete the `TODO`s, then:

```bash
tb3world                                     # terminal 1: the simulation
cb                                           # terminal 2: build (first time only)
ros2 run lecture_demo exercise_scan_listener # run your node
```

If you are stuck, the finished version is the file without the `exercise_` prefix.

## Check the code style (optional)

```bash
cd ~/workspace/src/lecture_demo && python3 -m pytest test
```
