from moveit_configs_utils import MoveItConfigsBuilder
from moveit_configs_utils.launches import generate_moveit_rviz_launch

def generate_launch_description():
    moveit_config = (
        MoveItConfigsBuilder("tm20", package_name="tm20_moveit_config")
        .to_moveit_configs()
    )
    moveit_config.moveit_cpp.update({"use_sim_time": True})
    return generate_moveit_rviz_launch(moveit_config)
