from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    # systemkeyboarcontrol = Node(
    #     package="system_py_hss", executable="systemkeyboarcontrol",
    #     name="systemkeyboarcontrol", output="screen"
    # )
    # trajctorypublisher = Node(
    #     package="system_py_hss", executable="trajctorypublisher",
    #     name="trajctorypublisher", output="screen"
    # )
    image_prossising_node = Node(
        package="system_py_hss", executable="image_prossising_node",
        name="image_prossising_node", output="screen", 
    )
    move_system_to_target = Node(
        package="system_py_hss", executable="move_system_to_target",
        name="move_system_to_target", output="screen"
    )
    dual_pid_controller = Node(
        package="system_py_hss", executable="dual_pid_controller",
        name="dual_pid_controller", output="screen", 
    )

    return LaunchDescription([dual_pid_controller, 
                              move_system_to_target, 
                              image_prossising_node,
                            #   trajctorypublisher,
                            #   systemkeyboarcontrol,
                              ])