# TM20 Cobot Simulation Package

This package contains the URDF, meshes, textures, and launch files for the TM20 robot simulation in ROS 2 Jazzy and Gazebo Harmonic.

## 🛠️ Prerequisites
Ensure you have the following installed:
* **ROS 2 Jazzy**
* **Gazebo Harmonic**
* **Colcon** build tools

## 🏗️ Building the Package

1. Navigate to your ROS 2 workspace:
   ```bash
   cd ~/ros2_ws

    If you previously had issues or old builds, clear the cache first:
    Bash

    rm -rf build/tm20 install/tm20

    Build the package:
    Bash

    colcon build --packages-select tm20

🚀 Running the Simulation

Every time you open a new terminal to run this simulation, you must export the resource path so Gazebo can find the 3D meshes and textures.

    Source the workspace and export the mesh paths:
    Bash

    cd ~/ros2_ws
    source install/setup.bash
    export GZ_SIM_RESOURCE_PATH=$COLCON_PREFIX_PATH/tm20/share

    Launch the robot in Gazebo:
    Bash

    ros2 launch tm20 sim.launch.py

📁 Package Structure

    urdf/: Contains the tm20.urdf robot description.

    meshes/: Contains the .STL 3D model files.

    textures/: Contains the visual skins/images for the robot.

    launch/: Contains the ROS 2 Python launch files.

    config/: Configuration files for the simulation.


---
