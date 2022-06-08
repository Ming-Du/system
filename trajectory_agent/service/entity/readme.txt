long lineId; //路线id，默认-1
String trajUrl; //轨迹文件下载的cos url，默认“”
String trajMd5; //轨迹文件md5，默认“”
String stopUrl; //打点文件下载的cos url，默认“”
String stopMd5; //轨迹文件md5，默认“”

long timestamp; //上传轨迹完成时间戳：用于MEC本地手动导入轨迹验证时不会被云端轨迹覆盖

String vehicleModel; //车型号（如红旗H9），默认“”，暂不加入校验逻辑、用于人工排查问题

现有param内容（保留）

MsgType：开启自动驾驶：MessageType.MsgTypeSetAutopilotModeReq
String startName; // 起点名称拼音首字母大写：科学城B区2号门（KXCBQ2HM）
String endName; // 终点名称拼音首字母大写：科学城C区三号门（KXCCQSHM）
AutopilotControlParameters.AutoPilotLonLat startLatLon;
AutopilotControlParameters.AutoPilotLonLat endLatLon;