# Drivers #

## Usage ##

以下用法说明只是对单个传感器运行的示意，由于每辆车上传感器的配置和外参都不同，具体运行格式参考[末尾](http://gitlab.zhidaoauto.com/autopilot/autopilot_L3/drivers#%E5%9C%A8%E4%B8%80%E8%BE%86%E6%96%B0%E8%BD%A6%E4%B8%8A%E7%9A%84%E9%A9%B1%E5%8A%A8%E9%85%8D%E7%BD%AE)的说明.

**1. <font color=blue>camera</font> 摄像头驱动**

***1.1 <font color=blue>camera</font> USB摄像头驱动***

启动方式:
```bash
$ roslaunch drivers_camera usb_cam.launch
```
启动脚本内容:
```xml
<!-- 摄像头设备路径, 使用 ls /dev/video* 查看 -->
<arg name="camera_device" default="/dev/video0" />

<arg name="config_path" default="$(find drivers_common)/conf"/>
<!-- 传感器参数文件 -->
<arg name="sensor_meta"
  default="$(arg config_path)/sensor.pb.txt" />
<!-- 解码格式, 目前用到的有 mjpeg, yuyv -->
<arg name="pixel_format" default="mjpeg" />
<!-- 传感器名称, 与calibrated_sensor标定文件内容一致 -->
<arg name="sensor_name" default="6mm_front" />

<node name="drivers_camera" output="screen" 
      pkg="drivers_camera" type="drivers_camera_node" 
      args="--sensor_meta_path=$(arg sensor_meta)" >
  <param name="video_device" value="$(arg camera_device)" />
  <!-- 图像像素宽度 -->
  <param name="image_width" value="1280" />
  <!-- 图像像素高度 -->
  <param name="image_height" value="720" />
  <!-- 设置输出帧率 -->
  <param name="framerate" value="25"/>
  <param name="pixel_format" value="$(arg pixel_format)" />
  <param name="camera_frame_id" value="$(arg sensor_name)" />
  <param name="io_method" value="mmap"/>
</node>
```

***1.2 <font color=blue>camera</font> 森云摄像头驱动***

***(1) 标定内外参时***
启动方式:
```bash
$ roslaunch drivers_camera sensing30_calib.launch frame_id:=H30-D05270524
$ roslaunch drivers_camera sensing60_calib.launch frame_id:=H60-D05270579
$ roslaunch drivers_camera sensing120_calib.launch frame_id:=H120-D05270538
注: 标定内参时可以不设置frame_id参数
```
启动脚本内容:
```xml
<?xml version="1.0"?>
<launch>
  <!-- 摄像头设备路径, 使用 ls /dev/video* 查看 -->
  <arg name="video_device" default="/dev/video0" />
  <!-- 摄像头id(对应SN号) -->
  <arg name="frame_id" default="H30-0527xxx" />
  <!-- 是否已标定, 0:未标定, 1:已标定 -->
  <arg name="calibed" default="0" />
  <!-- 图像节点topic -->
  <arg name="camera_topic" default="/sensor/camera/sensing/image_raw_30" />
  <group ns="sensor/camera/sensing">
    <node name="drivers_camera_sensing" pkg="drivers_camera"
        type="drivers_camera_sensing_node" output="screen">
      <param name="video_device" value="$(arg video_device)" />
      <!-- 设置输出帧率 -->
      <param name="framerate" value="30"/>
      <param name="camera_frame_id" value="$(arg frame_id)" />
      <param name="camera_topic" value="$(arg camera_topic)" />
      <!-- 图像像素宽度 -->
      <param name="image_width" value="1920" />
      <!-- 图像像素高度 -->
      <param name="image_height" value="1080" />
      <param name="calibed" value="$(arg calibed)" />
    </node>
  </group>
</launch>
```

***(2) 正常工作时(内外参已标定)***
启动方式:
```bash
$ roslaunch drivers_camera sensing30.launch frame_id:=H30-D05270524
$ roslaunch drivers_camera sensing60.launch frame_id:=H60-D05270579
$ roslaunch drivers_camera sensing120.launch frame_id:=H120-D05270538
```
启动脚本内容:
```xml
<?xml version="1.0"?>
<launch>
  <arg name="video_device" default="/dev/video0" />
  <arg name="config_path" default="$(find drivers_common)/conf"/>
  <!-- 传感器参数文件 -->
  <arg name="sensor_meta"
    default="$(arg config_path)/sensing.pb.txt" />
  <!-- 摄像头id(对应SN号) -->
  <arg name="frame_id" default="H30-D0527xxx" />
  <arg name="calibed" default="1" />
  <!-- 是否开启畸变校正(1:打开, 0:关闭) -->
  <arg name="undistort" default="0" />
  <group ns="sensor/camera/sensing30">
    <node name="drivers_camera_sensing30" pkg="drivers_camera"
        type="drivers_camera_sensing_node" output="screen" 
        args="--sensor_meta_path=$(arg sensor_meta)">
      <param name="video_device" value="$(arg video_device)" />
      <param name="framerate" value="30"/>
      <param name="camera_frame_id" value="$(arg frame_id)" />
      <param name="image_width" value="1920" />
      <param name="image_height" value="1080" />
      <param name="calibed" value="$(arg calibed)" />
      <param name="undistort" value="$(arg undistort)" />
    </node>
  </group>
</launch>
```

**2. <font color=blue>gnss</font> 惯导驱动**

启动方式:
```bash
$ roslaunch drivers_gnss data_spin.launch
```
启动脚本内容:
```xml
<!-- 配置文件默认路径 -->
<arg name="config_path" default="$(find drivers_common)/conf"/>
<!-- 传感器外参配置文件 -->
<arg name="sensor_meta" default="$(arg config_path)/sensor.pb.txt" />
<!-- 名称需要与sensor_meta中传感器名称对应 -->
<arg name="sensor_name" default="gnss" />

<node name="drivers_gnss" pkg="drivers_gnss" type="drivers_gnss_node"
    output="screen" ns="sensor/gnss"
    args="--sensor_meta_path=$(arg sensor_meta)" >
  <!-- 惯导设备USB接口路径 -->
  <param name="device" value="/dev/ttyACM0" />
  <param name="frame_id" value="$(arg sensor_name)" />
  <!-- 加速度偏移, 位姿偏移标定文件 -->
  <param name="config_file" value="$(arg config_path)/gyro_bias.pb.txt" />
</node>
```

`gyro_bias.pb.txt`文件存放加速度计偏移`accelerometer_bias`和磁力计偏移`gyroscope_bias`的标定. 具体参数意义和标定方法参照[wiki](http://wiki.zhidaohulian.com/pages/viewpage.action?pageId=48963104)

**3. <font color=blue>hesai</font> 禾赛激光雷达驱动**

启动方式:
```bash
$ roslaunch drivers_hesai hesai_lidar.launch
```
启动脚本内容(部分):
```xml
<!-- 配置文件默认路径 -->
<arg name="config_path" default="$(find drivers_common)/conf"/>
<!-- 传感器外参配置文件 -->
<arg name="sensor_meta" default="$(arg config_path)/sensor.pb.txt" />
<!-- 名称需要与sensor_meta中传感器名称对应 -->
<arg name="sensor_name" default="hesai_front" />
<!-- 设备IP -->
<arg name="server_ip" default="192.168.8.200"/>
<!-- host端接收的端口号 -->
<arg name="lidar_recv_port"  default="2368"/>
<!-- 设备型号需要对应 -->
<arg name="lidar_type" default="PandarXT-32"/>
```

**4. <font color=blue>livox</font> 览沃激光雷达驱动**

启动方式:
```bash
$ roslaunch drivers_livox livox_lidar.launch
```
启动脚本内容(部分):
```xml
<!-- 配置文件默认路径 -->
<arg name="config_path" default="$(find drivers_common)/conf"/>
<!-- 传感器外参配置文件 -->
<arg name="sensor_meta" default="$(arg config_path)/sensor.pb.txt" />
<!-- 设备ID 该ID出现在览沃激光设备背面二维码下方 -->
<arg name="bd_list" default="000000000000"/>
<!-- 名称需要与sensor_meta中传感器名称对应 -->
<arg name="sensor_name" default="hesai_front" />
<!-- 设备IP -->
<arg name="server_ip" default="192.168.8.200"/>
<!-- host端接收的端口号 -->
<arg name="lidar_recv_port"  default="2368"/>
<!-- 设备型号需要对应 -->
<arg name="lidar_type" default="PandarXT-32"/>
```

**5. <font color=blue>leishen</font> 镭神激光雷达驱动**

启动方式:
```bash
$ roslaunch drivers_lslidar lslidar_ch.launch  # 启动CH32驱动
$ roslaunch drivers_lslidar lslidar_c32.launch # 启动C32驱动
$ roslaunch drivers_lslidar lslidar_c16.launch # 启动C16驱动
```

CH32启动脚本内容(部分):
```xml
<!-- 激光设备ip, 所有安装在前向的激光雷达ip和port均以此为准 -->
<param name="lidar_ip" value="192.168.8.200"/>
<param name="device_port" value="2368"/>
<!-- 设备名称 -->
<param name="frame_id" value="lslidar_ch"/>
<!-- 点云最近范围 -->
<param name="min_range" value="0.15"/>
<!-- 点云最远范围 -->
<param name="max_range" value="150.0"/>
<!-- 使用gps授时 -->
<param name="use_gps_ts" value="false"/>
```

C32, C16启动脚本内容(部分):
```xml
<!-- 前向激光雷达ip:192.168.8.200, port:2368; 2369 -->
<!-- 左前激光雷达ip:192.168.8.201, port:2370; 2371 -->
<!-- 右前激光雷达ip:192.168.8.202, port:2372; 2373 -->
<arg name="device_ip" default="192.168.8.201" />
<arg name="msop_port" default="2370" />
<arg name="difop_port" default="2371" />
<!-- 回波模式 1单回波, 2双回波 -->
<arg name="return_mode" default="1" />
<!-- 设备名称 -->
<arg name="frame_id" default="c16_front_left" />
<!-- 点云距离范围 -->
<param name="min_distance" value="0.15"/>
<param name="max_distance" value="150.0"/>
<!-- 从线头开始顺时针方向 输出点云范围 -->
<param name="scan_start_angle" value="6000.0"/>
<param name="scan_end_angle" value="28000.0"/>
<!-- 距离尺度: 之前遇到点云值过小/过大的问题, 应该将值改为1或0.25 -->
<param name="distance_unit" value="1"/>
```

---
## 在一辆新车上的驱动配置 ##

在`system`仓库下的`config`目录建立一个以当前车的`ID={车型}{车牌号}`的目录，并建立该目录指向`vehicle`的软连接。目录下包含对该车传感器参数配置和启动脚本, 并由`system/launch`下的脚本指向这个存放在固定位置的启动脚本。为方便理解目录内参数文件分布，可参考`system/config/CCBJA8PA20`

```bash
$ roscd config
$ mkdir {车型}{地点}{车牌号}
$ ln -s {车型}{地点}{车牌号} vehicle
```

目前定义了三款车型 `长城CC`, `比亚迪BYD`, `金旅JL`; 自动驾驶车所在城市`北京BJ`, `天津TJ`, `衡阳HY`. 如果有新车配置的需求时, 长城车可拷贝`CCBJA8PA20`文件夹内所有配置, 比亚迪可拷贝`BYDBJA22872`, 金旅可拷贝`JLBJ1861378`.

通过如下命令启动传感器驱动:

```bash
$ roslaunch launch drivers.launch
```

其中`launch/drivers.launch`内容:

```xml
<!-- 摄像头驱动节点 -->
<include file="$(find config)/vehicle/drivers/camera/camera.launch" />
<!-- 激光雷达驱动节点 -->
<include file="$(find config)/vehicle/drivers/lidar/lidar.launch" />
<!-- 惯导驱动节点 -->
<include file="$(find config)/vehicle/drivers/gnss/gnss.launch" />
```

所有传感器依赖外参配置参数文件, 固定存放在`system/config/vehicle/sensor/calibrated_sensor.pb.txt`. 参数说明:

+ `base`: `"base_link"` 车体参考系名称
+ `sensor_info`: 传感器信息
 + `name`: 传感器名称, 与`frame id`对应
 + `type`: 传感器类型, 在`common/proto/sensor.proto`文件中定义
 + `orientation`: 安装朝向
 + `extrinsic`: 外参
   + `translation`: 平移系数
   + `rotation`: 旋转系数
 + `intrinsic`: 内参(camera)
   + `width`: 图像宽度
   + `height`: 图像高度
   + `matrix` * 9: 内参系数
