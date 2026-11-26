# ROS 2 Jazzy + Gazebo Harmonic — Factory Patrol Robot

A two-wheeled differential-drive robot in a simulated factory. It maps the floor with LiDAR,
patrols 4 checkpoints autonomously with Nav2, and can be switched on/off through a service.

## 1. Layout

```
src/
├── my_robot_interfaces/        Day 2  – MachineStatus message (ament_cmake)
├── my_robot_pkg/               Days 1-3, 5, 7 – Python nodes + launch files
│   ├── my_robot_pkg/
│   │   ├── temp_publisher.py       D2  publishes /compressor/temperature
│   │   ├── temp_monitor.py         D2  overheat alarm + reset_alarm service
│   │   ├── temp_subscriber.py      D2  minimal subscriber (/temperature)
│   │   ├── motor_service.py        D2  /set_motor service (SetBool)
│   │   ├── machine_status_publisher.py  D2  uses the custom MachineStatus msg
│   │   ├── qos_demo.py             D3  qos_pub / qos_sub – the QoS trap
│   │   ├── square_driver.py        D5  drives a square using /odom
│   │   └── patrol_node.py          D7  patrols via the Nav2 action
│   ├── launch/ monitor, qos_demo, tf_demo, patrol
│   ├── config/ params.yaml, patrol.yaml
│   └── rviz/   day3.rviz
└── my_robot_description/       Days 4-6 – robot, world, bridge, SLAM, Nav2
    ├── urdf/   my_robot.urdf.xacro, gazebo.xacro
    ├── worlds/ factory.sdf
    ├── config/ bridge.yaml, slam_params.yaml, nav2_params.yaml
    ├── launch/ display, sim, slam, nav, spawn_obstacle
    ├── rviz/   display.rviz, sim.rviz, nav.rviz
    └── maps/   (maps you save)
```

## 2. Install and build

```bash
# get the code: this repo is the workspace's src folder
mkdir -p ~/ros2_ws && git clone https://github.com/nhphuc5208/Learn_ROS2.git ~/ros2_ws/src

# dependencies
sudo apt install -y ros-jazzy-desktop ros-jazzy-ros-gz ros-jazzy-xacro \
  ros-jazzy-joint-state-publisher-gui ros-jazzy-teleop-twist-keyboard \
  ros-jazzy-slam-toolbox ros-jazzy-navigation2 ros-jazzy-nav2-bringup liburdfdom-tools
cd ~/ros2_ws && rosdep install --from-paths src -y --ignore-src

# build
cd ~/ros2_ws && colcon build --symlink-install && source install/setup.bash
```

Every new terminal must run `source ~/ros2_ws/install/setup.bash` (or use the `sws` alias).

## 3. Running each day

### Day 2: Python nodes
```bash
ros2 run my_robot_pkg temp_publisher --ros-args -p rate_hz:=5.0 -p machine_id:=AC-07   # T1
ros2 run my_robot_pkg temp_monitor   --ros-args -p threshold:=75.0                     # T2
ros2 topic hz /compressor/temperature                         # verify rate_hz
ros2 param set /temp_monitor threshold 90.0                   # change the threshold at runtime
ros2 service call /temp_monitor/reset_alarm std_srvs/srv/Trigger
ros2 run my_robot_pkg motor_service
ros2 service call /set_motor std_srvs/srv/SetBool "{data: true}"
ros2 run my_robot_pkg machine_status_publisher && ros2 topic echo /machine_status
```

### Day 3: launch, QoS, TF
```bash
ros2 launch my_robot_pkg monitor.launch.py threshold:=70.0 rqt:=true
ros2 launch my_robot_pkg qos_demo.launch.py                              # broken: sub receives nothing
ros2 launch my_robot_pkg qos_demo.launch.py pub_reliability:=reliable    # fixed
ros2 topic info /qos_demo/data -v
ros2 launch my_robot_pkg tf_demo.launch.py
ros2 run tf2_tools view_frames
```

### Day 4: URDF in RViz2
```bash
xacro ~/ros2_ws/src/my_robot_description/urdf/my_robot.urdf.xacro > /tmp/out.urdf && check_urdf /tmp/out.urdf
ros2 launch my_robot_description display.launch.py
ros2 launch my_robot_description display.launch.py use_arm:=true   # revolute arm exercise
```
Drag the sliders in the joint_state_publisher_gui window to turn the wheels or the arm.
Width exercise: change `wheel_sep` in `my_robot.urdf.xacro`. The DiffDrive plugin picks up the new value automatically.

