int32 LANE_MARK_WHITE = 0
int32 LANE_MARK_YELLOW = 1

int32 LANE_MARK_NONE = 0
int32 LANE_MARK_SOLID = 1
int32 LANE_MARK_BROKEN = 2


int32 color
int32 type
float32 confidence
geometry_msgs/Point[] points

# add by qianlei
LaneLineCubicCurve curve_car_coord
geometry_msgs/Point[] curve_image_coord_point_set
geometry_msgs/Point[] curve_car_coord_point_set
