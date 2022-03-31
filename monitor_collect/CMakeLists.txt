cmake_minimum_required(VERSION 2.8.3)
project(monitor_collect)
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
    FILES monitor_collect.py  simu_telematics.py simu_hz.py
    DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/
  )
install(
    DIRECTORY  proto entity launch busi_module core_module
    DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/
  )



