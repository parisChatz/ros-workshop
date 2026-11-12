#!/usr/bin/env bash
# Installs the Python packages needed by the yolo_detector node (CPU only) and downloads the
# default YOLO weights. Only needed outside the lecture Docker image (it already has them).
#
# Run it AFTER `rosdep install` (which installs OpenCV/NumPy/cv_bridge from apt):
#   bash install_yolo_deps.sh
#
# Why not simply `pip install ultralytics`?
#   * pip would download the CUDA build of PyTorch (several GB) - we use the CPU build.
#   * ultralytics depends on opencv-python, which needs NumPy 2 and would shadow apt's OpenCV
#     and break cv_bridge (built for NumPy 1.x) - so we install it with --no-deps and reuse the
#     system numpy/opencv/scipy/matplotlib/pillow/yaml.
# Same recipe as the Dockerfile of the lecture image.
set -euo pipefail

MODELS_DIR="${MODELS_DIR:-$HOME/.local/share/lecture_demo/models}"
ULTRALYTICS_VERSION="${ULTRALYTICS_VERSION:-8.4.210}"
MODEL="${MODEL:-yolo26s.pt}"   # the default model of the yolo_detector node
WEIGHTS_URL="https://github.com/ultralytics/assets/releases/download/v8.4.0/$MODEL"

# Ubuntu 24.04 marks the system Python as "externally managed": the flag below allows pip anyway.
PIP=(python3 -m pip install --user --break-system-packages --no-cache-dir --no-warn-script-location)

# Keep the NumPy that apt installed (cv_bridge is compiled against it)
CONSTRAINTS="$(mktemp)"
trap 'rm -f "$CONSTRAINTS"' EXIT
python3 -c "import numpy; print('numpy==' + numpy.__version__)" > "$CONSTRAINTS"

# PyTorch needs a newer typing_extensions than apt's; install it next to apt's copy.
"${PIP[@]}" --ignore-installed --no-deps typing_extensions
"${PIP[@]}" -c "$CONSTRAINTS" --index-url https://download.pytorch.org/whl/cpu torch torchvision
"${PIP[@]}" -c "$CONSTRAINTS" --no-deps "ultralytics==${ULTRALYTICS_VERSION}" ultralytics-thop polars

# Default weights. The node looks for them here (outside Docker) and would otherwise
# download them itself on its first run.
mkdir -p "$MODELS_DIR"
[ -s "$MODELS_DIR/$MODEL" ] || curl -fsSL -o "$MODELS_DIR/$MODEL" "$WEIGHTS_URL"

echo
echo "Done. Weights saved in $MODELS_DIR. Run the node with:"
echo "  ros2 run lecture_demo yolo_detector"
