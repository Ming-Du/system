cmake_minimum_required(VERSION 2.8.3)
project(mogo_reporter)

add_compile_options(
  -std=c++11
  -O3
  -g
  -Wall
)

find_package(catkin REQUIRED COMPONENTS
  roscpp
  autopilot_msgs
  common
  roslib
)

catkin_package(
  INCLUDE_DIRS include
  LIBRARIES ${PROJECT_NAME}
  CATKIN_DEPENDS common autopilot_msgs
  DEPENDS
)

find_package(yaml-cpp REQUIRED)

include_directories(
  include 
  ${PROJECT_SOURCE_DIR}/.. 
  ${catkin_INCLUDE_DIRS} 
  ${YAML_CPP_INCLUDE_DIR}
)

add_library(${PROJECT_NAME}
  src/mogo_reporter.cpp
)
target_link_libraries(
  ${PROJECT_NAME} 
  ${catkin_LIBRARIES}
  ${YAML_CPP_LIBRARIES}
)

add_executable(mogo_report_test test/mogo_report_test.cpp)
target_link_libraries(mogo_report_test ${PROJECT_NAME})

add_executable(mogo_report_test_all test/mogo_report_test_all.cpp)
target_link_libraries(mogo_report_test_all ${PROJECT_NAME})

add_executable(mogo_report_sub test/mogo_report_sub.cpp)
target_link_libraries(mogo_report_sub ${PROJECT_NAME})

install(TARGETS ${PROJECT_NAME} mogo_report_sub mogo_report_test mogo_report_test_all
  ARCHIVE DESTINATION ${CATKIN_PACKAGE_LIB_DESTINATION}
  LIBRARY DESTINATION ${CATKIN_PACKAGE_LIB_DESTINATION}
  RUNTIME DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
install(DIRECTORY include/
  DESTINATION ${CATKIN_GLOBAL_INCLUDE_DESTINATION}
)
install(DIRECTORY script/
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/script
)