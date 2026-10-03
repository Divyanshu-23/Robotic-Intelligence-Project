#!/usr/bin/env bash
source /opt/ros/jazzy/setup.bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/install/setup.bash"

echo "=========================================================="
echo " Starting SLAM Mapping Session (Gazebo + SLAM Toolbox + RViz)"
echo " Drive the robot using ./teleop.sh to explore the warehouse."
echo " When finished, run ./save_map.sh in another terminal."
echo "=========================================================="

ros2 launch warehouse_robot_navigation slam.launch.py headless:=false rviz:=true
