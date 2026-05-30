import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import SetEnvironmentVariable, ExecuteProcess, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch_ros.actions import Node

def generate_launch_description():
    # 1. Setup paths
    pkg_tm20 = get_package_share_directory('tm20')
    pkg_moveit_config = get_package_share_directory('tm20_moveit_config')
    
    # Path to your saved RViz config
    rviz_config_path = os.path.join(pkg_tm20, 'rviz', 'camera_view.rviz')
    
    controller_params_file = os.path.join(pkg_moveit_config, 'config', 'ros2_controllers.yaml')

    # Environment variables
    resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=[os.path.join(pkg_tm20, '..'), os.path.join(pkg_moveit_config, '..')]
    )

    plugin_path = SetEnvironmentVariable(
        name='GZ_SIM_SYSTEM_PLUGIN_PATH',
        value=[os.environ.get('GZ_SIM_SYSTEM_PLUGIN_PATH', ''), ':/opt/ros/jazzy/lib']
    )

    # Load the Robot Description (URDF)
    urdf_path = os.path.join(pkg_tm20, 'urdf', 'tm20.urdf')
    with open(urdf_path, 'r') as f:
        robot_desc_raw = f.read()

    robot_desc = robot_desc_raw.replace('CONTROLLER_PARAMS_FILE', controller_params_file)
    robot_desc = robot_desc.replace('package://tm20', 'file://' + pkg_tm20)

    # 2. Nodes
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='both',
        parameters=[{'robot_description': robot_desc, 'use_sim_time': True}]
    )

    gazebo = ExecuteProcess(
        cmd=['gz', 'sim', '-r', 'empty.sdf'],
        output='screen'
    )

    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-name', 'tm20', '-topic', 'robot_description', '-x', '0', '-y', '0', '-z', '0.1'],
        output='screen',
    )

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/tf@tf2_msgs/msg/TFMessage@gz.msgs.Pose_V',
            '/camera/depth_image/points@sensor_msgs/msg/PointCloud2@gz.msgs.PointCloudPacked',
            '/camera/depth_image/camera_info@sensor_msgs/msg/CameraInfo@gz.msgs.CameraInfo',
            '/camera/depth_image/image@sensor_msgs/msg/Image@gz.msgs.Image',
        ],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )
    
    # 3. Static Transform for Camera
    # NOTE: I adjusted the rotation to 1.67 (approx 95.7 deg) on X to help point the cloud forward
    camera_tf_node = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='camera_link_broadcaster',
        arguments=['0', '0', '0', '0', '-1.67', '-1.67', 'link_6', 'tm20/link_5/intel_d435'],
    )

    # 4. RViz Node
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_path],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    # 5. Controller Spawners
    load_joint_state_broadcaster = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster'],
        output='screen',
    )

    load_tm20_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['tm20_controller'],
        output='screen',
    )

    return LaunchDescription([
        resource_path,
        plugin_path,
        robot_state_publisher,
        gazebo,
        spawn_entity,
        bridge,
        camera_tf_node, 
        rviz_node,  # Added RViz here!
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=spawn_entity,
                on_exit=[load_joint_state_broadcaster],
            )
        ),
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=load_joint_state_broadcaster,
                on_exit=[load_tm20_controller],
            )
        ),
    ])