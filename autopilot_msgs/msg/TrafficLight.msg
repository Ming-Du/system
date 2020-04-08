# traffic light state message

int32 TYPE_DEFAULT = 0
int32 TYPE_VEHICLE = 1
int32 TYPE_BICYLE = 2
int32 TYPE_PEDSTRIAN = 3
int32 TYPE_LANE = 5

int32 STATE_OFF = 0
int32 STATE_RED = 1
int32 STATE_YELLOW = 2
int32 STATE_GREEN = 3
int32 STATE_FLASH = 4

int64 id
int32 type        # TYPE_*
int32 state       # STATE_*
float32 duration  # seconds since the last state changed
