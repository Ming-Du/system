# 在 C++ ros node 中使用
## 0. 项目编译  
使用命令 catkin_make --only-pkg-with-deps mogo_reporter 编译本项目  
## 1. 添加 libmogo_report.so 的引用  
- 在 package.xml 中添加
```
如果 format 是 1
  <build_depend>mogo_reporter</build_depend>
  <run_depend>mogo_reporter</run_depend>
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
1）MOGO_MSG_INIT()  // 通过默认的节点名来 初始化msg_reporter, **推荐**
2）MOGO_MSG_INIT_CFG("telematics") // 通过自定义的名称来初始化 msg_reporter
这里传入的名称是用来匹配事件code 配置文件的。
```
> 注意：  
> 必须在 ros::init 之后，再调用 MOGO_MSG_INIT_CFG  
> MOGO_MSG_INIT_CFG() 传入的 字符串必须是config 文件夹 中的配置文件的name, 否则会找不到配置文件，导致事件报告失败

- 汇报事件
```
通过 MOGO_MSG_REPORT() 宏 来进行事件汇报
 * MOGO_MSG_REPORT("事件码字符串"); // 默认附带最小间隔时间3s。若需要取消此限制请显示设置最小间隔时间
 * MOGO_MSG_REPORT("事件码字符串", "附带数据字符串"); // 默认附带最小间隔时间3s。若需要取消此限制请显示设置最小间隔时间
 * MOGO_MSG_REPORT("事件码字符串", "附带数据字符串", 3.0); // 事件报告最小间隔时间, 如果不添加第三个参数，默认是 MOGO_REPORTER_SPAN_SEC
 *
 * 使用事件码枚举的方式将在290版本弃用，请使用事件码字符串上报！！！
 * 弃用: MOGO_MSG_REPORT(mogo_msg::ReportMsgCode::EMAP_CAN_ADAPTER_NO_CHASSIS_INFO)
 * 推荐: MOGO_MSG_REPORT("EMAP_CAN_ADAPTER_NO_CHASSIS_INFO")
```
> 注意：
> 请使用 MOGO_MSG_REPORT("事件码字符串"); 的形式进行上报
> MOGO_MSG_REPORT(mogo_msg::ReportMsgCode::***) 枚举的方式将在290版本弃用，请尽快更换为字符串上报形式！！！

# 在 python 或 shell 中使用（获取事件码）
## 0. 项目编译  
使用命令 catkin_make --only-pkg-with-deps mogo_reporter 编译本项目

## 1. 在脚本中获取事件码 json
python script/get_msg_by_code.py <配置文件路径> <事件码>
如:
```
cd system/mogo_reporter
python script/get_msg_by_code.py config/mogo_sys.pb EHW_GNSS
```

# 事件码管理方式
1. 事件码采用git仓库的方式进行管理  
git地址为: https://gitlab.zhidaoauto.com/autopilot/ros/mogo_msgs  
每新增一个消息定义版本，将创建新分支。  
版本内的消息需求，各位研发需经过评审，后修改到自己dev分支的nodes/*.yaml中，并提交merge request，进行合并。  
MAP联调前确认MAP版本使用的事件码版本，最终打包到MAP镜像中  

2. 仓库文件结构说明  
result.yaml 用来管理 RESULT 定义   
action.yaml 用来管理 ACTION 定义  
nodes/'node_nice_name'.yaml 用来管理各个节点的消息定义, 'node_nice_name'为节点的友好命名，一般是节点命名的子串  
新的事件码按照每个算法模块，一个消息定义配置文件的方式进行管理。  
要保证各自的事件码Code唯一！！！  

3. nodes 中的yaml 配置格式说明  
```yaml
info: #info级别的消息
  - code: IMAP_TRA_LOADED  #要保证code的唯一性
    msg: 轨迹文件加载成功

  - code: ISYS_CONFIG_UPDATE_HADMAP
    msg: 需要重启升级高精度地图

error: #info级别的消息
  - code: EMAP_TRA_LOAD_FAILED
    msg: 加载轨迹文件失败
    result:  #取自 ../result.yaml
      - RESULT_AUTOPILOT_DISABLE
      - RESULT_REMOTEPILOT_DISABLE
    action:  #取自 ../action.yaml
      - ACTION_CONTACT_TECH_SUPPORT
```