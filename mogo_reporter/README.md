# 在 C++ ros node 中使用
## 0. 项目编译  
使用命令 catkin_make --only-pkg-with-deps mogo_reporter 编译本项目  
> 注意：如果找不到 *.pb.h 或 *_pb2.py 文件，先编译本项目
## 1. 添加 libmogo_report.so 的引用  
- 在 package.xml 中添加
```
如果 format 是 1
  <build_depend>mogo_report</build_depend>
  <run_depend>mogo_report</run_depend>
如果 format 是 2
  <build>mogo_reporter</build>
```
- 在 CMakeLists.txt 中添加
```
find_package(catkin REQUIRED COMPONENTS
  roscpp
  mogo_reporter  # 用来引用头文件和lib文件
)

catkin_package(
  INCLUDE_DIRS
  LIBRARIES ${PROJECT_NAME}
  CATKIN_DEPENDS mogo_reporter # 用来添加编译依赖项
  DEPENDS
)
```
## 2. 在源代码中使用API
- 包含头文件
```
#include "mogo_reporter/mogo_reporter.h"
```
- 第一次使用 进行初始化
```
ros::init(argc, argv, "mogo_report_test");
MOGO_MSG_INIT_CFG("telematics");
有两种初始化方式：
1）MOGO_MSG_INIT()  // 通过默认的节点名来 初始化msg_reporter
2）MOGO_MSG_INIT_CFG("telematics") // 通过自定义的名称来初始化 msg_reporter
这里传入的名称是用来匹配事件code 配置文件的。
```
> 注意：  
> 必须在 ros::init 之后，再调用 MOGO_MSG_INIT_CFG  
> MOGO_MSG_INIT_CFG() 传入的 字符串必须是config 文件夹 中的配置文件的name, 否则会找不到配置文件，导致事件报告失败

- 汇报事件
```
通过 MOGO_MSG_REPORT() 宏 来进行事件汇报
有几种参数:
1) MOGO_MSG_REPORT(mogo_msg::ReportMsgCode::ITELEMATICS_AUTOPILOT_CMD_RECEIVED); // 通过事件code进行汇报
2）MOGO_MSG_REPORT(mogo_msg::ReportMsgCode::ETELEMATICS_PAD_RECV_ERROR, "my msg"); // 通过事件code 外加自定义的 消息进行汇报
3）MOGO_MSG_REPORT_SRC("testsrc", mogo_msg::ReportMsgCode::ETELEMATICS_PAD_SEND_ERROR, "my msg"); // 可以自定义消息报告者的name，默认是节点名
```

# 在 python 或 shell 中使用（获取事件码）
## 0. 项目编译  
使用命令 catkin_make --only-pkg-with-deps mogo_reporter 编译本项目
> 注意：如果找不到 *.pb.h 或 *_pb2.py 文件，先编译本项目

## 1. 在脚本中获取事件码 json
python script/get_msg_by_code.py <配置文件路径> <事件码>
如:
```
cd system/mogo_reporter
python script/get_msg_by_code.py config/mogo_sys.pb EHW_GNSS
```

# 扩充事件码
1. 在 proto/mogo_report_codes.proto 中添加事件码枚举值
2. 把详细的事件信息添加到对应的 config/*.pb 中