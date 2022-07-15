cmake_minimum_required(VERSION 2.8.3)
project(hd_map_agent)
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
    FILES hd_map_agent.py
    DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/
  )
install(
    DIRECTORY  proto launch
    DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/
  )



