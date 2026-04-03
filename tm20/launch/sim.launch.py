import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import SetEnvironmentVariable, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_tm20 = get_package_share_directory('tm20')

    resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=[os.path.join(pkg_tm20, '..')]
    )

    with open(os.path.join(pkg_tm20, 'urdf', 'tm20.urdf'), 'r') as f:
        robot_desc = f.read()

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='both',
        parameters=[{
            'robot_description': robot_desc,
            'use_sim_time': True
        }]
    )

    # 2. Start Gazebo Harmonic (Empty World)
    gazebo = ExecuteProcess(
        cmd=['gz', 'sim', '-r', os.path.join(pkg_share, 'worlds', 'pick_place.sdf')],
        output='screen'
    )

    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'tm20',
            '-topic', 'robot_description',
            '-x', '0', '-y', '0', '-z', '0.1'
        ],
        output='screen',
    )

    # 5. Load the tm20 Trajectory Controller
    load_tm20_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['tm20_controller'],
        output='screen',
    )

    camera_tf_node = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='camera_link_broadcaster',
        arguments=[
            '0', '0', '0',
            '0', '0', '0',
            'link_6',
            'tm20/link_5/intel_d435'
        ],
    )

    # Sequence the spawners so they don't crash before the robot exists
    return LaunchDescription([
        resource_path,
        robot_state_publisher,
        gazebo,
        spawn_entity,
        camera_tf_node,
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
                '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
                '/tf@tf2_msgs/msg/TFMessage@gz.msgs.Pose_V',
                '/camera/depth_image/points@sensor_msgs/msg/PointCloud2@gz.msgs.PointCloudPacked',
                '/camera/depth_image/camera_info@sensor_msgs/msg/CameraInfo@gz.msgs.CameraInfo',
                '/camera/depth_image/image@sensor_msgs/msg/Image@gz.msgs.Image',
            ],
            parameters=[{'use_sim_time': True}],
            output='screen'
        )
    ])