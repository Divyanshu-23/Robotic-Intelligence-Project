#!/usr/bin/env bash
source /opt/ros/jazzy/setup.bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/install/setup.bash"

echo "=========================================================="
echo " Starting Nav2 Autonomous Warehouse Navigation"
echo " Use the '2D Goal Pose' button in RViz to send navigation goals."
echo "=========================================================="

ros2 launch warehouse_robot_navigation navigation.launch.py headless:=false rviz:=true
