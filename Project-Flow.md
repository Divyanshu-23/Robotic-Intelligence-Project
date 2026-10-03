Project: Autonomous Warehouse Robot

Goal: Build a completely software-based autonomous warehouse robot that can navigate a simulated warehouse, avoid obstacles, receive delivery tasks, find destinations, and autonomously deliver packages.

A good final title is:

Simulation-Based Autonomous Warehouse Robot using ROS 2 and Gazebo

The stack I recommend is Ubuntu 24.04 + ROS 2 Jazzy + Gazebo Harmonic + Nav2 + RViz 2 + Python/C++. ROS 2 Jazzy is supported with Gazebo Harmonic, and Nav2 has an official Jazzy simulation workflow.

1. What the final system should look like
                         USER
                           │
                           │ Delivery Task
                           ▼
                  ┌──────────────────┐
                  │  Task Manager    │
                  │     ROS 2 Node   │
                  └────────┬─────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │ Mission Planner  │
                  │   / Decision     │
                  └────────┬─────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │      Nav2        │
                  │                  │
                  │ Global Planner   │
                  │ Local Controller │
                  │ Costmaps         │
                  │ Recovery         │
                  └────────┬─────────┘
                           │
                       /cmd_vel
                           │
                           ▼
              ┌─────────────────────────┐
              │         Gazebo          │
              │                         │
              │   🤖 Mobile Robot       │
              │                         │
              │   LiDAR                 │
              │   Camera                │
              │   Wheel Odometry        │
              └───────────┬─────────────┘
                          │
                     Sensor Data
                          │
                          ▼
              ┌─────────────────────────┐
              │         ROS 2           │
              │ /scan /odom /tf /image  │
              └─────────────────────────┘

Gazebo simulates the robot and environment, while ROS 2 provides the communication and control layer. The ros_gz bridge handles communication between Gazebo Transport and ROS 2 where needed.

2. What you should NOT build initially

Don't start by creating your own robot model, SLAM algorithm, navigation algorithm, physics engine, etc.

You'll get overwhelmed.

Instead:

Use existing robotics infrastructure
Gazebo → physics + simulation
TurtleBot3/differential-drive robot → robot platform
LiDAR → simulated perception
SLAM Toolbox → mapping
Nav2 → navigation
RViz2 → visualization
ROS 2 → communication
You build
Warehouse environment
Warehouse task manager
Package/destination system
Mission logic
Dynamic obstacle scenarios
Performance evaluation
Optional custom behavior tree

That gives you enough original work for a course project.

3. Development environment

I recommend:

OS:       Ubuntu 24.04
ROS:      ROS 2 Jazzy
Gazebo:   Gazebo Harmonic
Language: Python 3 / C++
Visualization: RViz2
Navigation: Nav2
Mapping: SLAM Toolbox
Version Control: Git + GitHub

If you're currently on Windows 11, don't try to install the whole stack directly into Windows.

Use:

Windows 11
    │
    ▼
WSL2
    │
    ▼
Ubuntu 24.04
    │
    ├── ROS 2 Jazzy
    ├── Gazebo Harmonic
    ├── RViz2
    └── Nav2

Gazebo's current documentation specifically notes that Windows support has known runtime issues, while Ubuntu 24.04 has a recommended Gazebo Harmonic configuration for ROS 2 Jazzy.

4. Project folder structure

Eventually, your workspace can look like:

warehouse_ws/
│
├── src/
│   │
│   ├── warehouse_robot_description/
│   │   ├── urdf/
│   │   │   └── warehouse_robot.urdf.xacro
│   │   ├── meshes/
│   │   ├── config/
│   │   ├── launch/
│   │   └── package.xml
│   │
│   ├── warehouse_robot_gazebo/
│   │   ├── worlds/
│   │   │   └── warehouse.world
│   │   ├── models/
│   │   ├── config/
│   │   ├── launch/
│   │   └── package.xml
│   │
│   ├── warehouse_robot_navigation/
│   │   ├── config/
│   │   │   ├── nav2_params.yaml
│   │   │   └── slam_params.yaml
│   │   ├── maps/
│   │   │   └── warehouse_map.yaml
│   │   └── launch/
│   │
│   ├── warehouse_robot_tasks/
│   │   ├── warehouse_robot_tasks/
│   │   │   ├── task_manager.py
│   │   │   ├── mission_planner.py
│   │   │   └── package_manager.py
│   │   ├── config/
│   │   └── launch/
│   │
│   └── warehouse_robot_interfaces/
│       ├── msg/
│       ├── srv/
│       └── action/
│
└── README.md

Don't create all of this on Day 1. We'll build it incrementally.

5. Phase 1 — Learn ROS 2 fundamentals

Before touching your warehouse, learn these:

Nodes
Node A ───────► Node B
Topics
Publisher
    │
    ▼
 /scan
    │
    ▼
Subscriber
Services

Request → Response.

Actions

Actions are particularly important for your project because navigation is naturally goal-oriented:

