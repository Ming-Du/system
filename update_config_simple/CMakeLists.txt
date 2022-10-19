cmake_minimum_required(VERSION 2.8.3)
project(update_config_simple)
find_package(catkin REQUIRED COMPONENTS
  roscpp
  autopilot_msgs
  common
)
find_package(Protobuf REQUIRED)

catkin_package()

include_directories(
  ${catkin_INCLUDE_DIRS} 
)


install(
	FILES AiModelImpInterfaceDataSource.py CacheUtils.py CommonHttpUtils.py CommonPara.py CommonSchedulerImpInterfaceTaskSchedulingPool.py CommonSimpleSchedulerImpInterfaceTaskSchedulingPool.py CommonTriggerImpInterfaceTrigger.py CommonUtilsCompare.py CommonUtilsReadFile.py ConfigImpInterfaceDataSource.py EnumDataSourceType.py EnumJobStatus.py EnumJobType.py EnumVersion.py Executor.py FileUtils.py HdMapAgentImpInterfaceDataSource.py InterfaceDataSource.py InterfaceTaskSchedulingPool.py InterfaceTrigger.py JobItem.py Job.py LogLine.py SlamMapImpInterfaceDataSource.py TrajectoryImpInterfaceDataSource.py update_config_simple.py
    DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/
  )
install(
    DIRECTORY  proto entity launch
    DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/
  )



