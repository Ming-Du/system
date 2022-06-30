cmake_minimum_required(VERSION 2.8.3)
project(trajectory_agent)
find_package(catkin REQUIRED COMPONENTS
  roscpp
  autopilot_msgs
  common
)
find_package(Protobuf REQUIRED)

catkin_package()

include_directories(
  ${catkin_INCLUDE_DIRS} 
)


install(
    FILES trajectory_agent.py
    DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/
  )
install(
    DIRECTORY  proto service  launch
    DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/
  )



