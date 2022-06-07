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
  INCLUDE_DIRS include proto
  LIBRARIES ${PROJECT_NAME}
  CATKIN_DEPENDS common autopilot_msgs
  DEPENDS
)

find_package(Protobuf REQUIRED)

set(PROTO_PATH "${CMAKE_CURRENT_SOURCE_DIR}/proto")
set(OUTPUT_CXX_DIR "${CMAKE_CURRENT_SOURCE_DIR}/proto")
set(OUTPUT_PY_DIR "${CMAKE_CURRENT_SOURCE_DIR}/script")
file(GLOB PROTO_SOURCE_FILES "${PROTO_PATH}/*.proto")

foreach(input_proto ${PROTO_SOURCE_FILES})
  get_filename_component(FILE_NAME ${input_proto} NAME_WE)

  set(OUTPUT_CXX_HEADER "${OUTPUT_CXX_DIR}/${FILE_NAME}.pb.h")
  set(OUTPUT_CXX_SOURCE "${OUTPUT_CXX_DIR}/${FILE_NAME}.pb.cc")
  set(OUTPUT_PY_SCRIPT "${OUTPUT_PY_DIR}/${FILE_NAME}_pb2.py")
  list(APPEND OUTPUT_SOURCES_CXX ${OUTPUT_CXX_HEADER} ${OUTPUT_CXX_SOURCE})
  list(APPEND OUTPUT_SOURCES_PY ${OUTPUT_PY_SCRIPT})
endforeach()

add_custom_command(
  OUTPUT  ${OUTPUT_SOURCES_CXX}
  COMMAND ${PROTOBUF_PROTOC_EXECUTABLE} --cpp_out=${OUTPUT_CXX_DIR} --proto_path=${PROTO_PATH} ${PROTO_SOURCE_FILES}
  DEPENDS ${PROTO_SOURCE_FILES}
  WORKING_DIRECTORY ${PROTO_PATH}
)

add_custom_command(
  OUTPUT  ${OUTPUT_SOURCES_PY}
  COMMAND ${PROTOBUF_PROTOC_EXECUTABLE} --python_out=${OUTPUT_PY_DIR} --proto_path=${PROTO_PATH} ${PROTO_SOURCE_FILES}
  DEPENDS ${PROTO_SOURCE_FILES}
  WORKING_DIRECTORY ${PROTO_PATH}
)

add_custom_target(
  compile_protos
  DEPENDS ${OUTPUT_SOURCES_CXX} ${OUTPUT_SOURCES_PY}
)

include_directories(include proto ${PROJECT_SOURCE_DIR}/.. ${catkin_INCLUDE_DIRS})

add_library(${PROJECT_NAME}
  ${OUTPUT_SOURCES_CXX}
  src/mogo_reporter.cpp
)
target_link_libraries(${PROJECT_NAME} 
  ${catkin_LIBRARIES}
  ${PROTOBUF_LIBRARIES}
)
add_dependencies(${PROJECT_NAME} compile_protos)

add_executable(mogo_report_test test/mogo_report_test.cpp)
target_link_libraries(mogo_report_test ${PROJECT_NAME})

add_executable(mogo_report_test_all test/mogo_report_test_all.cpp)
target_link_libraries(mogo_report_test_all ${PROJECT_NAME})

add_executable(mogo_report_sub test/mogo_report_sub.cpp)
target_link_libraries(mogo_report_sub ${PROJECT_NAME})

install(TARGETS ${PROJECT_NAME} mogo_report_sub
  ARCHIVE DESTINATION ${CATKIN_PACKAGE_LIB_DESTINATION}
  LIBRARY DESTINATION ${CATKIN_PACKAGE_LIB_DESTINATION}
  RUNTIME DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
install(DIRECTORY include/
  DESTINATION ${CATKIN_GLOBAL_INCLUDE_DESTINATION}
)
install(FILES ${OUTPUT_CXX_HEADER}
  DESTINATION ${CATKIN_GLOBAL_INCLUDE_DESTINATION}/mogo_reporter
)

#file(GLOB PYTHON_FILES "script/*.py")
#catkin_install_python(PROGRAMS ${PYTHON_FILES}
#  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/script
#)
install(DIRECTORY script/
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/script
)

file(GLOB PROTO_CONFIG_FILES "config/*.pb")
install(FILES ${PROTO_CONFIG_FILES}
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/config
)