# Common Object message
# $Id$

uint16 TYPE_UNKNOWN = 0
uint16 TYPE_PEDESTRIAN = 3
uint16 TYPE_BICYCLE = 4
uint16 TYPE_MOTOR = 5
uint16 TYPE_RIDER = 6
uint16 TYPE_CAR = 7
uint16 TYPE_TRUCK = 8
uint16 TYPE_BUS = 9
uint16 TYPE_TRAIN = 10
uint16 TYPE_SIGN = 20
uint16 TYPE_LIGHT = 30
uint16 TYPE_UNKNOWN_SMALL = 91
uint16 TYPE_UNKNOWN_BIG = 92
uint16 TYPE_UNKNOWN_STATIC = 93
uint16 TYPE_UNKNOWN_DYNAMIC = 94

int32 id                    # obj id, after tracked
int32 type                  # obj category
float64 timestamp           # sensing time
float32 confidence          # probability
int32 status                # reserved

float32 x_distance          # longitudinal distance
float32 y_distance          # lateral distance
float32 angle               # obj angle relative to host vehicle

geometry_msgs/Point   center   # x,y,z in meter
geometry_msgs/Point   size     # length width height(in meter)
geometry_msgs/Point[] contour  # contour points

