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

node_config["/local_planning"] = {}
node_config["/local_planning"]["sub"] = ["/perception/fusion/obstacles"]
node_config["/local_planning"]["pub"] = "/planning/trajectory"

node_config["/perception/fusion/perception_fusion2"] = {}
node_config["/perception/fusion/perception_fusion2"]["sub"] = ["/perception/lidar/lidar_obstacle", "/perception/camera/camera_obstacle"]
node_config["/perception/fusion/perception_fusion2"]["pub"] = "/perception/fusion/obstacles"

node_config["/perception/fusion/perception_fusion"] = {}
node_config["/perception/fusion/perception_fusion"]["sub"] = ["/perception/lidar/lidar_obstacle_cluster", "/perception/camera/camera_obstacle"]
node_config["/perception/fusion/perception_fusion"]["pub"] = "/perception/fusion/obstacles"

node_config["/perception/lidar/rs_perception_node"] = {}
node_config["/perception/lidar/rs_perception_node"]["sub"] = ["/sensor/lidar/middle/point_cloud"]
node_config["/perception/lidar/rs_perception_node"]["pub"] = "/perception/lidar/lidar_obstacle"

node_config["/perception/lidar/perception_lidar"] = {}
node_config["/perception/lidar/perception_lidar"]["sub"] = ["/sensor/lidar/front_left/point_clound", "/sensor/lidar/front_right/point_cloud"]
node_config["/perception/lidar/perception_lidar"]["pub"] = "/perception/lidar/lidar_obstacle"

node_config["/sensor/lidar/robosense/drivers_robosense_node"] = {}
node_config["/sensor/lidar/robosense/drivers_robosense_node"]["sub"] = []
node_config["/sensor/lidar/robosense/drivers_robosense_node"]["pub"] = "/sensor/lidar/middle/point_cloud"

node_config["/sensor/lidar/c32/front_left/c32_left_decoder"] = {}
node_config["/sensor/lidar/c32/front_left/c32_left_decoder"]["sub"] = []
node_config["/sensor/lidar/c32/front_left/c32_left_decoder"]["pub"] = "/sensor/lidar/front_left/point_clound"

node_config["/sensor/lidar/c32/front_right/c32_right_decoder"] = {}
node_config["/sensor/lidar/c32/front_right/c32_right_decoder"]["sub"] = []
node_config["/sensor/lidar/c32/front_right/c32_right_decoder"]["pub"] = "/sensor/lidar/front_right/point_clound"

node_config["/trt_yolov5"] = {}
node_config["/trt_yolov5"]["sub"] = ["/sensor/camera/sensing/image_raw_60"]
node_config["/trt_yolov5"]["pub"] = "/perception/camera/camera_obstacle"

node_config["/sensor/camera/sensing60/drivers_camera_sensing60"] = {}
node_config["/sensor/camera/sensing60/drivers_camera_sensing60"]["sub"] = []
node_config["/sensor/camera/sensing60/drivers_camera_sensing60"]["pub"] = "/sensor/camera/sensing/image_raw_60"


