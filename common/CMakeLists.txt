cmake_minimum_required(VERSION 2.8.3)
project(common)

## is used, also find other catkin packages
find_package(catkin REQUIRED COMPONENTS
)

find_program(PROTOC protoc)
set(pb_file_root ${CMAKE_CURRENT_SOURCE_DIR}/proto)
file(GLOB proto_files ${pb_file_root}/*.proto)
set(pb_out_path ${CMAKE_CURRENT_SOURCE_DIR}/proto)

foreach(pb_file ${proto_files})
    get_filename_component(pb_file_name ${pb_file} NAME_WE)
    set(cur_out_file
        #${pb_out_path}/include/${pb_file_name}.pb.h
        ${pb_out_path}/${pb_file_name}.pb.cc
        )
    set(pb_out_files ${pb_out_files} ${cur_out_file})
    add_custom_command(
        OUTPUT ${cur_out_file}
        COMMAND ${PROTOC} ${pb_file} --cpp_out=${pb_out_path} -I=${pb_file_root}
        DEPENDS ${PROTOC} ${pb_file}
        WORKING_DIRECTORY ./
        # ${CMAKE_CURRENT_SOURCE_DIR}
        )
endforeach(pb_file ${proto_files})

#set_source_files_properties(${pb_out_files} PROPERTIES GENERATED TRUE)

set(CMAKE_CXX_FLAGS "-std=c++11 -O3 -Wall ${CMAKE_CXX_FLAGS}")

catkin_package(
  INCLUDE_DIRS include
  LIBRARIES ${PROJECT_NAME}
  CATKIN_DEPENDS roscpp
#  DEPENDS system_lib
)

include_directories(
  ${catkin_INCLUDE_DIRS}
  include
)

add_library(${PROJECT_NAME}
    src/pb_utils.cc
    ${pb_out_files}
)

target_link_libraries(${PROJECT_NAME}
    ${catkin_LIBRARIES}
    #${PROTOBUF_LIBRARIES}
)
