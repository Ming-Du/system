#!/usr/bin/python3

node_config = {}

node_config["/jinlv_can_adapter"] = {}
node_config["/jinlv_can_adapter"]["sub"] = ["/chassis/command"]
node_config["/jinlv_can_adapter"]["pub"] = ""
node_config["/jinlv_can_adapter"]["man_end"] = "can_end"

node_config["/controller"] = {}
node_config["/controller"]["sub"] = ["/planning/trajectory"]
node_config["/controller"]["pub"] = "/chassis/command"
node_config["/controller"]["man_beg"] = "controller_begin"

node_config["/local_planning"] = {}
node_config["/local_planning"]["sub"] = ["/perception/fusion/obstacles", "/hadmap_engine/lanes_msg", "/planning/global_trajectory"]
node_config["/local_planning"]["pub"] = "/planning/trajectory"
node_config["/local_planning"]["man_beg"] = "planning_begin"

node_config["/perception/fusion/perception_fusion2"] = {}
node_config["/perception/fusion/perception_fusion2"]["sub"] = ["/perception/fusion_mid/lidar_obstacle", "/perception/camera/camera_obstacle_front60", "/perception/lidar/lidar_zvision_obstacle"]
node_config["/perception/fusion/perception_fusion2"]["pub"] = "/perception/fusion/obstacles"

node_config["/perception/fusion/perception_fusion_mid"] = {}
node_config["/perception/fusion/perception_fusion_mid"]["sub"] = ["/perception/lidar/lidar_obstacle"]
node_config["/perception/fusion/perception_fusion_mid"]["pub"] = "/perception/fusion_mid/lidar_obstacle"

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
node_config["/perception_camera_2D_front"]["sub"] = ["/sensor/camera/sensing/image_raw_60/nvjpeg", "/sensor/camera/sensing/image_raw_30"]
node_config["/perception_camera_2D_front"]["pub"] = "/perception/camera/camera_obstacle_front60"

node_config["/sensor/camera/sensing60/drivers_camera_sensing60"] = {}
node_config["/sensor/camera/sensing60/drivers_camera_sensing60"]["sub"] = []
node_config["/sensor/camera/sensing60/drivers_camera_sensing60"]["pub"] = "/sensor/camera/sensing/image_raw_60/nvjpeg"
node_config["/sensor/camera/sensing60/drivers_camera_sensing60"]["man_beg"] = "camera_grab"

#2.10.0 新增config
node_config["/hadmap_engine_node"] = {}
node_config["/hadmap_engine_node"]["sub"] = []
node_config["/hadmap_engine_node"]["pub"] = "/hadmap_engine/lanes_msg"

node_config["/hadmap_server"] = {}
node_config["/hadmap_server"]["sub"] = []
node_config["/hadmap_server"]["pub"] = "/planning/global_trajectory"


#2.11.0 新增M2 lidar适配

node_config["/M2_can_adapter"] = {}
node_config["/M2_can_adapter"]["sub"] = ["/chassis/command"]
node_config["/M2_can_adapter"]["pub"] = ""
node_config["/M2_can_adapter"]["man_end"] = "can_end"

node_config["/perception/lidar/rs_perception_zvision_node"] = {}
node_config["/perception/lidar/rs_perception_zvision_node"]["sub"] = ["/sensor/zvisionlidar/middle/point_cloud"]
node_config["/perception/lidar/rs_perception_zvision_node"]["pub"] = "/perception/lidar/lidar_zvision_obstacle"

node_config["/xiaoba_zvisionlidars_fusion"] = {}
node_config["/xiaoba_zvisionlidars_fusion"]["sub"] = ["/sensor/lidar/zvisionlidar/front/point_cloud", "/sensor/lidar/zvisionlidar/left/point_cloud","/sensor/lidar/zvisionlidar/rear/point_cloud","/sensor/lidar/zvisionlidar/right/point_cloud"]
node_config["/xiaoba_zvisionlidars_fusion"]["pub"] = "/sensor/zvisionlidar/middle/point_cloud"

node_config["/zvision_lidar_front_nodelet_manager"] = {}
node_config["/zvision_lidar_front_nodelet_manager"]["sub"] = []
node_config["/zvision_lidar_front_nodelet_manager"]["pub"] = "/sensor/lidar/zvisionlidar/front/point_cloud"
node_config["/zvision_lidar_front_nodelet_manager"]["man_beg"] = "lidar_grab"

node_config["/zvision_lidar_left_nodelet_manager"] = {}
node_config["/zvision_lidar_left_nodelet_manager"]["sub"] = []
node_config["/zvision_lidar_left_nodelet_manager"]["pub"] = "/sensor/lidar/zvisionlidar/left/point_cloud"
node_config["/zvision_lidar_left_nodelet_manager"]["man_beg"] = "lidar_grab"

node_config["/zvision_lidar_right_nodelet_manager"] = {}
node_config["/zvision_lidar_right_nodelet_manager"]["sub"] = []
node_config["/zvision_lidar_right_nodelet_manager"]["pub"] = "/sensor/lidar/zvisionlidar/right/point_cloud"
node_config["/zvision_lidar_right_nodelet_manager"]["man_beg"] = "lidar_grab"

node_config["/zvision_lidar_rear_nodelet_manager"] = {}
node_config["/zvision_lidar_rear_nodelet_manager"]["sub"] = []
node_config["/zvision_lidar_rear_nodelet_manager"]["pub"] = "/sensor/lidar/zvisionlidar/rear/point_cloud"
node_config["/zvision_lidar_rear_nodelet_manager"]["man_beg"] = "lidar_grab"


