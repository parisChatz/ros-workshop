# ROS 2 Jazzy + TurtleBot3 – Student Tutorial

This tutorial gets you from "nothing installed" to "my own code drives a simulated robot".
Everything (ROS 2 Jazzy, Gazebo, TurtleBot3, Nav2, VS Code) lives in one Docker container.
You only need **Docker** and a **web browser**. It works the same on Windows, macOS and Linux
(Intel/AMD and Apple Silicon).

---

## 1. Install Docker

| Your system | What to install |
|---|---|
| **Windows 10/11** | [Docker Desktop](https://www.docker.com/products/docker-desktop/) (use the WSL 2 backend, the default) |
| **macOS** (Intel or Apple Silicon) | [Docker Desktop](https://www.docker.com/products/docker-desktop/) |
| **Linux** | [Docker Engine](https://docs.docker.com/engine/install/) + the Compose plugin. Then run `sudo usermod -aG docker $USER` and log out/in. |

**Windows:** follow the extra setup in [Windows setup](#windows-setup-wsl-2) below *before* section 2.

Check that it works:

```bash
docker --version
docker compose version
```

**Give Docker enough resources** (Docker Desktop → Settings → Resources): at least
**4 CPUs and 8 GB RAM**. The simulation is rendered in software, so more CPU = smoother.
(On Windows the memory limit is set in `.wslconfig`, see the Windows setup below.)

> The first start builds the image (10-20 minutes, several GB of downloads). Do this **before** the lecture, on a good connection.

## Windows setup (WSL 2)

On Windows, keep the project **inside WSL (Linux)**, not under `C:\...`. It is much faster, and
file permissions and symlinks (needed by `colcon build`) work properly.

1. **Install WSL + Ubuntu.** Open PowerShell **as Administrator** and run:

   ```powershell
   wsl --install
   ```

   Reboot when asked, then open **Ubuntu** from the Start menu and create a username and password.
   (Needs virtualization enabled in the BIOS/UEFI. It normally is. If WSL or Docker says
   "virtualization is disabled", enable it there.)
2. **Install [Docker Desktop](https://www.docker.com/products/docker-desktop/)** with the WSL 2
   backend (the default). Then in Docker Desktop → Settings → Resources → **WSL integration**, switch
   on **Ubuntu**.
3. **Give WSL enough memory.** By default WSL gets half of your RAM, and Docker Desktop's resource
   sliders do not apply to it. In PowerShell:

   ```powershell
   notepad $env:USERPROFILE\.wslconfig
   ```

   Paste this and save (use less than your total RAM; 8 GB needs a laptop with 16 GB):

   ```ini
   [wsl2]
   memory=8GB
   ```

   Then run `wsl --shutdown` and start Docker Desktop again.
4. From now on, run **all commands in the Ubuntu terminal** (not PowerShell). In section 2, clone
   into your Linux home:

   ```bash
   cd ~
   git clone <repo-url> ros-workshop
   cd ros-workshop
   ```

   Do not use the ZIP download on Windows. Open the browser links with `127.0.0.1` instead of
   `localhost` if `localhost` does not load.
5. Your files are at `\\wsl$\Ubuntu\home\<you>\ros-workshop\workspace` in Windows Explorer. VS Code in the
   browser (port 8080) is the easiest way to edit them.

## 2. Get the lecture files and start the environment

1. Get the lecture folder with `git clone <repo-url>` and open a
   terminal in it. **Windows: use the Ubuntu terminal from the Windows setup above.** The folder contains
   `docker-compose.yml` and a `workspace/` folder with the example package `lecture_demo`.
2. Start everything:

   ```bash
   docker compose up -d
   ```

   The first time this builds the image (be patient, watch the progress). Later starts take seconds.
3. Open in your browser:

   | URL | What you get |
   |---|---|
   | <http://localhost:6080/vnc.html> → click **Connect** | A Linux desktop. Gazebo, RViz and terminals appear here. |
   | <http://localhost:8080> | **VS Code** in the browser, opened on your `workspace` folder. |

Useful commands (run in the lecture folder on your own computer):

```bash
docker compose ps          # is it running? (should say "healthy")
docker compose logs -f     # see what is going on
docker compose down        # stop and remove the container (your files are kept)
docker compose up -d       # start again
```

**Where are my files?** Everything inside the container's `~/workspace` is the `workspace/`
folder next to `docker-compose.yml` on your computer. It survives `docker compose down`, and you
may edit those files with any editor on your computer too. Do not put files anywhere else in the
container – they are lost when the container is removed.

## 3. Tour of the environment

In the browser desktop (port 6080) a terminal is already open. Try:

```bash
ros2 --help
echo $TURTLEBOT3_MODEL     # waffle
ros2 pkg list | grep turtlebot3
```

ROS is already sourced in every new terminal. In VS Code (port 8080) use
**Terminal → New Terminal** to get the same environment.

Tip: the browser desktop sometimes steals keyboard shortcuts. Click into the desktop once before
typing, and use the noVNC side panel (little arrow on the left edge) for the clipboard and
full-screen.

## 4. Your first simulation

In a terminal on the desktop:

```bash
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

(or the shortcut `tb3world`). After ~20–40 s a **Gazebo** window with a TurtleBot3 *waffle*
appears. Other worlds: `empty_world.launch.py`, `turtlebot3_house.launch.py` (heavy!).
Change the robot with `export TURTLEBOT3_MODEL=burger` *before* launching.

Open a **second terminal** (right-click desktop → Terminal, or `xfce4-terminal`) and explore:

```bash
ros2 topic list
ros2 topic echo /odom --once          # where does the robot think it is?
ros2 topic echo /scan --once          # lidar
ros2 topic info /cmd_vel              # note the type!
rqt_graph                             # picture of nodes and topics
```

Drive it with the keyboard (stay in this terminal while pressing keys):

```bash
ros2 run turtlebot3_teleop teleop_keyboard      # or: tb3teleop
```

Look at it in **RViz**:

```bash
ros2 run rviz2 rviz2
```

Set *Fixed Frame* to `odom`, then **Add → RobotModel** and **Add → LaserScan** (topic `/scan`).

> **Jazzy gotcha:** in ROS 2 Jazzy the TurtleBot3 simulation expects `geometry_msgs/msg/TwistStamped`
> on `/cmd_vel` (older tutorials use `Twist`). Publish from the command line like this:
>
> ```bash
> ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/TwistStamped \
>   "{header: {frame_id: base_link}, twist: {linear: {x: 0.2}, angular: {z: 0.0}}}"
> ```

Stop things with **Ctrl+C**. Simulation too slow? See [Troubleshooting](#8-troubleshooting).

## 5. Write your first code

An example package, `lecture_demo`, is already in `workspace/src/`. Open it in VS Code
(port 8080) and read it first:

* `lecture_demo/lecture_demo/scan_listener.py` – a **subscriber** (lidar → closest obstacle).
* `lecture_demo/lecture_demo/square_driver.py` – a **publisher** (drives the robot in a square).
* `lecture_demo/lecture_demo/edge_detector.py` – **both**: camera image in, edge image out.
* `lecture_demo/lecture_demo/yolo_detector.py` – a neural network that finds objects in the camera image
  (see "Object detection with YOLO" below).

Every file starts with a comment block explaining what it does, and the code is commented line
by line. The package follows the standard ROS 2 Python layout (the same one
`ros2 pkg create` generates); `workspace/src/lecture_demo/README.md` explains each file and folder.

Build and run it (terminal in `~/workspace`):

```bash
cd ~/workspace
colcon build --symlink-install      # shortcut: cb
source install/setup.bash           # (cb does this too)
```

With the simulation from step 4 still running:

```bash
ros2 run lecture_demo scan_listener
ros2 run lecture_demo square_driver --ros-args -p side_length:=0.5 -p use_sim_time:=true
```

`--symlink-install` means edits to your Python files take effect without rebuilding (restart the
node). You only need to rebuild after adding **new** files, entry points or launch files.

### Create your own package

```bash
cd ~/workspace/src
ros2 pkg create --build-type ament_python --node-name my_node my_robot_pkg
cd ~/workspace && colcon build --symlink-install --packages-select my_robot_pkg
source install/setup.bash
ros2 run my_robot_pkg my_node
```

Edit `my_robot_pkg/my_robot_pkg/my_node.py` in VS Code. Minimal publisher that moves the robot
forward:

```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped


class Forward(Node):
    def __init__(self):
        super().__init__('forward')
        self.pub = self.create_publisher(TwistStamped, 'cmd_vel', 10)
        self.create_timer(0.1, self.tick)

    def tick(self):
        msg = TwistStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.twist.linear.x = 0.1
        self.pub.publish(msg)


def main():
    rclpy.init()
    rclpy.spin(Forward())
```

To register a second node, add a line to `entry_points` → `console_scripts` in `setup.py`:
`'forward = my_robot_pkg.forward:main'`, then rebuild.

### Image processing: edge detection on the camera

`lecture_demo/edge_detector.py` subscribes to `/camera/image_raw`, converts it with `cv_bridge`,
runs OpenCV's Canny edge detector and publishes the result on `/camera/edges`. It is also started
by `complete_initial_demo.launch.py`. Only the **waffle** models have a camera (not `burger`).

```bash
# with the simulation running
ros2 run lecture_demo edge_detector --ros-args -p use_sim_time:=true -p low_threshold:=30 -p high_threshold:=100
ros2 run rqt_image_view rqt_image_view     # pick /camera/image_raw or /camera/edges in the drop-down
```

Drive the robot towards the walls or the coloured pillars to see more edges; an empty view
(sky and floor only) just shows the horizon line. Lower thresholds give more edges.
The camera is 1920x1080, which is heavy in software rendering: expect a few frames per second.

### Object detection with YOLO

Edge detection is a hand-written recipe. **YOLO** is a neural network that has *learned* what
objects look like: it tells you **what** is in the image (person, chair, bus... 80 everyday
classes), **where** (a box) and **how sure** it is (a score from 0 to 1).
`lecture_demo/yolo_detector.py` runs it on `/camera/image_raw` and publishes:

* `/yolo/image` – the camera image with boxes and labels drawn on it
* `/yolo/detections` – the same results as data (`vision_msgs/Detection2DArray`), which other
  nodes could use, e.g. to follow a person

```bash
# with the simulation running
ros2 run lecture_demo yolo_detector --ros-args -p use_sim_time:=true
ros2 run rqt_image_view rqt_image_view     # pick /yolo/image in the drop-down
ros2 topic echo /yolo/detections
```

The default Gazebo world has no real everyday objects, so YOLO may report nothing, or low-score
guesses such as "refrigerator 0.45" for a pillar. Keep only confident detections with
`-p conf:=0.6`. If your computer is slow, make it faster with `-p imgsz:=320`.

Three neural networks are included in `/opt/models/`. The default, `yolo26s`, is the most
accurate. If your computer is slow, `yolo26n` needs about half the computation (`yolo11n` is a
similar, older small one):

```bash
ros2 run lecture_demo yolo_detector --ros-args -p model:=yolo26n.pt
```

**To see YOLO working on real objects**, publish a photo as if it were the robot's camera.
Put a `.jpg` with people, cars, chairs... into your `workspace/` folder, **stop the simulation**
(it also publishes on `/camera/image_raw`) and run:

```bash
ros2 run image_publisher image_publisher_node ~/workspace/my_photo.jpg --ros-args -r image_raw:=/camera/image_raw
ros2 run lecture_demo yolo_detector       # in a second terminal
ros2 run rqt_image_view rqt_image_view    # in a third: pick /yolo/image
```

The `rqt_image_view` window opens small and shows the picture as a thumbnail: **maximise or
resize the window** (title bar buttons, or drag its corner) to see the boxes.

The first run of the node takes a second or two to load the network. It runs on the CPU (no
graphics card needed), so expect a few frames per second next to the simulator.

### Guided exercises: complete the code

For each demo there is an exercise version with a few **TODO**s for you to fill in. Everything
else is already written, and every TODO has hints.

| Exercise file (in `lecture_demo/lecture_demo/`) | You write | Run it with |
|---|---|---|
| `exercise_scan_listener.py` | subscription, filtering the lidar readings, printing the closest one (3 TODOs) | `ros2 run lecture_demo exercise_scan_listener` |
| `exercise_square_driver.py` | publisher, state durations, velocity, publishing (4 TODOs) | `ros2 run lecture_demo exercise_square_driver` |
| `exercise_edge_detector.py` | subscription, grayscale, blur + Canny, publishing the result (4 TODOs) | `ros2 run lecture_demo exercise_edge_detector` |

Workflow:

1. Start the simulation in one terminal: `tb3world`.
2. Open the exercise file in VS Code, read the comment block at the top, and complete the TODOs.
3. In a second terminal run `cb` once (it registers the new `exercise_*` commands), then run your node.
   After that, just save the file and restart the node (Ctrl+C, run again).
4. Stuck? The finished version is the same file without the `exercise_` prefix.

An unfinished exercise runs without errors; it just does not do anything yet. Look for the
`# flake8: noqa` line near the top: it only keeps the code-style checker quiet while you work
and you can delete it when you are done.

### Extra challenges

1. Make `scan_listener` publish `std_msgs/Float32` on `/closest_obstacle`; view it in `rqt_plot`.
2. Make the robot **stop** when something is closer than 0.4 m (subscribe to `/scan`, publish
   to `/cmd_vel` from the same node).
3. Make `square_driver` use `/odom` instead of timers, so the square is more accurate.

## 6. Write and run a launch file

A launch file starts many nodes at once. The package has one launch file per demo, in
`workspace/src/lecture_demo/launch/`. Each one starts the TurtleBot3 world plus that demo, and has
comments explaining every part, so open them in VS Code and read them:

| Launch file | What it shows |
|---|---|
| `scan_listener_demo.launch.py` | **Subscriber**: read the lidar, print the closest obstacle |
| `square_driver_demo.launch.py` | **Publisher**: drive the robot in a square (launch argument `side_length`) |
| `edge_detector_demo.launch.py` | **Image processing**: edges from the camera, shown in `rqt_image_view` (arguments `low_threshold`, `high_threshold`) |
| `complete_initial_demo.launch.py` | **Everything together** (world + all three nodes) |

```bash
# Each launch file starts its own simulation: stop the previous one first (Ctrl+C)
ros2 launch lecture_demo scan_listener_demo.launch.py
ros2 launch lecture_demo square_driver_demo.launch.py side_length:=1.0
ros2 launch lecture_demo edge_detector_demo.launch.py low_threshold:=30
ros2 launch lecture_demo complete_initial_demo.launch.py
ros2 launch lecture_demo square_driver_demo.launch.py --show-args    # list the arguments
```

To add a launch file to **your** package:

1. Create `launch/my.launch.py` in the package.
2. In `setup.py`, make sure `data_files` installs it (copy the `glob('launch/*.launch.py')` line and
   `from glob import glob` from `lecture_demo/setup.py`).
3. `colcon build --symlink-install`, `source install/setup.bash`, `ros2 launch my_robot_pkg my.launch.py`.

Remember `use_sim_time: True` for your nodes when running with Gazebo.

## 7. Optional: Navigation and SLAM

Nav2 and TurtleBot3's navigation/Cartographer packages are installed:

```bash
# terminal 1
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
# terminal 2
ros2 launch turtlebot3_cartographer cartographer.launch.py use_sim_time:=true   # build a map
# terminal 3
ros2 run turtlebot3_teleop teleop_keyboard
```

Save the map with `ros2 run nav2_map_server map_saver_cli -f ~/workspace/my_map`, then use
`ros2 launch turtlebot3_navigation2 navigation2.launch.py use_sim_time:=true map:=$HOME/workspace/my_map.yaml`
and set goals in RViz. This is CPU hungry in software rendering – expect it to be slow.

## 8. Troubleshooting

| Problem | Fix |
|---|---|
| <http://localhost:6080> does not load | `docker compose ps` – is it running/healthy? Wait 20 s after `up`. Port already used? Edit the ports in `docker-compose.yml` (e.g. `"127.0.0.1:6081:6080"`). |
| Desktop is blank/grey | Click **Connect**; reload the page; `docker compose restart`. |
| Gazebo window is black or crashes | Only the GUI is affected, the simulation keeps running. Close the Gazebo window and restart just the GUI with the older renderer: `gz sim -g --render-engine-gui ogre`. |
| Simulation is very slow (real-time factor ≪ 100 %) | Use `empty_world` or `turtlebot3_world`, not `house`. Close RViz/other Gazebo windows. Give Docker more CPUs. Don't resize the Gazebo window to full screen. Lower `VNC_GEOMETRY` in `.env`. |
| `ros2: command not found` | You're in a non-interactive shell. Run `source /opt/ros/jazzy/setup.bash`, or use `docker compose exec -u ros ros bash -l`. |
| Package not found after `colcon build` | Run `source ~/workspace/install/setup.bash` in **that** terminal. |
| Robot does not react to `/cmd_vel` | Wrong message type – use `TwistStamped` (see step 4). |
| `Permission denied` in `workspace/` | On Linux the container adapts to the folder owner automatically; if you created the folder with `sudo`, run `sudo chown -R $USER workspace`. |
| Apple Silicon Mac is slow | The image is built for your machine's architecture automatically (arm64 on Apple Silicon). Make sure Docker Desktop is *not* forced to use Rosetta/amd64 emulation. |
| Start from scratch | `docker compose down` – your `workspace/` stays. To wipe builds: `rm -rf workspace/build workspace/install workspace/log`. |

## 9. Cheat sheet

```bash
# Docker (on your computer, in the lecture folder)
docker compose up -d | down | restart | ps | logs -f
docker compose exec -u ros ros bash        # extra terminal inside the container

# ROS 2 (inside the container)
ros2 node list | info <node>
ros2 topic list | echo <t> | info <t> | hz <t> | pub <t> <type> '<yaml>'
ros2 service list | call <srv> <type> '<yaml>'
ros2 param list | get <node> <p> | set <node> <p> <v>
ros2 interface show geometry_msgs/msg/TwistStamped
ros2 run <pkg> <exe>            ros2 launch <pkg> <file.launch.py>
rqt_graph    rviz2    ros2 bag record -a

# Build
cd ~/workspace && colcon build --symlink-install [--packages-select <pkg>]
source install/setup.bash
```
