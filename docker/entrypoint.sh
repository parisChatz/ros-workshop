#!/bin/bash
# Runs as root: adapt the 'ros' user to the owner of the bind-mounted workspace
# (avoids permission problems on Linux hosts whose UID is not 1000), then start
# the desktop + editor services under supervisord.
set -e

WS=/home/ros/workspace
mkdir -p "$WS"

HOST_UID=$(stat -c %u "$WS")
HOST_GID=$(stat -c %g "$WS")
CUR_UID=$(id -u ros)
CUR_GID=$(id -g ros)

if [ "$HOST_UID" != "0" ] && { [ "$HOST_UID" != "$CUR_UID" ] || [ "$HOST_GID" != "$CUR_GID" ]; }; then
    [ "$HOST_GID" != "$CUR_GID" ] && groupmod -o -g "$HOST_GID" ros
    [ "$HOST_UID" != "$CUR_UID" ] && usermod -o -u "$HOST_UID" ros
    # fix ownership of the rest of the home directory (not the workspace)
    find /home/ros -xdev -path "$WS" -prune -o -exec chown -h "$HOST_UID:$HOST_GID" {} + 2>/dev/null || true
fi

# stale X locks after a container restart
rm -f /tmp/.X1-lock /tmp/.X11-unix/X1

if [ "$#" -gt 0 ]; then
    exec "$@"
fi
exec /usr/bin/supervisord -n -c /etc/supervisor/supervisord.conf