Go to location X
       ↓
    Running
       ↓
  Feedback
       ↓
   Completed

Nav2 uses ROS interfaces and action servers for navigation tasks.

6. Phase 2 — Get a robot moving in Gazebo

Before making a warehouse, your first milestone is:

Robot successfully moves inside Gazebo through ROS 2 commands.

Start with a standard TurtleBot-style robot.

You'll learn:

Gazebo
  ↓
Robot
  ↓
ROS 2
  ↓
/cmd_vel

For example, conceptually:

/cmd_vel
    ↓
Differential Drive Controller
    ↓
Left wheel + Right wheel
    ↓
Robot moves
Success condition

You should be able to:

Launch Gazebo
      ↓
Spawn robot
      ↓
Run ROS 2 command
      ↓
Robot moves

Do not proceed until this works.

7. Phase 3 — Add simulated sensors

Now give your virtual robot perception.

I'd use:

Primary sensor

2D LiDAR

It publishes something like:

/scan

Conceptually:

                 obstacle
                    █
                    █
                    █
                    │
        \           │           /
         \          │          /
          \         │         /
           \        │        /
            \       │       /
             \      │      /
                 🤖

The LiDAR gives the robot distance measurements.

Also use

Wheel odometry

/odom

And TF:

map
 │
 ▼
odom
 │
 ▼
base_link
 │
 ├── laser
 └── camera

That TF structure is fundamental to ROS navigation. Nav2 documents the map → odom → base_link → sensor frames relationship explicitly.

8. Phase 4 — Build your warehouse

Now create:

        WAREHOUSE

┌──────────────────────────────────┐
│                                  │
│ 📦 📦 📦     SHELF A             │
│                                  │
│ 📦 📦 📦     SHELF B             │
│                                  │
│                                  │
│             🤖                   │
│                                  │
│      📦 📦 📦                    │
│      SHELF C                     │
│                                  │
│                         🏁       │
│                    DELIVERY      │
└──────────────────────────────────┘

Start simple.

Version 1

Only:

floor
walls
3 shelves
robot
destination
Version 2

Add:

10+ shelves
multiple delivery points
static obstacles
Version 3

Add:

moving obstacles
dynamic packages
multiple robots
9. Phase 5 — Mapping

Now the robot should explore the warehouse.

Use:

SLAM Toolbox

The process:

LiDAR
  ↓
SLAM
  ↓
Occupancy Grid
  ↓
Warehouse Map

Your robot doesn't initially know:

"Where am I?"
"What does this warehouse look like?"

SLAM allows it to build a map while estimating its position.

Nav2's documentation identifies SLAM Toolbox as the standard/default supported approach for generating a static map, while AMCL can subsequently localize the robot against a map.

10. Phase 6 — Save the map

Once you've mapped your warehouse:

warehouse_map.yaml
warehouse_map.pgm

Now your robot can use the saved map.

This means you don't need to perform SLAM every time.

Your final workflow becomes:

Warehouse Map
      ↓
Localization
      ↓
Navigation
11. Phase 7 — Nav2

This is where the project becomes a serious robotics project.

Nav2 provides the navigation framework for:

planning
control
localization integration
costmaps
recovery
behaviors

and is specifically designed for autonomous mobile robot navigation.

Conceptually:

              GOAL
                │
                ▼
        ┌──────────────┐
        │ Global       │
        │ Planner      │
        └──────┬───────┘
               │
             PATH
               │
               ▼
        ┌──────────────┐
        │ Local        │
        │ Controller   │
        └──────┬───────┘
               │
           /cmd_vel
               │
               ▼
             ROBOT

Nav2's planner and controller servers are central components of this process.

12. First Nav2 test

Before building your warehouse intelligence, simply make this work:

Robot at A

        A 🤖
         │
         │
         │
         ▼
        B 🏁

Give:

Navigation Goal → B

Robot should autonomously navigate.

This is already provided as an official Nav2 simulation workflow with TurtleBot.

13. Phase 8 — Your actual intelligence layer

Now we start writing your code.

Instead of manually clicking:

"Navigate to this point."

you want:

"Deliver package A12 to Station 3."

Your system translates this high-level instruction into navigation goals.

14. Task Manager

Create:

task_manager.py

It receives:

Package: A12
Destination: Station 3

Then:

Task Manager
     ↓
Find package A12
     ↓
Get package coordinates
     ↓
Send navigation goal
     ↓
Wait
     ↓
Package reached
     ↓
Send destination goal
15. Create a warehouse database

You don't initially need MongoDB/PostgreSQL.

Use YAML or JSON:

warehouse.yaml

Example concept:

packages:

  A12:
    location: [2.5, 4.0]
    destination: station_1

  B21:
    location: [-1.5, 3.0]
    destination: station_2

stations:

  station_1:
    location: [8.0, 2.0]

  station_2:
    location: [-6.0, 4.0]

Your ROS node reads this.

16. Define your own ROS 2 interfaces

