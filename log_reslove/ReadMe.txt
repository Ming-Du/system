
一：环境配置

1，需要安装 protobuf python 库，解析 ros nodes 消息使用。
可以通过 pip install protobuf 命令安装


--------------------------------------------------------
--------------------------------------------------------

二，工具安装

1，新建 operator_tool 目录

2，把当前文件夹下全部内容拷贝到 operator_tool 目录下

3，配置 conf.txt，这是工具脚本的配置文件。

4，和系统其它模块一起编译、安装。
备注：
	operator_tool.py 和 operator_tool.ui 以及文件夹中的 proto 都会被安装到同一目录。

4，启动 operator_tool 工具方式

python operator_tool.py qt5 conf.txt

注：
	1》启动前需要配置好配置文件中的配置项
	2》脚本需要两个参数，pyqt 版本和 配置文件 conf.txt 的绝对路径。
	3》如果启动失败，主要原因就是 conf.txt 指定有错，或者配置文件有问题。
	
5，用 start_operator_tool 启动工具
为了方便启动工具，把启动命令写入一个简单脚本 start_operator_tool.
给脚本添加执行权限:

chmod 777 start_operator_tool

之后就可以通过它启动工具。
--------------------------------------------------------
--------------------------------------------------------

三，工具功能简介

1，Control tab
1）Traffic light 部分
功能状态：可用。
功能说明：设置红绿灯。
备注：

2）Control Mode
功能状态：可用。
功能说明：
	设置自动驾驶或人工驾驶。
	变换车道线。
	设置最大行驶速度。
备注：

3）Choose Map
功能状态：可用
功能说明：选择行驶地图。
备注：
	

4）Lock log
功能状态：可用
功能说明：锁定当前 ros 日志
备注：由于需求理解不同，需要再讨论和测试。

2，Tool tab
1）Track operation
功能状态：可用
功能说名：
	录制轨迹。
	导出轨迹文件。
备注：
	
	
2）Mark maps
功能状态：可用。
功能说明：
	地图打点。
备注：
	1》地图打点文件通过配置文件配置路径，名称自动生成。
	2》举例：/home/root/stop_and_speed_limit_20201214035902.txt
	3》每次重新启动工具，点击任意地图打点按钮，地图打点文件都会重新生成一个。
	4》地图打点文件以时间戳为后缀，区分每个不同打点文件。
	
3）Calibration
功能状态：不可用。
功能说明：
	外参标定。
备注：
	需要再讨论需求细节。

3，Monitor tab
1）Ros Node
功能状态：可用
功能说明：
	工具启动后，根据收到的节点状态数据，展示当前系统中正在运行和未启动的 ros 节点。绿色表示已经启动，红色表示没有启动。
	会自动更新 ros 节点启停状态，并展示。
	启动指定的节点。（此功能是否需要，带讨论。）
	停止指定的节点。（此功能是否需要，带讨论。）
备注：
	只是展示收到的节点状态信息

2）Mem Status
功能状态：可用。
功能说明：实时显示当前系统内存状态。
备注：
	只是展示收到的内存状态信息

3）Cpu Status
功能状态：可用。
功能说明：展示当前系统每个 CPU 的利用率。
备注：
	只是展示收到的 cpu 状态信息
--------------------------------------------------------
--------------------------------------------------------


四，配置文件 conf.txt 配置项说明


1，traj_filter_exe_path:
说明：traj_filter 可执行文件的路径。
举例：/home/mogo/autopilot/lib/hadmap/
备注：
	1》路径后面需要有反斜杠 '/'，否则可能找不到可执行文件。

2，record_track_file_path
说明：轨迹文件存放路径
举例：/home/mogo/
备注：
	1》路径后面需要有反斜杠 '/'。
	2》文件名自动生成
	
3，choose_map_json_file_path
说明：地图选择功能的配置文件放置路径
举例：/home/mogo/
备注：


4，mark_map_file_path
说明：地图打点生成的文件所在路径
举例：/home/mogo/
备注：	
	1》只能指定路径，文件名自动生成。
	
5，traj_file_path
说明：对应于 hadmap_server 的 launch 文件的 traj_file 选项，指定文件路径。
举例： /home/mogo/autopilot/share/map_data
备注：
	1》
		
6，traj_file_prefix
说明：对应于 hadmap_server 的 launch 文件的 traj_file 选项，指定文件路径的前缀。
举例：$(find map_data)
备注：
	1》在 launch 文件中配置可能是如下写法：
	   <param name="traj_file" value="$(find map_data)/BXY/demo_bxy_ql_gov_40km_af_loc_bias.csv:$(find map_data)/BXY/BXY_19_7_40km.csv:$(find map_data)/BXY/BXY_7_QL_40km.csv" />
    
			
	  发送此 value 给 ros 节点时，需要获取绝对路径：
	  /home/mogo/autopilot/share/map_data/BXY/demo_bxy_ql_gov_40km_af_loc_bias.csv
	  
	  工具需要把 $(find map_data 替换为 /home/mogo/autopilot/share/map_data。
	  
	  否则工具发出的路径数据不可用。
	  
7，db_file_path
说明：
举例：
备注：
	1》参考 traj_file_path 和 traj_file_prefix


8，db_file_prefix
说明：
举例：
备注：
	1》参考 traj_file_path 和 traj_file_prefix

	  


















