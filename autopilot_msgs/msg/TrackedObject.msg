# Tracked Object message
# $Id$

CommonObject obj

float32  yaw       #box orientation angle from x axis, counter clockwise(in rad),range -pi to pi
float32  yaw_rate  #in rad/s
geometry_msgs/Vector3 velocity  # absolute velocity, in m/s, vx, vy, vz
geometry_msgs/Point[] trace     # historical positions

float32  absolute_longitude_v    # along lane speed, m/s
float32  absolute_longitude_a    # in m/s2, longitudinal acc
float32  absolute_lateral_v      # vertical to lane speed, left positive, m/s

#float32 x_speed             # longitudinal speed relative to host vehicle, m/s
#float32 y_speed             # lateral speed relative to host vehicle, m/s

