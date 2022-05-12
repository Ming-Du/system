cmake_minimum_required(VERSION 2.8.3)
SET(CMAKE_BUILD_TYPE "Debug")
SET(CMAKE_CXX_FLAGS_DEBUG "$ENV{CXXFLAGS} -O0 -Wall -g -ggdb")


project(update_config)

add_definitions(-std=c++11 -g -O3)

# list(APPEND CMAKE_PREFIX_PATH /home/opencv_test/)

add_subdirectory(src/proto)

add_compile_options(-g -Wno-deprecated-declarations)
## Find catkin macros and libraries
## if COMPONENTS list like find_package(catkin REQUIRED COMPONENTS xyz)
## is used, also find other catkin packages
find_package(catkin REQUIRED COMPONENTS autopilot_msgs common image_transport roscpp std_msgs std_srvs sensor_msgs)

## pkg-config libraries
find_package(PkgConfig REQUIRED)
pkg_check_modules(avcodec libavcodec REQUIRED)
pkg_check_modules(swscale libswscale REQUIRED)

###################################################
## Declare things to be passed to other projects ##
###################################################

## LIBRARIES: libraries you create in this project that dependent projects also need
## CATKIN_DEPENDS: catkin_packages dependent projects also need
## DEPENDS: system dependencies of this project that dependent projects also need
catkin_package(
  INCLUDE_DIRS ${PROJECT_SOURCE_DIR}/src/proto
  LIBRARIES 
  ${PROJECT_NAME}
)

# cuda
if (CMAKE_SYSTEM_PROCESSOR MATCHES "aarch64")
    message("embed_platform on")
    include_directories(/usr/include/)
    link_directories(/usr/lib/aarch64-linux-gnu/)
else()
    message("embed_platform off")
    include_directories(/usr/include/)
    link_directories(/usr/lib/aarch64-linux-gnu/)
endif()

###########
## Build ##
###########

find_package(OpenCV REQUIRED)
include_directories(include
  ${catkin_INCLUDE_DIRS}
  ${PROJECT_SOURCE_DIR}/src/proto
  ../../
)

add_executable(${PROJECT_NAME} src/update_config.cpp src/md5.cpp  src/mogo_curl.cpp  src/mogo_json.cpp)
target_link_libraries(${PROJECT_NAME}
  ${catkin_LIBRARIES}
  curl
  jsoncpp
  protobuf
  config_proto
  proj
)



#############
## Install ##
#############

## Mark executables and/or libraries for installation
install(TARGETS  ${PROJECT_NAME}
  RUNTIME DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
  LIBRARY DESTINATION ${CATKIN_PACKAGE_LIB_DESTINATION}
)

install(DIRECTORY launch/
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/launch
  FILES_MATCHING PATTERN "*.launch"
)

# install(DIRECTORY include/${PROJECT_NAME}/
#    DESTINATION ${CATKIN_PACKAGE_INCLUDE_DESTINATION}
#    FILES_MATCHING PATTERN "*.h" PATTERN "*.hpp"
# )

