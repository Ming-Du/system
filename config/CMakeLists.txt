cmake_minimum_required(VERSION 2.8.3)
project(config)
#find_package(catkin REQUIRED)
catkin_package()
install(DIRECTORY A7HL79 Q3TS20
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)
