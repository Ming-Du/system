class CollectVehicleInfo:
    int_pilot_mode = None
    b_steer_inference = None
    b_brake_inference = None
    b_accel_inference = None
    b_gear_switch_inference = None
    b_location_missing = None
    b_trajectory_missing = None
    b_chassis_status_missing = None
    int_error_code = None
    str_err_msg = None

    def __init__(self):
        self.int_pilot_mode = 0
        self.b_steer_inference = False
        self.b_brake_inference = False
        self.b_accel_inference = False
        self.b_gear_switch_inference = False
        self.b_location_missing = False
        self.b_trajectory_missing = False
        self.b_chassis_status_missing = False
        self.int_error_code = 0
        self.str_err_msg = "normal"
