#!/usr/bin/env bash
source /opt/ros/jazzy/setup.bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/install/setup.bash"

MAP_DIR="$DIR/src/warehouse_robot_navigation/maps"
mkdir -p "$MAP_DIR"

echo "=========================================================="
echo " Saving Warehouse Map to $MAP_DIR/warehouse_map"
echo "=========================================================="

ros2 run nav2_map_server map_saver_cli -f "$MAP_DIR/warehouse_map" --ros-args -p use_sim_time:=true

# Also copy into install directory so it is immediately available
INSTALL_MAP_DIR="$DIR/install/warehouse_robot_navigation/share/warehouse_robot_navigation/maps"
mkdir -p "$INSTALL_MAP_DIR"
cp "$MAP_DIR/warehouse_map"* "$INSTALL_MAP_DIR/" 2>/dev/null || true

echo "Map saved successfully!"
