Break the project into independent milestones.

Stage 1:

ROS 2 workspace
      ↓
Robot package
      ↓
Gazebo
      ↓
Robot spawns

Stage 2:

Robot
 ├── LiDAR
 ├── Camera
 └── Odometry

Stage 3:

SLAM
 ↓
Warehouse map

Stage 4:

Nav2
 ↓
Autonomous navigation

Stage 5:

Warehouse
 ↓
Packages
 ↓
Delivery missions

Stage 6:
Task Manager
 ↓
Mission Planner
 ↓
Nav2

Stage 7:

Dynamic obstacles
 ↓
Replanning

Stage 8:

Multiple robots
 ↓
Task allocation
 ↓
Collision avoidance