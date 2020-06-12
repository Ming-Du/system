#coding=utf-8
import rospy
from cv_bridge import CvBridge
from sensor_msgs.msg import Image, CompressedImage
from autopilot_msgs.msg import CommonObjects, VisualObjects
#from threading import Thread, Lock
import cv2
import numpy as np
from time import sleep

#bridge = CvBridge()

COLS = 1280
ROWS = 720

cv2.namedWindow("image",cv2.WINDOW_NORMAL)
cv2.resizeWindow("image", 889, 500)

class Process():
    #f = open("data/gt_info.txt","w")
    #writer = cv2.VideoWriter('video/out.mp4', 
    #    cv2.VideoWriter_fourcc(*'mp4v'), 20, (1280,720))
    count = 1

    def __init__(self):
        rospy.Subscriber("/lidar_detection/clusters_msg", CommonObjects, self.cluster_callback)
        rospy.Subscriber("/usb_cam_6mm/image_raw/compressed", CompressedImage, self.image_callback)
        rospy.Subscriber("/camera_detection/bounding_boxes", VisualObjects, self.visual_callback)

    def cluster_callback(self, msg):
        self.cluster_objs = Cluster(Time.now().to_sec(), msg.objs)

    def visual_callback(self, msg):
        self.visual_objs = Visual(Time.now().to_sec(), msg.objs)

    def image_callback(self, msg):
        #img = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        np_arr = np.fromstring(msg.data, np.uint8)
        image_np = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        #cv2.imshow("", image_np)
        #cv2.waitKey(1)
        self.count += 1
        
    def write_file(self, msgs): 
        self.f.writelines(msgs+"\n")

    def write_img(self, img):
        cv2.imwrite("img/%06d.jpg"%(self.count), img)

    def write_vid(self, frame):
        self.writer.write(frame)

if __name__ == "__main__":
    rospy.init_node("tbag", anonymous=True);

    p = Process()
    #Subscriber("/sensor/gnss/")
    
    rospy.spin()
