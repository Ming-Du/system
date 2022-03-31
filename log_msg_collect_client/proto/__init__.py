from sys import path
path.append('proto')

import vehicle_state_pb2   as vehicle_state
import chassis_pb2         as common_chassis
import control_command_pb2 as common_control_command
import error_code_pb2      as common_error_code
import geometry_pb2        as common_geometry
import hadmap_pb2          as common_hadmap
import header_pb2          as common_header
import lane_mark_pb2       as common_lane_mark
import localization_pb2    as common_localization
import object_pb2          as common_object
import planning_pb2        as common_planning
import routing_pb2         as common_routing
import traffic_light_pb2   as common_traffic_light
import trajectory_pb2      as common_trajectory
import vehicle_config_pb2  as common_vehicle_config
import vehicle_state_pb2   as common_vehicle_state

