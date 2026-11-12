# ROS 2 Jazzy + Gazebo (Harmonic) + TurtleBot3 lecture image
# Browser desktop (noVNC) on :6080, VS Code (code-server) on :8080.
# Multi-arch: linux/amd64, linux/arm64.
FROM ros:jazzy-ros-base

ARG DEBIAN_FRONTEND=noninteractive
ARG USERNAME=ros
ARG USER_UID=1000
ARG USER_GID=1000
# Leave empty for the latest code-server release, or pin e.g. 4.96.4
ARG CODE_SERVER_VERSION=

# ---------------------------------------------------------------- ROS packages
RUN apt-get update && apt-get install -y --no-install-recommends \
        ros-jazzy-desktop \
        ros-jazzy-ros-gz \
        ros-jazzy-turtlebot3 \
        ros-jazzy-turtlebot3-simulations \
        ros-jazzy-nav2-bringup \
        ros-jazzy-teleop-twist-keyboard \
        ros-jazzy-image-publisher \
        python3-colcon-common-extensions \
        python3-rosdep \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*

# ---------------------------------------- Desktop (VNC + noVNC), software GL
RUN apt-get update && apt-get install -y --no-install-recommends \
        tigervnc-standalone-server tigervnc-common \
        novnc websockify \
        xfce4 xfce4-terminal thunar \
        dbus-x11 x11-xserver-utils xdg-utils \
        adwaita-icon-theme fonts-dejavu-core \
        libgl1-mesa-dri libglx-mesa0 libegl1 mesa-utils \
        supervisor sudo curl ca-certificates git nano vim less locales \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /usr/share/novnc/vnc.html /usr/share/novnc/index.html

# ----------------------------------------------------------------- code-server
RUN curl -fsSL https://code-server.dev/install.sh \
      | sh -s -- ${CODE_SERVER_VERSION:+--version ${CODE_SERVER_VERSION}} \
    && rm -rf /var/lib/apt/lists/* /tmp/*

# ------------------------------------------- YOLO object detection (CPU only)
# Used by lecture_demo/yolo_detector.py. Why it is installed this way:
#  * PyTorch comes from the CPU-only wheel index: the default amd64 wheel bundles CUDA (+GBs).
#  * ultralytics is installed with --no-deps ON PURPOSE. Its requirements include opencv-python,
#    which needs NumPy 2 in current releases and would shadow apt's OpenCV and break cv_bridge
#    (compiled for NumPy 1.x). We reuse the apt numpy/opencv/scipy/matplotlib/pillow/yaml/...
#  * numpy is pinned to the apt version with a constraints file so nothing can upgrade it.
#  * typing_extensions: apt's copy has no pip RECORD file, so pip cannot uninstall it; put a
#    newer one next to it first.
#  * The weights are baked in (pinned release URL), so students need no internet at runtime.
#  * The last line fails the build if cv_bridge, torch or the model stop working together.
RUN python3 -c "import numpy; print('numpy==' + numpy.__version__)" > /tmp/constraints.txt \
    && pip install --break-system-packages --no-cache-dir --ignore-installed --no-deps \
        typing_extensions \
    && pip install --break-system-packages --no-cache-dir -c /tmp/constraints.txt \
        --index-url https://download.pytorch.org/whl/cpu torch torchvision \
    && pip install --break-system-packages --no-cache-dir -c /tmp/constraints.txt --no-deps \
        ultralytics==8.4.210 ultralytics-thop polars \
    && mkdir -p /opt/models \
    && curl -fsSL -o /opt/models/yolo11n.pt \
        https://github.com/ultralytics/assets/releases/download/v8.4.0/yolo11n.pt \
    && . /opt/ros/jazzy/setup.sh \
    && python3 -c "import numpy, cv_bridge, torch; from ultralytics import YOLO; \
YOLO('/opt/models/yolo11n.pt'); assert numpy.__version__.startswith('1.')" \
    && rm -rf /tmp/constraints.txt /root/.config/Ultralytics

# The node's default is yolo26s (more accurate). yolo26n needs about half the CPU time, for
# students whose computers are slow; use it with:
#   ros2 run lecture_demo yolo_detector --ros-args -p model:=yolo26n.pt
# Separate layer so changing the model list does not re-download PyTorch.
RUN curl -fsSL -o /opt/models/yolo26n.pt \
        https://github.com/ultralytics/assets/releases/download/v8.4.0/yolo26n.pt \
    && curl -fsSL -o /opt/models/yolo26s.pt \
        https://github.com/ultralytics/assets/releases/download/v8.4.0/yolo26s.pt \
    && . /opt/ros/jazzy/setup.sh \
    && python3 -c "from ultralytics import YOLO; YOLO('/opt/models/yolo26n.pt'); YOLO('/opt/models/yolo26s.pt')" \
    && rm -rf /root/.config/Ultralytics

# ------------------------------------------------------------------ User setup
# Ubuntu 24.04 images ship a default 'ubuntu' user on UID 1000; replace it.
RUN (userdel -r ubuntu 2>/dev/null || true) \
    && groupadd --gid ${USER_GID} ${USERNAME} \
    && useradd --uid ${USER_UID} --gid ${USER_GID} -m -s /bin/bash ${USERNAME} \
    && echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/${USERNAME} \
    && chmod 0440 /etc/sudoers.d/${USERNAME} \
    && mkdir -p /tmp/.X11-unix && chmod 1777 /tmp/.X11-unix \
    && mkdir -p /home/${USERNAME}/workspace \
    && chown -R ${USER_UID}:${USER_GID} /home/${USERNAME}

# code-server extensions (best effort: Open VSX may be unreachable at build time)
USER ${USERNAME}
RUN code-server --install-extension ms-python.python || true
USER root

COPY docker/bashrc.append /tmp/bashrc.append
RUN sed -i 's/\r$//' /tmp/bashrc.append \
    && cat /tmp/bashrc.append >> /home/${USERNAME}/.bashrc \
    && cp /tmp/bashrc.append /etc/profile.d/ros-lecture.sh \
    && rm /tmp/bashrc.append
COPY docker/supervisord.conf /etc/supervisor/conf.d/lecture.conf
COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
COPY docker/autostart-terminal.desktop /home/${USERNAME}/.config/autostart/terminal.desktop
# Windows safety net: strip CRLF line endings from files copied in from the host
RUN sed -i 's/\r$//' /usr/local/bin/entrypoint.sh /etc/supervisor/conf.d/lecture.conf \
        /home/${USERNAME}/.config/autostart/terminal.desktop \
    && chmod +x /usr/local/bin/entrypoint.sh \
    && chown -R ${USER_UID}:${USER_GID} /home/${USERNAME}/.config

ENV TURTLEBOT3_MODEL=waffle \
    ROS_DOMAIN_ID=30 \
    RMW_IMPLEMENTATION=rmw_fastrtps_cpp \
    DISPLAY=:1 \
    LIBGL_ALWAYS_SOFTWARE=1 \
    QT_X11_NO_MITSHM=1 \
    VNC_GEOMETRY=1600x900 \
    YOLO_AUTOINSTALL=False \
    LANG=C.UTF-8

WORKDIR /home/${USERNAME}/workspace
EXPOSE 6080 8080
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
