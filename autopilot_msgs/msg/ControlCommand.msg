# command send to the chassis
Header header

int32 MODE_MANUAL = 0
int32 MODE_AUTO_DRIVE = 1
int32 MODE_STEER_ONLY = 2
int32 MODE_SPEED_ONLY = 3
int32 MODE_REMOTE_DRIVE = 6

int32 GEAR_NONE = 0
int32 GEAR_P = 1
int32 GEAR_R = 2
int32 GEAR_N = 3
int32 GEAR_D = 4

int32 LIGHT_NONE = 0
int32 LIGHT_LEFT = 1
int32 LIGHT_RIGHT = 2
int32 LIGHT_FLASH = 3

int32 OFF = 0
int32 ON = 1

int32 control_mode   # MODE_*
float32 steer_angle    
float32 accel

int32 gear    # GEAR_*
int32 light   # LIGHT_* 

#bool switch_off_engine  # 发动机熄火请求
bool horn         #鸣笛    0= OFF ; 1 = ON;
bool highbeam     #远光灯
bool lowbeam      #近光灯
bool headlight    #前照灯 
bool foglight     #雾灯
bool clearance_lamps  #示廓灯
bool epb         #电子手刹
bool warn_light    #报警灯

bool LocalitonMissing
bool TrajectoryMissing
bool VehicleStateMissing
