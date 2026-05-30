cmake_minimum_required(VERSION 3.8)
project(tm20_perception)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(tf2 REQUIRED)
find_package(pcl_ros REQUIRED)
find_package(pcl_conversions REQUIRED)
find_package(PCL REQUIRED)

include_directories(${PCL_INCLUDE_DIRS})

add_executable(pcl_filter_node src/pcl_filter_node.cpp)
ament_target_dependencies(pcl_filter_node
  rclcpp sensor_msgs pcl_ros pcl_conversions tf2_ros tf2
)
target_link_libraries(pcl_filter_node ${PCL_LIBRARIES})

# Install C++ node
install(TARGETS pcl_filter_node
  DESTINATION lib/${PROJECT_NAME}
)

# Install Python node
install(PROGRAMS
  object_detector.py
  DESTINATION lib/${PROJECT_NAME}
)

# Install launch and config
install(DIRECTORY launch config
  DESTINATION share/${PROJECT_NAME}
)

ament_package()