#include <ros/ros.h>
#include <signal.h>

#include <sys/types.h>
#include <dirent.h>
#include <unistd.h>
#include <vector>
#include <map>

#include "mogo_curl.h"
#include "const.h"
#include "md5.h"

bool MoveTempMapFile()
{
	std::string map_path = "/home/mogo/autopilot/share/hadmap_engine/data/hadmap_data/";
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


void LinkFile(std::string file_path, std::string SN)
{
        std::map<std::string, std::string> file_link_map;
        std::string rm_cmd = "rm -rf /home/mogo/autopilot/share/config/vehicle";
        system(rm_cmd.c_str());
        std::string link_cmd = "ln -s /home/mogo/data/vehicle_monitor/" + SN + " /home/mogo/autopilot/share/config/vehicle";
        system(link_cmd.c_str());
        char line[1000];
        FILE *fpr = fopen(file_path.c_str(), "r+");
        if(fpr)
        {
                while(!feof(fpr))
                {
                        memset(line, 0, 1000);
                        fgets(line,1000,fpr);
                        if(strlen(line)<10) continue;
                        std::string str = line;
                        if(str[str.size()-1]=='\n')
                        {
                                str = str.substr(0, str.size()-1);
                        }
                        string::size_type pos = str.find(":");
                        if(pos == -1) continue;
                        std::string src_path = str.substr(0, pos);
                        std::string link_path = str.substr(pos+1, str.size());
                        file_link_map[src_path] = link_path;
                }
                fclose(fpr);
        }
        else
        {
                ROS_ERROR("open all file link list error");
        }
	        for(auto it=file_link_map.begin(); it!=file_link_map.end(); it++)
        {
                std::string src_file = it->first;
                std::string link_file = it->second;
		if(access(link_file.c_str(), F_OK)==0)
                {
                        std::string rm_cmd = "rm -rf " + link_file;
                        system(rm_cmd.c_str());
                }
                if(access(src_file.c_str(), F_OK)==0)
                {
                        std::string link_cmd = "ln -s " + src_file + " " + link_file;
                        system(link_cmd.c_str());
                }
        }
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
	LinkFile("/home/mogo/autopilot/share/config/vehicle/slinks.cfg", SN);
        LinkFile("/home/mogo/data/vehicle_monitor/slinks.cfg", SN);

	return flag;
}


int main(int argc, char **argv)
{
	//gflags::ParseCommandLineFlags(&argc, &argv, true);
	ros::init(argc, argv, "update_config_cpp");
	ros::NodeHandle h_node;
	ros::Rate loop_rate(1);


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
