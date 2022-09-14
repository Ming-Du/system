cmake_minimum_required(VERSION 2.8.3)

project(log_reslove)
find_package(catkin REQUIRED COMPONENTS
  roscpp
  autopilot_msgs
  # ${PROJECT_NAME}_proto
)
find_package(Protobuf REQUIRED)

catkin_package(CATKIN_DEPENDS)

include_directories(
  ${catkin_INCLUDE_DIRS} 
)

###### gen *_pb2.py files   ######## 
string(REGEX REPLACE  "(.*)/(.*)/(.*)" "\\1" project_src_path ${PROJECT_SOURCE_DIR})

set(proto_dir ${project_src_path}/system/common/proto)
set(proto_gen_dir ${PROJECT_SOURCE_DIR}/proto)
set(proto_gen_python_files "")
set(proto_files "")

file(STRINGS ${PROJECT_SOURCE_DIR}/proto/__init__.py import_list)

foreach(words ${import_list})
        string(STRIP ${words} word)
        string(REGEX REPLACE "^import.(.*)_pb2" "\\1" proto_name ${word})
        if(NOT (${proto_name} STREQUAL ${word}))
                list(APPEND proto_gen_python_files ${proto_gen_dir}/${proto_name}_pb2.py)
                list(APPEND proto_files ${proto_dir}/${proto_name}.proto)
        endif()
endforeach(words ${import_list})

add_custom_command(
        OUTPUT ${proto_gen_python_files}
        COMMAND ${PROTOBUF_PROTOC_EXECUTABLE}
                --proto_path=${proto_dir}
                --python_out=${proto_gen_dir} ${proto_files}
        DEPENDS ${PROTOBUF_PROTOC_EXECUTABLE} ${proto_files}
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
)

add_custom_target(run_log_reslove ALL DEPENDS ${proto_gen_python_files})

###############

install(FILES
	log_reslove.launch
	DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)

catkin_install_python(PROGRAMS
	log_reslove.py
        config.py
	DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)

install(
        DIRECTORY ./proto 
	DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)
