import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import SetEnvironmentVariable, ExecuteProcess, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch_ros.actions import Node

def generate_launch_description():
    # 1. Setup paths
    pkg_tm20 = get_package_share_directory('tm20')
    
    # Ensure you are using the actual name of your MoveIt config package here.
    # If your package is named differently, update 'tm20_moveit_config'
    pkg_moveit_config = get_package_share_directory('tm20_moveit_config')
    controller_params_file = os.path.join(pkg_moveit_config, 'config', 'ros2_controllers.yaml')

    # Environment variable for Gazebo to find your robot meshes and configs
    resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=[os.path.join(pkg_tm20, '..'), os.path.join(pkg_moveit_config, '..')]
    )

        # ADD THIS NEW BLOCK: Point Gazebo directly to the ROS 2 Jazzy plugin folder
    plugin_path = SetEnvironmentVariable(
        name='GZ_SIM_SYSTEM_PLUGIN_PATH',
        value=[os.environ.get('GZ_SIM_SYSTEM_PLUGIN_PATH', ''), ':/opt/ros/jazzy/lib']
    )

    # Load the Robot Description (URDF)
    urdf_path = os.path.join(pkg_tm20, 'urdf', 'tm20.urdf')
    with open(urdf_path, 'r') as f:
        robot_desc_raw = f.read()

    # Dynamically inject the absolute path into the URDF to prevent Jazzy/Harmonic parser crash
    robot_desc = robot_desc_raw.replace('CONTROLLER_PARAMS_FILE', controller_params_file)
    robot_desc = robot_desc.replace('package://tm20', 'file://' + pkg_tm20)

    # 2. Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='both',
        parameters=[{
            'robot_description': robot_desc,
            'use_sim_time': True
        }]
    )

    # 3. Start Gazebo (Using Harmonic/Gazebo Sim)
    gazebo = ExecuteProcess(
        cmd=['gz', 'sim', '-r', 'empty.sdf'],
        output='screen'
    )

    # 4. Spawn Entity
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'tm20',
            '-topic', 'robot_description',
            '-x', '0', '-y', '0', '-z', '0.1'
        ],
        output='screen',
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

    # 6. Bridge for Clock and Sensors
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/tf@tf2_msgs/msg/TFMessage@gz.msgs.Pose_V',
        ],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    # Return the description with sequenced events
    return LaunchDescription([
        resource_path,
        plugin_path,
        robot_state_publisher,
        gazebo,
        spawn_entity,
        bridge,
        # Sequence: Only start broadcasters after robot is spawned
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=spawn_entity,
                on_exit=[load_joint_state_broadcaster],
            )
        ),
        # Sequence: Only start controllers after broadcasters are active
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=load_joint_state_broadcaster,
                on_exit=[load_tm20_controller],
            )
        ),
    ])