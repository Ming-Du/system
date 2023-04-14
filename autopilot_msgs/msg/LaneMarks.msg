Header header
Header header_ros_time_start
Header header_ros_time_end

LaneMark left # current left line
LaneMark right # current right line
LaneMark left2 # 
LaneMark right2 #

# add by qianlei
LaneMark[] lanemarks

RoadSide[] roadsides

geometry_msgs/Point[] fs_img_point_set  # 2D points of freespace contours

# add by wandanpan
RoadArrow[] arrows
sensor_msgs/Image lane_arrow_stopline_crossing_seg  # lane:235, arrow:245, stopline:255, crossing:205
sensor_msgs/Image fs_rs_seg  # freespace and roadside, freespace:215, roadside:225
sensor_msgs/Image laneline_inst_seg  # laneline instance seg

# laneline arrow stopline exist flag
bool laneline_exist_flag
bool arrow_exist_flag
bool stopline_exist_flag
bool crossing_exist_flag