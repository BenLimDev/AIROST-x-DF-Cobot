from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    pkg_share = get_package_share_directory('tm20_perception')
    params_file = os.path.join(pkg_share, 'config', 'filter_params.yaml')

    pcl_filter_node = Node(
        package='tm20_perception',
        executable='pcl_filter_node',
        name='pcl_filter_node',
        parameters=[params_file],
        output='screen'
    )

    object_detector_node = Node(
        package='tm20_perception',
        executable='object_detector.py',
        name='object_detector',
        output='screen'
    )

    return LaunchDescription([
        pcl_filter_node,
        object_detector_node,
    ])