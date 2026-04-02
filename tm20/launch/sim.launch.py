import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import xacro

def generate_launch_description():
    package_name = 'tm20'
    pkg_share = get_package_share_directory(package_name)
    
    # Process the URDF file
    urdf_file = os.path.join(pkg_share, 'urdf', 'tm20.urdf')
    doc = xacro.process_file(urdf_file)
    robot_description = {'robot_description': doc.toxml()}

    # 1. Robot State Publisher
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description, {'use_sim_time': True}]
    )

    # 2. Start Gazebo Harmonic (Empty World)
    gazebo = ExecuteProcess(
        cmd=['gz', 'sim', '-r', 'empty.sdf'],
        output='screen'
    )

    # 3. Spawn the Robot in Gazebo
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-string', doc.toxml(),
                   '-name', 'tm20',
                   '-allow_renaming', 'true'],
        output='screen'
    )

    # 4. Load Joint State Broadcaster
    load_joint_state_broadcaster = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster'],
        output='screen',
    )

    # 5. Load the tm20 Trajectory Controller
    load_tm20_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['tm20_controller'],
        output='screen',
    )

    # Sequence the spawners so they don't crash before the robot exists
    return LaunchDescription([
        node_robot_state_publisher,
        gazebo,
        spawn_entity,
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
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=[
                '/camera/depth_image/points@sensor_msgs/msg/PointCloud2@gz.msgs.PointCloudPacked',
                '/camera/depth_image/camera_info@sensor_msgs/msg/CameraInfo@gz.msgs.CameraInfo',
                '/camera/depth_image/image@sensor_msgs/msg/Image@gz.msgs.Image',
            ],
            parameters=[{'use_sim_time': True}],
            output='screen'
        )
    ])