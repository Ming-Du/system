#!/usr/bin/python3

node_config = {}
node_config["/DongFeng_E70_can_adapter"] = {}
node_config["/DongFeng_E70_can_adapter"]["sub"] = ["/chassis/command"]
node_config["/DongFeng_E70_can_adapter"]["pub"] = ""

node_config["/jinlv_can_adapter"] = {}
node_config["/jinlv_can_adapter"]["sub"] = ["/chassis/command"]
node_config["/jinlv_can_adapter"]["pub"] = ""

node_config["/controller"] = {}
node_config["/controller"]["sub"] = ["/planning/trajectory"]
node_config["/controller"]["pub"] = "/chassis/command"
node_config["/controller"]["man_beg"] = "controller_begin"

node_config["/local_planning"] = {}
node_config["/local_planning"]["sub"] = ["/perception/fusion/obstacles"]
node_config["/local_planning"]["pub"] = "/planning/trajectory"
node_config["/local_planning"]["man_beg"] = "planning_begin"

node_config["/perception/fusion/perception_fusion2"] = {}
node_config["/perception/fusion/perception_fusion2"]["sub"] = ["/perception/lidar/lidar_obstacle", "/perception/camera/camera_obstacle_front60"]
node_config["/perception/fusion/perception_fusion2"]["pub"] = "/perception/fusion/obstacles"

node_config["/perception/lidar/rs_perception_node"] = {}
node_config["/perception/lidar/rs_perception_node"]["sub"] = ["/sensor/lidar/middle/point_cloud"]
node_config["/perception/lidar/rs_perception_node"]["pub"] = "/perception/lidar/lidar_obstacle"

node_config["/xiaoba_lidars_fusion"] = {}
node_config["/xiaoba_lidars_fusion"]["sub"] = ["/sensor/lidar/front_left/point_cloud", "/sensor/lidar/front_right/point_cloud", "/sensor/lidar/rear/point_cloud"]
node_config["/xiaoba_lidars_fusion"]["pub"] = "/sensor/lidar/middle/point_cloud"

node_config["/sensor/lidar/c32/front_left/c32_left_decoder"] = {}
node_config["/sensor/lidar/c32/front_left/c32_left_decoder"]["sub"] = ["/sensor/lidar/c32/front_left/lslidar_packet"]
node_config["/sensor/lidar/c32/front_left/c32_left_decoder"]["pub"] = "/sensor/lidar/front_left/point_cloud"

node_config["/sensor/lidar/c32/front_right/c32_right_decoder"] = {}
node_config["/sensor/lidar/c32/front_right/c32_right_decoder"]["sub"] = ["/sensor/lidar/c32/front_right/lslidar_packet"]
node_config["/sensor/lidar/c32/front_right/c32_right_decoder"]["pub"] = "/sensor/lidar/front_right/point_cloud"

node_config["/sensor/lidar/c32/rear/c32_rear_decoder"] = {}
node_config["/sensor/lidar/c32/rear/c32_rear_decoder"]["sub"] = ["/sensor/lidar/c32/rear/lslidar_packet"]
node_config["/sensor/lidar/c32/rear/c32_rear_decoder"]["pub"] = "/sensor/lidar/rear/point_cloud"

node_config["/sensor/lidar/c32/front_left/c32_left_driver"] = {}
node_config["/sensor/lidar/c32/front_left/c32_left_driver"]["sub"] = []
node_config["/sensor/lidar/c32/front_left/c32_left_driver"]["pub"] = "/sensor/lidar/c32/front_left/lslidar_packet"
node_config["/sensor/lidar/c32/front_left/c32_left_driver"]["man_beg"] = "lidar_grab"

node_config["/sensor/lidar/c32/front_right/c32_right_driver"] = {}
node_config["/sensor/lidar/c32/front_right/c32_right_driver"]["sub"] = []
node_config["/sensor/lidar/c32/front_right/c32_right_driver"]["pub"] = "/sensor/lidar/c32/front_right/lslidar_packet"
node_config["/sensor/lidar/c32/front_right/c32_right_driver"]["man_beg"] = "lidar_grab"

node_config["/sensor/lidar/c32/rear/c32_rear_driver"] = {}
node_config["/sensor/lidar/c32/rear/c32_rear_driver"]["sub"] = []
node_config["/sensor/lidar/c32/rear/c32_rear_driver"]["pub"] = "/sensor/lidar/c32/rear/lslidar_packet"
node_config["/sensor/lidar/c32/rear/c32_rear_driver"]["man_beg"] = "lidar_grab"

node_config["/perception_camera_2D_front"] = {}
node_config["/perception_camera_2D_front"]["sub"] = ["/sensor/camera/sensing/image_raw_60/nvjpeg"]
node_config["/perception_camera_2D_front"]["pub"] = "/perception/camera/camera_obstacle_front60"

node_config["/sensor/camera/sensing60/drivers_camera_sensing60"] = {}
node_config["/sensor/camera/sensing60/drivers_camera_sensing60"]["sub"] = []
node_config["/sensor/camera/sensing60/drivers_camera_sensing60"]["pub"] = "/sensor/camera/sensing/image_raw_60/nvjpeg"
node_config["/sensor/camera/sensing60/drivers_camera_sensing60"]["man_beg"] = "camera_grab"
