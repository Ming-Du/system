cmake_minimum_required(VERSION 2.8.3)

project(log_msg_collect_client)
find_package(catkin REQUIRED COMPONENTS
  roscpp
  autopilot_msgs
)
#find_package(Protobuf REQUIRED)

catkin_package(CATKIN_DEPENDS)

include_directories(
  ${catkin_INCLUDE_DIRS} 
)

add_custom_target(run_log_msg_collect_client)

###############

install(FILES
	log_msg_collect_client.launch
	DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)

catkin_install_python(PROGRAMS
	log_msg_collect_client.py
	DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)

