25. What you should demonstrate to your professor

Your final demo should be a sequence like this:

Demo 1 — Basic robot
Gazebo → Robot → ROS 2 → /cmd_vel
Demo 2 — Perception

Show:

LiDAR → /scan → RViz

Demo 3 — Mapping

Robot explores:

Unknown warehouse
       ↓
      SLAM
       ↓
Completed map

Demo 4 — Autonomous navigation
Give goal
   ↓
Nav2
   ↓
Robot autonomously reaches goal

Demo 5 — Warehouse delivery
Deliver A12 → Station 3

Robot:

Find A12
   ↓
Navigate
   ↓
Pickup
   ↓
Navigate
   ↓
Station 3
   ↓
Deliver

Demo 6 — Dynamic obstacle

Put an obstacle in its route.

Show:

Obstacle detected
       ↓
Replanning
       ↓
New path
       ↓
Successful delivery

Demo 7 — Performance

Report:

Metric	Result
Successful deliveries	X/Y
Average path length	X m
Average mission time	X s
Collision count	X
Replanning events	X
Navigation failures	X