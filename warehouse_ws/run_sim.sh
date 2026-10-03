#!/usr/bin/env bash
# Source ROS 2 Jazzy and the workspace
source /opt/ros/jazzy/setup.bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/install/setup.bash"

echo "=========================================================="
echo " Starting Autonomous Warehouse Robot Simulation (Gazebo Harmonic)"
echo "=========================================================="

ros2 launch warehouse_robot_gazebo warehouse_sim.launch.py headless:=false rviz:=true
