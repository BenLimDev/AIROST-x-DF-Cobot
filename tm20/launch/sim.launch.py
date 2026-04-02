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

    # 2. Gazebo Bridge (THIS IS THE CLOCK FIX)
    # This connects Gazebo's internal clock to ROS 2
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
        output='screen'
    )
    
    # 1. Robot State Publisher
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description, {'use_sim_time': True}]
    )



    # 3. Start Gazebo Harmonic (Empty World)
    # The '-r' flag tells Gazebo to start running immediately
    gazebo = ExecuteProcess(
        cmd=['gz', 'sim', '-r', 'empty.sdf'],
        output='screen'
    )

    # 4. Spawn the Robot in Gazebo
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-string', doc.toxml(),
                   '-name', 'tm20',
                   '-allow_renaming', 'true'],
        output='screen'
    )

    # 5. Load Joint State Broadcaster
    load_joint_state_broadcaster = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster', '--param-file', os.path.join(pkg_share, 'config', 'joint_names_tm20.yaml')],
        output='screen',
    )

    # 6. Load the tm20 Trajectory Controller
    load_tm20_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['tm20_controller', '--param-file', os.path.join(pkg_share, 'config', 'joint_names_tm20.yaml')],
        output='screen',
    )

    # Final list of things to launch
    return LaunchDescription([
        node_robot_state_publisher,
        bridge,  # <--- Added the bridge here!
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
        )
    ])