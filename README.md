# ROS 2 Jazzy lecture environment

One Docker image with **ROS 2 Jazzy**, **Gazebo Harmonic**, **TurtleBot3** (+ simulations, Nav2,
Cartographer), **RViz2**, and **VS Code in the browser**. A full Linux desktop is served through
noVNC, so the same setup runs on Windows, macOS and Linux (amd64 and arm64) with no GPU or X server
configuration.

**Students → read [TUTORIAL.md](TUTORIAL.md).** Short version:

```bash
docker compose up -d
# desktop:  http://localhost:6080/vnc.html   (click Connect)
# VS Code:  http://localhost:8080
```

Your code lives in `./workspace` (bind-mounted to `~/workspace` in the container).

## Layout

| Path | Purpose |
|---|---|
| `Dockerfile` | The image (base `ros:jazzy-ros-base`) |
| `docker-compose.yml`, `.env` | Run configuration (ports bound to localhost only) |
| `docker/` | supervisord config (Xvnc, XFCE, noVNC, code-server), entrypoint, shell setup |
| `workspace/src/lecture_demo/` | Example package: subscriber, publisher, launch file |
| `.github/workflows/build.yml` | Optional manual CI build check (amd64 + arm64) |
| `Makefile` | `build`, `up`, `down`, `shell`, `push` |

## Distribution

Students `git clone` this repo (or download the ZIP) and run `docker compose up -d`. The first run
builds the image from the `Dockerfile` on their own machine (10-20 min, ~10 GB of downloads); later
runs reuse it. No registry is involved.

* Ask students to do the first run **before** the session, on a good connection, not on venue wifi.
* Instructor shortcuts: `make build`, `make up`, `make shell`.
* Optional: `.github/workflows/build.yml` (manual run only) builds amd64 and arm64 natively on GitHub
  runners, a cheap way to check that the image builds on both architectures. It also publishes to GHCR,
  which you can ignore, or use later to switch students to a prebuilt image.

## Things worth knowing

* **Rendering is software only** (Mesa llvmpipe). It works everywhere but Gazebo runs at roughly
  a third of real time for `turtlebot3_world` on a desktop CPU. Prefer `empty_world`/`turtlebot3_world`;
  `turtlebot3_house` is heavy.
* **Jazzy TurtleBot3 uses `TwistStamped` on `/cmd_vel`**, not `Twist`. The tutorial and the sample
  package already account for this.
* Ports are bound to `127.0.0.1`; code-server and VNC run **without authentication**. Do not publish
  them on a network interface.
* Linux hosts: the entrypoint remaps the `ros` user to the owner of `./workspace`, so files are not
  root-owned on the host.
* Optional Linux/NVIDIA acceleration is intentionally not part of the default setup.

## Verified

On amd64: image builds; `docker compose up` becomes healthy; ports 6080/8080 respond;
`colcon build` of `lecture_demo` works; `ros2 launch lecture_demo complete_initial_demo.launch.py` starts Gazebo
(GUI visible in the noVNC desktop), `/odom` changes and `/scan` is received.
**Not yet tested:** an actual arm64 image build/run (no qemu on the authoring machine); all ROS apt
packages and the code-server release used are published for arm64.
