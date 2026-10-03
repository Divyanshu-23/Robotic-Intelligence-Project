# Autonomous Warehouse Robot

## Objective

Build a fully software-based autonomous warehouse robot
using ROS 2 Jazzy and Gazebo.

## Environment

Ubuntu 24.04
ROS 2 Jazzy
Gazebo Harmonic

## Robot

Differential-drive mobile robot.

Sensors:
- 2D LiDAR
- RGB camera
- wheel odometry

## Required capabilities

1. Robot spawning in Gazebo
2. ROS 2 communication
3. LiDAR sensing
4. Odometry
5. TF tree
6. SLAM
7. Warehouse mapping
8. Autonomous navigation using Nav2
9. Static obstacle avoidance
10. Dynamic obstacle avoidance
11. Warehouse locations
12. Package locations
13. Delivery missions
14. Task management
15. Mission state machine
16. Performance metrics

## Constraints

- Fully software based
- No physical hardware
- ROS 2 Jazzy
- Gazebo
- Python preferred for custom ROS nodes
- Use existing ROS/Nav2 capabilities where appropriate
- Do not unnecessarily reinvent ROS 2/Nav2 functionality

## Development principle

Implement and test one milestone at a time.
Do not move to the next milestone until the current milestone works.