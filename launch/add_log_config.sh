#!/bin/bash

[[ -z "$1" ]] && exit 1
level=${2:-ERROR}
launch_name=$(echo ${1##*/} | cut -d. -f1)
ROSCONSOLE_CONFIG_FILE="$ABS_PATH/config/${launch_name}_${level}_console.config"
ROS_PYTHON_LOG_CONFIG_FILE="$ABS_PATH/config/python_logging_${launch_name}.conf"
echo >$ROSCONSOLE_CONFIG_FILE
echo >$ROS_PYTHON_LOG_CONFIG_FILE
ros_log_dir=${ROS_LOG_DIR}/${launch_name}
[[ ! -d ${ros_log_dir} ]] && mkdir -p ${ros_log_dir}

pkg_str=$(xmllint --xpath "//@pkg" $1 2>/dev/null | sed 's/\"//g')
PythonLoggingInfoFile=rospy_${launch_name}_INFO.log
PythonLoggingErrorFile=rospy_${launch_name}_ERROR.log
for value in $pkg_str; do
    pkg_name=${value/*=/}
    Aconsole=C${pkg_name}
    InfoAppender=I_${pkg_name}
    ErrorAppender=E_${pkg_name}
    ErrorFile=${pkg_name}_ERROR.log
    InfoFile=${pkg_name}_INFO.log
    #LOGCXX
    echo "log4j.logger.ros=${level},${InfoAppender},${ErrorAppender}
log4j.appender.${InfoAppender}=org.apache.log4j.DailyRollingFileAppender
log4j.appender.${InfoAppender}.Threshold=INFO
log4j.appender.${InfoAppender}.ImmediateFlush=true
log4j.appender.${InfoAppender}.Append=true
log4j.appender.${InfoAppender}.File=${ros_log_dir}/${InfoFile}
log4j.appender.${InfoAppender}.DatePattern='.'yyyy-MM-dd-HH
log4j.appender.${InfoAppender}.layout=org.apache.log4j.PatternLayout
log4j.appender.${InfoAppender}.layout.ConversionPattern=[%-5p] %d{yyyy-MM-dd HH:mm:ss.SSS} %l: %m %n

log4j.appender.${ErrorAppender}=org.apache.log4j.DailyRollingFileAppender
log4j.appender.${ErrorAppender}.Threshold=ERROR
log4j.appender.${ErrorAppender}.ImmediateFlush=true
log4j.appender.${ErrorAppender}.Append=true
log4j.appender.${ErrorAppender}.File=${ros_log_dir}/${ErrorFile}
log4j.appender.${ErrorAppender}.DatePattern='.'yyyy-MM-dd-HH
log4j.appender.${ErrorAppender}.layout=org.apache.log4j.PatternLayout
log4j.appender.${ErrorAppender}.layout.ConversionPattern=[%-5p] %d{yyyy-MM-dd HH:mm:ss.SSS} LWP:%t(%r) %l: %m %n
" >>$ROSCONSOLE_CONFIG_FILE
done 
    
#Python logging
echo "[loggers]
keys=root, rospyInfo

[handlers]
keys=fileHandler,streamHandler,fileHandlerRospyInfo,fileHandlerRospyError

[filters]
keys=base

[formatters]
keys=defaultFormatter,infoFormatter,errorFormatter

[logger_root]
level=INFO
handlers=fileHandler

[logger_rospyInfo]
level=INFO
handlers=fileHandlerRospyInfo
propagate=1
qualname=rosout

[handler_fileHandler]
class=handlers.RotatingFileHandler
level=DEBUG
formatter=defaultFormatter
# log filename, mode, maxBytes, backupCount
args=('${ros_log_dir}/${launch_name}.launch.log','a')

[handler_fileHandlerRospyInfo]
class=handlers.TimedRotatingFileHandler
level=INFO
formatter=infoFormatter
# log filename, when, interval, backupCount
args=('${ros_log_dir}/${PythonLoggingInfoFile}', 'h', 1)

[handler_fileHandlerRospyError]
class=handlers.RotatingFileHandler
level=ERROR
formatter=errorFormatter
# log filename, when, interval, backupCount
args=('${ros_log_dir}/${PythonLoggingErrorFile}', 'h', 1)

[handler_streamHandler]
class=rosgraph.roslogging.RosStreamHandler
level=DEBUG
formatter=defaultFormatter
# colorize output flag
args=(True,)

[formatter_infoFormatter]
format=[%(levelname)s] %(asctime)s %(filename)s(%(lineno)d): %(message)s

[formatter_errorFormatter]
format=[%(levelname)s] %(asctime)s %(filename)s(%(lineno)d): %(message)s

[formatter_defaultFormatter]
format=[%(levelname)s][%(name)s] %(asctime)s: %(message)s
">>$ROS_PYTHON_LOG_CONFIG_FILE
