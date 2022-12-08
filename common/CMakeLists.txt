cmake_minimum_required(VERSION 2.8.3)
project(common)

find_package(catkin REQUIRED COMPONENTS
  roscpp
)

find_package(Protobuf REQUIRED)

set(CMAKE_CXX_FLAGS "-std=c++11 -O3 -g -Wall ${CMAKE_CXX_FLAGS}")

catkin_package(
  INCLUDE_DIRS include proto ${PROJECT_SOURCE_DIR}/..
  LIBRARIES ${PROJECT_NAME} ${PROJECT_NAME}_proto protobuf
)

message(STATUS "PROJECT_SOURCE_DIR:${PROJECT_SOURCE_DIR}")

add_subdirectory(proto)
include_directories(
  ${catkin_INCLUDE_DIRS}
  include
)


#add by shh
set(proto_dir ${PROJECT_SOURCE_DIR}/proto)
file(GLOB proto_files "${proto_dir}/*.proto")
file(GLOB proto_files_2 "${proto_dir}/v2x/*.proto")
list(APPEND proto_files ${proto_files_2})

message(STATUS "Proto Source Dir: ${proto_dir}")
message(STATUS "Proto Source Files: ${proto_files}")

catkin_destinations()
set(proto_gen_py_dir ${CATKIN_DEVEL_PREFIX}/${CATKIN_PACKAGE_PYTHON_DESTINATION})
file(MAKE_DIRECTORY ${proto_gen_py_dir})

file(WRITE ${proto_gen_py_dir}/__init__.py)
set(proto_gen_py_files "")
foreach(proto_file ${proto_files})
    get_filename_component(proto_name ${proto_file} NAME_WE)
    list(APPEND proto_gen_py_files ${proto_gen_py_dir}/${proto_name}_pb2.py)
endforeach(proto_file ${proto_files})

add_custom_command(
    OUTPUT  ${proto_gen_py_files}
    COMMAND ${PROTOBUF_PROTOC_EXECUTABLE} --proto_path=${proto_dir}/v2x --proto_path=${proto_dir} --python_out=${proto_gen_py_dir}  ${proto_files}
    DEPENDS ${PROTOBUF_PROTOC_EXECUTABLE} ${proto_files}
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
)
add_custom_target(runa ALL DEPENDS ${proto_gen_py_files})
set_source_files_properties(${proto_gen_py_files} PROPERTIES GENERATED TRUE)
#add end
add_library(${PROJECT_NAME}
  src/pb_utils.cc
)

target_link_libraries(${PROJECT_NAME}
  ${catkin_LIBRARIES}
  ${PROJECT_NAME}_proto
  glog yaml-cpp
)

install(TARGETS ${PROJECT_NAME}
   ARCHIVE DESTINATION ${CATKIN_PACKAGE_LIB_DESTINATION}
   LIBRARY DESTINATION ${CATKIN_PACKAGE_LIB_DESTINATION}
   RUNTIME DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

#add by shh
install(DIRECTORY ${proto_gen_py_dir}/
  DESTINATION ${CATKIN_PACKAGE_PYTHON_DESTINATION}
  FILES_MATCHING PATTERN "*.py"
)

install(DIRECTORY include
  DESTINATION ${CATKIN_GLOBAL_INCLUDE_DESTINATION}/common
  FILES_MATCHING PATTERN "*.h"
)

install(DIRECTORY proto
  DESTINATION ${CATKIN_GLOBAL_INCLUDE_DESTINATION}/common
  FILES_MATCHING PATTERN "*.h"
)
#add end
