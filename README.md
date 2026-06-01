# system_py_hss

A Python-based ROS 2 control and algorithms package for the `system_hss` robot.  
It contains nodes for keyboard teleoperation, trajectory publishing, image processing, target-reaching motion, and PID control.

> This package is designed to be used together with [`system_hss`](https://github.com/Qaroom/system_hss) (the URDF + Gazebo + `ros2_control` simulation package).

## Nodes

| Command | Description |
|---|---|
| `systemkeyboarcontrol` | Manual control of the robot via keyboard teleoperation |
| `trajctorypublisher` | Publishes joint trajectories (`JointTrajectory`) |
| `image_prossising_node` | Image-processing node that consumes camera frames |
| `move_system_to_target` | Drives the robot to a given target point |
| `dual_pid_controller` | PID controller for two independent axes |

## Structure

```
system_py_hss/
├── launch/            # ROS 2 launch files
├── resource/          # ament_python resource marker
├── system_py_hss/     # Python source code (nodes)
├── test/              # Lint and unit tests
├── package.xml
├── setup.cfg
└── setup.py
```

## Installation

Clone the package into a ROS 2 workspace and build it:

```bash
cd ~/ros2_ws/src
git clone https://github.com/Qaroom/system_py_hss.git
cd ~/ros2_ws
colcon build --packages-select system_py_hss
source install/setup.bash
```

## Usage

To run individual nodes:

```bash
ros2 run system_py_hss systemkeyboarcontrol
ros2 run system_py_hss trajctorypublisher
ros2 run system_py_hss image_prossising_node
ros2 run system_py_hss move_system_to_target
ros2 run system_py_hss dual_pid_controller
```

Or start multiple nodes together using a launch file from the `launch/` folder:

```bash
ros2 launch system_py_hss <launch_file>.launch.py
```

For a full scenario, first bring up the simulation with the `system_hss` package, then start the relevant control/algorithm nodes from this package.

## License

[MIT License](LICENSE)  
Copyright (c) 2026 Akram Al Qasemi