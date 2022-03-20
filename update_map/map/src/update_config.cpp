//#include <ros/ros.h>
#include <ros/ros.h>
#include <sensor_msgs/NavSatFix.h>
#include <ros/time.h>
#include <nav_msgs/Odometry.h>

#include "mogo_curl.h"
#include "const.h"
#include "md5.h"

static sensor_msgs::NavSatFix gps_fix;

void GpsFixCallback(const sensor_msgs::NavSatFixConstPtr &msg)
{
    std::cout << "begin receive message" << std::endl;
    gps_fix = *msg;
    double longtitude = gps_fix.longitude;
    double latitude = gps_fix.latitude;
    double altitude = gps_fix.altitude;
    std::cout << longtitude << " " << latitude << " " <<altitude << std::endl;
    MogoCurl *pCurl = new MogoCurl;
    pCurl->Init();
    std::string url_list = "https://mdev.zhidaohulian.com/config/map/list";
    std::string url_check = "https://mdev.zhidaohulian.com/config/map/sync";
    std::string SN = pCurl->GetPlate();
    char szMac[18];
    int nRtn = get_mac(szMac, sizeof(szMac));
    for(int i=0; i<strlen(szMac); i++)
    {
	    szMac[i] = tolower(szMac[i]);
    }
    

    bool flag = true;
    flag = pCurl->DownloadFileMapImpl(url_list, url_check, szMac, SN, longtitude, latitude, altitude);
    if(flag == false)
    {
	    int times = 0;
	    while(times++<5)
	    {
		    sleep(1);
		    flag = pCurl->DownloadFileMapImpl(url_list, url_check, szMac, SN, longtitude, latitude, altitude);
		    if(flag ==true) break;
	    }
    }
    delete pCurl;
    exit(0);
}

int main(int argc, char **argv)
{
	sleep(180);
	//MogoCurl *pCurl = new MogoCurl;
	//std::string file_path = "test.ps";
	//std::string url = "https://map-algorithm-huadong-1255510688.cos.ap-beijing.myqcloud.com/data/%E4%B8%B4%E6%97%B6%E6%B5%8B%E8%AF%95.jpg";
	//pCurl->Download(url, file_path);

	double longtitude = gps_fix.longitude;
	double latitude = gps_fix.latitude;
	double altitude = gps_fix.altitude;
	std::cout << longtitude << " " << latitude << " " <<altitude << std::endl;
	MogoCurl *pCurl = new MogoCurl;
	pCurl->Init();
	std::string url_list = "https://mdev-qa.zhidaohulian.com/config/map/list";
	std::string url_check = "https://mdev-qa.zhidaohulian.com/config/map/sync";
	std::string SN = pCurl->GetPlate();

	char szMac[18];
	int nRtn = get_mac(szMac, sizeof(szMac));
	for(int i=0; i<strlen(szMac); i++)
	{
		if(szMac[i]>='A' && szMac[i]<='Z')
		szMac[i] = tolower(szMac[i]);
	}
	std::cout << "mac is " << szMac << std::endl;
	
	/*
	bool flag = true;
	flag = pCurl->DownloadFileMapImpl(url_list, url_check, szMac, SN, longtitude, latitude, altitude);
	if(flag == false)
	{
		int times = 0;
		while(times++<5)
		{
			sleep(1);
			flag = pCurl->DownloadFileMapImpl(url_list, url_check, szMac, SN, longtitude, latitude, altitude);
			if(flag ==true) break;
		}
	}
	delete pCurl;

	*/	
	ros::init(argc, argv, "update_map");
	ros::NodeHandle n("~");
	ros::Subscriber sub_gps = n.subscribe("/sensor/gnss/gps_fix", 1000, GpsFixCallback);
	ros::NodeHandle h_node;
        ros::Rate loop_rate(1);
	int sec = 0;
        while(ros::ok() && sec++ < 5)
        {
                loop_rate.sleep();
                ROS_INFO("ROS is ok!");
                ros::spinOnce();
        }
	return 0;
}