#!/usr/bin/env bash
source /opt/ros/jazzy/setup.bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/install/setup.bash"

echo "=========================================================="
echo " Teleop Control for Warehouse Robot"
echo " Use i/k to move forward/backward, j/l to turn, space to stop"
echo "=========================================================="

ros2 run teleop_twist_keyboard teleop_twist_keyboard
