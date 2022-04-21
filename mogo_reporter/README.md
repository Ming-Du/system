# How to use
1. Add depends in package.xml and CMakeLists.txt
```
  <build_depend>roscpp</build_depend>
  <build_depend>mogo_reporter</build_depend>
  <build_export_depend>roscpp</build_export_depend>
  <build_export_depend>mogo_reporter</build_export_depend>
  <exec_depend>roscpp</exec_depend>
  <exec_depend>mogo_reporter</exec_depend>
```
```
find_package(catkin REQUIRED COMPONENTS
  roscpp
  mogo_reporter  # To find include dir and lib dir
)

catkin_package(
  INCLUDE_DIRS
  LIBRARIES ${PROJECT_NAME}
  CATKIN_DEPENDS mogo_reporter # To add deps of mogo_reporter
  DEPENDS
)
```
2. Add report codes in your cpp
```cpp
#include "mogo_reporter/mogo_reporter.h"  // Include header

ros::init(argc, argv, "mogo_report_test");
MOGO_MSG_INIT_CFG("telematics");
/*
MOGO_MSG_INIT();  // init mogo reporter by node name defalut.
MOGO_MSG_INIT_CFG("telematics") // init mogo reporter by specified name, which is used by fuzzy matching with config pb files.
Note: you must call MOGO_MSG_INIT after ros::init.
*/
MOGO_MSG_REPORT(mogo_msg::ReportMsgCode::ITELEMATICS_AUTOPILOT_CMD_RECEIVED);
// report msg by code
MOGO_MSG_REPORT(mogo_msg::ReportMsgCode::ETELEMATICS_PAD_RECV_ERROR, "my msg");
// report msg with custom message
MOGO_MSG_REPORT_SRC("testsrc", mogo_msg::ReportMsgCode::ETELEMATICS_PAD_SEND_ERROR, "my msg");
// report msg by custom src name, the default src name is node name
```

# How to add report msg codes
1. And enum value in proto/mogo_report_codes.proto
2. And report msg codes in specified config pb file in config/*.pb