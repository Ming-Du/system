
一：运行说明

1，车上运行，匹配自动驾驶过程中的时间点，订阅了车辆状态topic /system_master/SysVehicleState
	车上手动启动命令 容器中root用户下执行 
	roslaunch --wait /home/mogo/autopilot/share/log_reslove/log_reslove.launch &

2、离线测试，需要设置 g_test_mode = True  不初始化topic，不匹配自驾时间段
	离线测试，需要创建好/home/mogo/data/log 目前，并将车上的保留日志放置到 /home/mogo/data/log/ROS_STAT/EXPORT
    离线环境测试命令  进入到log_reslove源码目录
	python3 log_reslove.py


--------------------------------------------------------
--------------------------------------------------------

二，埋点日志原理介绍

1，参考文档
   http://wiki.zhidaohulian.com/pages/viewpage.action?pageId=79454645

2，因为依赖于ros埋点，ros的代码（mogo_libs）修改，需要注意log_reslove的解析变更。


--------------------------------------------------------
--------------------------------------------------------

三，log_reslove 的DAG配置介绍

1、 config.py 中双层dict的形式进行了配置

2、第一层字典中的key 表示node名称， value 是二层字典表示了该node的订阅topic列表，发布topic，以及手动埋点关键字段

3、注意，目前全链路配置中的节点为关键链路节点，且只支持一路pub输出
--------------------------------------------------------
--------------------------------------------------------


四，log_relove 结构介绍

main()函数中
  首先 初始化config配置中关键Node节点的实例
  其次 创建 Log_handler()类，并运行 

关键函数
	Node_base().update_node_info()  自驾期间的日志行进行解析存储
	Log_handler().run_once()  一次自驾允许的处理

	Log_handler().get_topic_info() 反向全链路匹配计算函数
	Log_handler().get_sensor_node_info() 正向全链路匹配计算函数


关键全局结构：
all_link_node_list  记录了Node_base的实例列表， 每个实例包含自身node的pub sub man_beg man_end等节点内匹配逻辑
all_link_topic_list  记录了所有topic的信息字段，包含每个uuid标识的topic的sub pub 以及关联beg 或者 end信息


--------------------------------------------------------
--------------------------------------------------------


五，log_relove 迭代修改说明

MAP2.11之前版本 主要功能罗列 
1、正向统计
2、反向统计
3、自驾时间范围的判断
3、按解析次数(2秒一次) 保存自驾时候日志


20220109 log_reslove 迭代修改说明（更新到MAP3.0.0+）
1、全链路匹配最后时间last_timestamp  只在正向统计中计算
2、反向统计 只统计last_timestamp 之前的，之后数据缓存，下一次匹配（为了反向匹配更全，减少丢失）
3、增加clear_match_data_and_save_error_topic 清除last_timestamp之前的topic，输出topic匹配不全的信息


















