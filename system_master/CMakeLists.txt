cmake_minimum_required(VERSION 2.8.3)

project(system_master)
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

###### pen pb2.py files   ######## 
string(REGEX REPLACE  "(.*)/(.*)/(.*)" "\\1" project_src_path ${PROJECT_SOURCE_DIR})

set(proto_dir ${project_src_path}/system/common/proto)
set(proto_gen_dir ${PROJECT_SOURCE_DIR}/proto)
set(proto_gen_python_files "")
file(GLOB proto_files "${proto_dir}/*.proto")

foreach(proto_file ${proto_files})
        get_filename_component(proto_name ${proto_file} NAME_WE)
        list(APPEND proto_gen_python_files
                ${proto_gen_dir}/${proto_name}_pb2.py
        )
endforeach(proto_file ${proto_files})

add_custom_command(
        OUTPUT ${proto_gen_python_files}
        COMMAND ${PROTOBUF_PROTOC_EXECUTABLE}
                --proto_path=${proto_dir}
                --python_out=${proto_gen_dir} ${proto_files}
        DEPENDS ${PROTOBUF_PROTOC_EXECUTABLE} ${proto_files}
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
)

add_custom_target(run_system_master ALL DEPENDS ${proto_gen_python_files})

###############

install(FILES
	system_master.launch
	start_system_master.sh
	keep_system_pid_alived_102.sh
	DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)

catkin_install_python(PROGRAMS
	system_master.py
	sys_agent_handler.py
	sys_node_handler.py
	sys_common.py
	sys_config.py
	sys_globals.py
	sys_test_tools.py
	DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)

install(
        DIRECTORY ./proto 
	DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)
