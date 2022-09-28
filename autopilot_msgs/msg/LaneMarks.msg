Header header
Header header_ros_time_start
Header header_ros_time_end

LaneMark left # current left line
LaneMark right # current right line
LaneMark left2 # 
LaneMark right2 #

# add by qianlei
LaneMark[] lanemarks

# add by wandanpan
RoadArrow[] arrows
sensor_msgs/Image lane_arrow_stopline_seg
sensor_msgs/Image fs_rs_seg  # freespace and roadside
sensor_msgs/Image laneline_inst_seg  # laneline instance seg

# laneline arrow stopline exist flag
bool laneline_exist_flag
bool arrow_exist_flag
bool stopline_exist_flag