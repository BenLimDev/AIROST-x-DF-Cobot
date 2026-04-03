# AIROST X DF COBOT PROJECT

## TM20 Robotic Arm Simulation (ROS 2 Jazzy + Gazebo Harmonic)
This repository contains the ROS 2 packages and MoveIt 2 configurations for simulating a Techman Robot TM20 (with a depth camera mount) using Gazebo Harmonic and `ros2_control`. 

## 📋 Prerequisites

Before cloning this repository, ensure your system meets the following requirements:
* **OS:** Ubuntu 24.04 LTS
* **ROS Version:** [ROS 2 Jazzy Jalisco](https://docs.ros.org/en/jazzy/Installation.html)
* **Gazebo Version:** Gazebo Harmonic (default for ROS 2 Jazzy)

You must also have the core ROS 2 development tools installed:
```bash
sudo apt update
sudo apt install python3-colcon-common-extensions python3-vcstool python3-rosdep2 git
```

## 🛠️ Installation & Setup

**1. Create a ROS 2 Workspace**
```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
```

**2. Clone the Repository**
```bash
git clone [https://github.com/BenLimDev/AIROST-x-DF-Cobot.git] .
```

**3. Install Dependencies using `rosdep`**
It is highly recommended to use `rosdep` to automatically fetch the required ROS 2 packages (like MoveIt, `ros_gz_bridge`, and `gz_ros2_control`).
```bash
cd ~/ros2_ws
sudo rosdep init # (Skip if you've already done this in the past)
rosdep update
rosdep install --from-paths src --ignore-src -r -y
```

**4. Build the Workspace**
```bash
cd ~/ros2_ws
colcon build --symlink-install
```
*(Note: `--symlink-install` is recommended so you don't have to rebuild every time you tweak a python script or YAML file).*

**5. Source the Workspace**
```bash
source install/setup.bash
```
*Tip: Add `source ~/ros2_ws/install/setup.bash` to your `~/.bashrc` to do this automatically in every new terminal.*

## 🚀 Running the Simulation

### 1. Launch Gazebo and the Robot Controllers
This launch file starts Gazebo Harmonic, spawns the TM20 robot, and activates the `joint_state_broadcaster` and `tm20_controller` via `ros2_control`.

```bash
ros2 launch tm20 sim.launch.py
```

### 2. Launch MoveIt 2 and RViz (In a new terminal)
Once Gazebo is running and the controllers are active, open a new terminal, source the workspace, and launch your MoveIt configuration to start planning trajectories:

```bash
cd ~/ros2_ws
source install/setup.bash
# Replace this with the actual name of your MoveIt launch file if different
ros2 launch tm20_moveit_config demo.launch.py use_sim_time:=true
```

## 🏗️ Package Architecture

* **`tm20`**: Contains the URDF, robot meshes (`.STL` files), and the main simulation launch file (`sim.launch.py`).
* **`tm20_moveit_config`**: Contains the MoveIt 2 configuration, semantic robot description (SRDF), kinematics, and the `ros2_controllers.yaml` file.

## ⚠️ Notes on the Implementation

* **Dynamic URDF Parsing:** To circumvent a known URDF parser limitation in ROS 2 Jazzy when linking YAML parameters to the Gazebo system plugin, `sim.launch.py` dynamically injects the absolute path to `ros2_controllers.yaml` into the URDF at runtime.
* **Mesh Resolution:** The simulation launch file automatically sets `GZ_SIM_RESOURCE_PATH` to ensure Gazebo Harmonic natively resolves `package://` mesh URIs without requiring a standalone `model.config` setup.
* **Fixed Joints:** Link 6 is intentionally defined as a `fixed` joint to act as a mount for the depth camera and is excluded from the `tm20_controller` joint list to prevent hardware activation crashes.
```