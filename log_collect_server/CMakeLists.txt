cmake_minimum_required(VERSION 2.8.3)

project(log_collect_server)
find_package(catkin REQUIRED COMPONENTS
  roscpp
  autopilot_msgs
  # ${PROJECT_NAME}_proto
)
#find_package(Protobuf REQUIRED)

catkin_package(CATKIN_DEPENDS)

include_directories(
  ${catkin_INCLUDE_DIRS} 
)


install(FILES
	log_collect_server.launch
	DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)

catkin_install_python(PROGRAMS
	log_collect_server.py
	DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)


