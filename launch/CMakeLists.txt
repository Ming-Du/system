cmake_minimum_required(VERSION 2.8.3)
project(launch)
#find_package(catkin REQUIRED)
catkin_package()
install(DIRECTORY .
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)
