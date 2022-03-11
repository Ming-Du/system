#include <ros/ros.h>
#include <signal.h>

#include <sys/types.h>
#include <dirent.h>
#include <unistd.h>
#include <vector>

#include "mogo_curl.h"
#include "const.h"
#include "md5.h"

bool MoveTempMapFile()
{
	std::string map_path = "/autocar-code/install/share/hadmap_engine/data/hadmap_data/";
	DIR *dir = opendir(map_path.c_str());
	struct dirent *ptr;
	while((ptr = readdir(dir)) != NULL)
	{
		std::string temp_file_path = ptr->d_name;
		size_t pos = temp_file_path.find(".sqlite.temp");
		if(pos != -1)
		{
			std::string mv_cmd = "mv " + map_path + temp_file_path + " " + map_path + temp_file_path.substr(0, temp_file_path.size()-5);
			system(mv_cmd.c_str());
		}
	}
	closedir(dir);
}

bool UpdatePbFile()
{
	MogoCurl *pCurl = new MogoCurl;
	pCurl->Init();
	std::string url_list = "https://mdev.zhidaohulian.com/config/driver/list";
	std::string url_pull = "https://mdev.zhidaohulian.com/config/driver/pull";
	std::string url_sync = "https://mdev.zhidaohulian.com/config/driver/sync";
	std::string SN = pCurl->GetPlate();
	char szMac[18];
	int nRtn = get_mac(szMac, sizeof(szMac));
	for(int i=0; i<strlen(szMac); i++)
        {
                szMac[i] = tolower(szMac[i]);
        }
	bool flag = true;
	flag = pCurl->DownloadFileContentImpl(url_list, url_pull, url_sync, szMac, SN);
	if(flag == false)
	{
		int times = 0;
		while(times++<5)
		{
			sleep(1);
			flag = pCurl->DownloadFileContentImpl(url_list, url_pull, url_sync, szMac, SN);
			if(flag ==true) break;
		}
	}
	delete pCurl;
	return flag;
}


bool UpdateOtherFile()
{
	MogoCurl *pCurl = new MogoCurl;
	pCurl->Init();
	std::string url_list = "https://mdev.zhidaohulian.com/config/file/list";
	std::string url_sync = "https://mdev.zhidaohulian.com/config/file/sync";
	std::string SN = pCurl->GetPlate();
	char szMac[18];
	int nRtn = get_mac(szMac, sizeof(szMac));
	for(int i=0; i<strlen(szMac); i++)
        {
                szMac[i] = tolower(szMac[i]);
        }
	bool flag = true;
	flag = pCurl->DownloadBinaryFileImpl(url_list, url_sync, szMac, SN);
	if(flag == false)
	{
		int times = 0;
		while(times++<5)
		{
			sleep(1);
			flag = pCurl->DownloadBinaryFileImpl(url_list, url_sync, szMac, SN);
			if(flag ==true) break;
		}
	}
	delete pCurl;
	return flag;
}


int main(int argc, char **argv)
{
	//gflags::ParseCommandLineFlags(&argc, &argv, true);
	ros::init(argc, argv, "update_config_cpp");
	ros::NodeHandle h_node;
	ros::Rate loop_rate(1);


	MoveTempMapFile();
	UpdatePbFile();
	UpdateOtherFile();
	int sec = 0;
        while(ros::ok() && sec++ < 1)
        {
                loop_rate.sleep();
                ROS_INFO("ROS is ok!");
                ros::spinOnce();
        }
	ROS_INFO("ROS exit!");
	return 0;
}
