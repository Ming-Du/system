cmake_minimum_required(VERSION 2.8.3)
project(guardian)

find_package(catkin REQUIRED COMPONENTS message_generation std_msgs)

# add_message_files(DIRECTORY msg FILES Floats.msg HeaderString.msg)
# add_service_files(DIRECTORY srv FILES AddTwoInts.srv BadTwoInts.srv)
#generate_messages(DEPENDENCIES std_msgs)

catkin_package(CATKIN_DEPENDS message_runtime std_msgs metric_msgs)

catkin_install_python(PROGRAMS
  system_guardian.py
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)
install(FILES
  system_guardian.launch
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)

install(FILES
  system_guardian.json
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)

# if(CATKIN_ENABLE_TESTING)
#   find_package(rostest)
#   foreach(T
#       test/test-add-two-ints.launch
#       test/test-peer-subscribe-notify.launch
#       test/test-add-two-ints-with-roscpp-server.launch
#       test/test-talker-listener.launch
#       test/test-talker-listener-with-roscpp.launch
#       test/test-on-shutdown.launch
#       test/test-connection-header.launch)
#      add_rostest(${T})
#   endforeach()
# endif()
