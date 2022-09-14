import rospy
class CommonPara:
    dictCarInfo = None

    def __init__(self):
        self.dictCarInfo = {}

    def read_car_info(self):
        try:
            with open("/autocar-code/project_commit.txt") as fp1:
                contents1 = fp1.read().split("\n")
            dictCarInfo = {}
            dictCarInfo["code_version"] = contents1[1][len("Version:"):]

            with open("/home/mogo/data/vehicle_monitor/vehicle_config.txt") as fp2:
                contents2 = fp2.read().split("\n")

            plate = contents2[0].split(":")[-1]
            plate = plate.strip().strip("\"")

            brand = contents2[1].split(":")[-1]
            brand = brand.strip().strip("\"")

            dictCarInfo["car_plate"] = plate
            dictCarInfo["car_type"] = brand
        except Exception as e:
            rospy.logwarn("read carInfo failed!")
            return False
        return dictCarInfo

    def initPara(self):
        self.dictCarInfo = self.read_car_info()
