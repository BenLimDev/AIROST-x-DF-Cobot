from moveit_configs_utils import MoveItConfigsBuilder
from moveit_configs_utils.launches import generate_move_group_launch
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    moveit_config = (
        MoveItConfigsBuilder("tm20", package_name="tm20_moveit_config")
        .trajectory_execution(file_path="config/moveit_controllers.yaml")
        .to_moveit_configs()
    )
    moveit_config.moveit_cpp.update({"use_sim_time": True})
    return generate_move_group_launch(moveit_config)