### Day 5: Gazebo + control
```bash
ros2 launch my_robot_description sim.launch.py rviz:=true          # T1
ros2 run teleop_twist_keyboard teleop_twist_keyboard               # T2 (i , j l k)
ros2 topic hz /odom                                                # ~50 Hz
ros2 run my_robot_pkg square_driver --ros-args -p use_sim_time:=true -p side:=2.0   # 2 m square
ros2 launch my_robot_description spawn_obstacle.launch.py x:=1.5 y:=0.0             # add an obstacle
gz topic -l ; gz model -m my_robot --pose
```

### Day 6: Sensors, SLAM, Nav2
```bash
ros2 topic hz /scan                                     # ~10 Hz, 360 points
ros2 run rqt_image_view rqt_image_view                  # pick /camera/image_raw

# Build a map
ros2 launch my_robot_description slam.launch.py         # T1 (Gazebo + SLAM + RViz2)
ros2 run teleop_twist_keyboard teleop_twist_keyboard    # T2: drive slowly around the factory
cd ~/ros2_ws/src/my_robot_description/maps && ros2 run nav2_map_server map_saver_cli -f factory_map

# Drive to a goal. In RViz2 click "Nav2 Goal", then click on the map
ros2 launch my_robot_description nav.launch.py                       # SLAM + Nav2
ros2 launch my_robot_description nav.launch.py \
    map:=$HOME/ros2_ws/src/my_robot_description/maps/factory_map.yaml # AMCL, remember 2D Pose Estimate
```

### Day 7: Capstone, patrol
```bash
ros2 launch my_robot_pkg patrol.launch.py                 # ONE command starts the whole system
ros2 topic echo /patrol/status
ros2 service call /patrol/enable std_srvs/srv/SetBool "{data: false}"   # stop
ros2 service call /patrol/enable std_srvs/srv/SetBool "{data: true}"    # resume
ros2 launch my_robot_description spawn_obstacle.launch.py x:=4.0 y:=2.0 # drop an obstacle while running
```
To change the patrol points, edit `my_robot_pkg/config/patrol.yaml`. On a slow machine add `headless:=true` to skip the Gazebo GUI.

## 4. Architecture

```
 [teleop / Nav2 / patrol_node] --/cmd_vel--> ros_gz_bridge --> [Gazebo: physics + DiffDrive]
                                                                     |
 [SLAM Toolbox] <--/scan-- ros_gz_bridge <--- LiDAR, camera, IMU ----+
       | /map, TF map->odom                                          |
       v                                                             |
 [Nav2: planner -> controller] <--/odom, TF odom->base_footprint ----+
       ^
       | action navigate_to_pose
 [patrol_node] <-- service /patrol/enable
```
- **Gazebo** plays the real world: the factory, the robot, the sensors.
- **ros_gz_bridge** translates data between Gazebo and ROS 2, configured in `bridge.yaml`.
- **SLAM** uses the LiDAR to build a map and work out where the robot is on it.
- **Nav2** plans a path around obstacles and outputs velocity commands on `/cmd_vel`.
- **patrol_node** is the "supervisor": it hands Nav2 one waypoint at a time and logs each arrival.

## 5. Known issues and fixes

| Problem | Symptom | Fix |
|---|---|---|
| Body bottom touches the floor (body height 0.12, centered on the 0.06 wheel axle) | Drives straight but **cannot turn in place** | `base_z_off = 0.03` raises the body |
| Cylinder wheel collision | Robot turns 13% faster than odom thinks, SLAM map is doubled and skewed | Wheel collision uses a sphere |
| JointStatePublisher plugin sets `<topic>` but the bridge used the default topic | No `/joint_states` | Bridge uses `/joint_states` |
| `wheel_separation` hard-coded to 0.34 | Changing `wheel_sep` breaks odom | Use `${wheel_sep}` |
| SLAM `min_pass_through: 2` + NavFn planner | Nav2 reports "Failed to create plan" | `min_pass_through: 1`, Smac 2D planner |

## 6. Recovery

```bash
pkill -f gz; pkill -f ros2; pkill -f rviz2
rm -rf /dev/shm/fastrtps* /dev/shm/sem.fastrtps* 2>/dev/null
cd ~/ros2_ws && rm -rf build install log && colcon build --symlink-install && source install/setup.bash
```