This is where you can make the project more sophisticated.

Create:

warehouse_robot_interfaces
Custom message
PackageInfo.msg

Potential fields:

string package_id
string destination_id
float64 x
float64 y
Custom service
RequestDelivery.srv

Conceptually:

Request:
    package_id

Response:
    accepted
    message

Then your system can receive:

Request:
A12

and respond:

Delivery accepted
17. Mission planner

Create:

mission_planner.py

It becomes your high-level brain.

              USER
               │
               ▼
        "Deliver A12"
               │
               ▼
       ┌───────────────┐
       │ Mission       │
       │ Planner       │
       └───────┬───────┘
               │
       ┌───────┴────────┐
       ↓                ↓
Find Package       Find Destination
       │                │
       └───────┬────────┘
               ↓
          Navigation
               ↓
            Nav2
18. Mission state machine

Don't write one giant Python script.

Use states:

IDLE
  ↓
TASK_RECEIVED
  ↓
GO_TO_PACKAGE
  ↓
PACKAGE_REACHED
  ↓
PICKUP_SIMULATION
  ↓
GO_TO_DESTINATION
  ↓
DELIVERY
  ↓
RETURN_TO_BASE
  ↓
COMPLETED

If something goes wrong:

NAVIGATION_FAILED
        ↓
REPLAN
        ↓
NAVIGATE

This is robotic decision-making, rather than simply moving a robot.

19. Dynamic obstacle avoidance

This should be one of your major demonstrations.

Initially:

Robot ───────────────► Destination

Then introduce:

Robot ────── 🚧 ─────► Destination

The robot should detect the obstacle and modify its route.

Nav2's costmaps, planners, controllers and recovery behaviors are designed for this type of navigation.

Your demo can show:

Original path
     ↓
Obstacle appears
     ↓
Costmap updates
     ↓
Path becomes invalid
     ↓
Planner generates new path
     ↓
Robot continues

That is an excellent demonstration for your course.

20. Add a custom Behavior Tree

Once everything works, this is where I'd make the project more advanced.

Nav2 uses Behavior Trees to orchestrate navigation behavior, and they can be customized for application-specific behavior.

Your high-level tree could be:

              DELIVERY
                  │
            Sequence
                  │
        ┌─────────┴─────────┐
        ↓                   ↓
 Navigate           Navigate
 to Package         to Station
        │                   │
   Pickup              Delivery
        │                   │
        └─────────┬─────────┘
                  ↓
             Return Home

And recovery:

Navigation
    │
    ├── Success → Continue
    │
    └── Failure
          ↓
       Recovery
          ↓
       Re-plan
          ↓
       Navigate
21. Optional: simulated pickup

Because you're fully software-based, don't worry about making a real robotic arm.

You can simulate pickup logically.

For example:

Robot reaches package
        ↓
Package status:
AVAILABLE
        ↓
Robot "picks" package
        ↓
Package status:
CARRIED
        ↓
Robot moves
        ↓
Robot reaches station
        ↓
Package status:
DELIVERED

You can even make the package visually attach to the robot in Gazebo later.

22. Optional computer vision

You don't need AI for the core project.

But if your professor expects some perception component, add a simulated camera.

For example:

Camera
   ↓
Image
   ↓
OpenCV
   ↓
Package/marker detection
   ↓
ROS 2
   ↓
Task Manager

You could place ArUco markers on warehouse shelves and have the robot identify them.

That gives you:

Robotics + perception + navigation

without making the project primarily an AI project.

23. Optional multi-robot extension

Only do this after one robot works.

Then:

              Warehouse
                  │
       ┌──────────┼──────────┐
       ↓          ↓          ↓
    Robot 1    Robot 2    Robot 3

Task manager:

Package A → Robot 2
Package B → Robot 1
Package C → Robot 3

Selection could consider:

distance
battery
current task
estimated completion time

For example:

score =
    distance
  + task_time
  + congestion

Then select the robot with the lowest score.

This would turn your project into a multi-agent robotics system.

24. Your final architecture

By the end, aim for:

                    USER
                     │
                     ▼
              ┌──────────────┐
              │ Task Manager │
              └──────┬───────┘
                     │
                     ▼
              ┌──────────────┐
              │Mission Planner│
              └──────┬───────┘
                     │
              ┌──────┴───────┐
              │              │
              ▼              ▼
        Package DB       Robot State
              │              │
              └──────┬───────┘
                     ▼
              ┌──────────────┐
              │     Nav2     │
              │              │
              │ Planner      │
              │ Controller   │
              │ Costmaps     │
              │ BT Navigator │
              └──────┬───────┘
                     │
                  /cmd_vel
                     │
                     ▼
              ┌──────────────┐
              │    Gazebo    │
              │              │
              │ Robot        │
              │ LiDAR        │
              │ Camera       │
              │ Warehouse    │
              └──────┬───────┘
                     │
                 Sensor Data
                     │
                     ▼
                    ROS 2