# maps/

Maps saved from SLAM (Day 6) go here:

```bash
cd ~/ros2_ws/src/my_robot_description/maps
ros2 run nav2_map_server map_saver_cli -f factory_map
# -> factory_map.pgm + factory_map.yaml
```

Then use it with: `ros2 launch my_robot_description nav.launch.py map:=$HOME/ros2_ws/src/my_robot_description/maps/factory_map.yaml`
