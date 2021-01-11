# DEIS
This repository contains the code for the final project of Group 4 in the "Design of Embedded and Intelligent Systems" - 2020 at Halmstad university. The project evolved around the scenario of a pandemic in 2040 and development of autonomous intelligent vehicle to perform the task on an emergency vehicle. The two core hardware components were a two-wheeled robot and a DJI Ryze Tello drone. 

The effort of our Group was to have the wheeled robot represent an emergency vehicle that can with the help of the drone quickly and safely move through two intersections from point A to point B. More details of the project and the individual parts can be found in our project report.

# Arduino
This folder contains the code controlling the motors of the wheeled robot and interfaces with their encoders and the main controller of the Robot, the Raspberry Pi.

# ArUco
This folder contains code testing the ArUco marker detection as well as a marker generator.

# Camera
This folder contains coder for camera calibration purposes.

# Drone
This folder contains the PID based drone monitor that follows the robot and monitors the intersection. 

# GPS
This folder contains the dev version of the ArUco based GPS implementation.

# Intersection
This folder contains the code running the intersection monitor. It is separated into sub-folders containing code for a simple implementation without ROS2 integration and two different ROS2 versions. The first one only monitors the intersection, publishing the status to everyone, while the second one monitors and checks for the presence of our robot and then sends it move or stop commands. 

# Raspberry Pi
This folder contains the code running on the Rapsberry Pi main Controller of the Robot and is responsible for communicating with the Arduino, the GPS camera to obtain location info and the Intersection manager via ROS2.