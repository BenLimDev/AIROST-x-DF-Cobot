cmake_minimum_required(VERSION 3.8)
project(tm20)

# 1. Find ROS 2 Build Tools
find_package(ament_cmake REQUIRED)

# 2. Install Directories (This makes them available in the 'install' folder)
install(DIRECTORY
  config
  launch
  meshes
  urdf
  DESTINATION share/${PROJECT_NAME}
)

# 3. Export the package for ROS 2
ament_package()
