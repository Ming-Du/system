#include <ros/ros.h>
#include <signal.h>
#include <thread>
#include <mutex>
#include <sys/types.h>
#include <dirent.h>
#include <unistd.h>
#include <vector>
#include <ros/ros.h>
#include <sensor_msgs/NavSatFix.h>
#include <ros/time.h>
#include <nav_msgs/Odometry.h>

#include "proto/vehicle_state.pb.h"
#include "proto/system_pilot_mode.pb.h"
#include "proto/chassis.pb.h"
#include "autopilot_msgs/BinaryData.h"
#include "autopilot_msgs/ros_proto.h"

#include "mogo_curl.h"
#include "const.h"
#include "md5.h"



std::atomic<int> pilotmode(0);
std::mutex check_lock;
std::list<DownloadFile> file_list;

std::list<DownloadFile> all_list;
std::list<DownloadFile> update_list;
std::list<DownloadFile> updated_list;

system_master::SYSVehicleState STATE;

static MogoCurl *pCurl = NULL;

void catch_signal_sigint(int sig)
{
        ROS_ERROR("get signal signal");
}


/*
void catch_signal_sigusr1(int sig)
{
	if(sig == SIGUSR1)
	{
		pilotmode = 1;
	}
        ROS_ERROR("get signal sigusr1");
}

void catch_signal_sigusr2(int sig)
{
	if(sig == SIGUSR2)
	{
		pilotmode = 0;
	}
        ROS_ERROR("get signal sigusr2");
}
*/

pid_t getProcessId(const char *process_name)
{
	FILE *fp;
	char buf[1000] = {'\0'};
	char cmd[200] = {'\0'};
	pid_t pid = -1;
	sprintf(cmd, "pidof %s", process_name);
	if((fp = popen(cmd, "r")) != NULL)
	{
		if(fgets(buf, 255, fp) != NULL)
		{
			pid = atoi(buf);
			pid_t cur_pid = getpid();
		}
	}
	else
	{
		return -1;
	}
	pclose(fp);
	return pid;
}

std::map<std::string, std::string> LoadTempFileMap()
{
	std::map<std::string, std::string> temp_file_map;
	FILE *fp_temp_r = fopen("/home/mogo/data/temp_path.list", "r+");
	if(fp_temp_r)
	{
		while(!feof(fp_temp_r))
		{
			char line[1000];
			memset(line, 0, 1000);
			fgets(line,1000,fp_temp_r);
			if(strlen(line)<10) continue;
			std::string str = line;
			string::size_type pos = str.find(":");
			if(pos == -1) continue;
			std::string file_path = str.substr(0, pos);
			std::string file_name = str.substr(pos+1, str.size()-1);
			temp_file_map[file_path] = file_name;
		}
		fclose(fp_temp_r);
	}
	else
	{
		ROS_ERROR("open temp_path.list error");
	}
	return temp_file_map;
}

//pilotmode 作为一个全局变量可以供下载线程使用
void ChassisStateCallback(const autopilot_msgs::BinaryDataConstPtr& msg)
{
	RosToProto<system_master::SYSVehicleState>((*msg), STATE);
	pilotmode = STATE.pilot_mode();
}

bool GetAllFileList(std::string update_url, std::string check_url, std::string mac_addr, std::string SN, std::list<DownloadFile> &file_list)
{
	if(!pCurl->GetUpdateBinaryFileList(update_url, mac_addr, SN, file_list)) return false;
	return true;
}

bool GetUpdateFileList(std::string update_url, std::string check_url, std::string mac_addr, std::string SN, std::list<DownloadFile> &file_list, 
		std::list<DownloadFile> &update_list, std::list<DownloadFile> &updated_list)
{
	if(!GetAllFileList(update_url, check_url, mac_addr, SN, file_list)) return false;
	std::map<std::string, std::string> file_md5_map;

	char line[1000];
	FILE *fpr = fopen("/home/mogo/data/all_file_md5.list", "r+");
	if(fpr)
	{
		while(!feof(fpr))
		{
			memset(line, 0, 1000);
			fgets(line,1000,fpr);
			if(strlen(line)<10) continue;
			std::string str = line;
			string::size_type pos = str.find(":");
			if(pos == -1) continue;
			std::string path = str.substr(0, pos);
			std::string md5sum = str.substr(pos+1, 32);
			file_md5_map[path] = md5sum;
		}
		fclose(fpr);
	}
	else
	{
		ROS_ERROR("open all file md5 list error");
	}
	
	std::map<std::string, std::string> temp_file_map = LoadTempFileMap();

	//这个file list 是指的云端获取的全量文件列表
	for(auto it=file_list.begin(); it!=file_list.end(); it++)
	{
		std::string file_path = (*it).file_path;
		std::string file_md5 = (*it).md5_str;
		int pos = file_path.find_last_of("/");
		std::string file_name = file_path.substr(pos+1, file_path.size());	
		std::string temp_file_path = "/home/mogo/data/temp/" + file_name + ".temp." + file_md5;
		
		//检测删除过期的临时文件,可能因为没有下载完而被覆盖了新的版本
		{
			for(auto it_map=temp_file_map.begin(); it_map!=temp_file_map.end(); it_map++)
			{
				std::string p_file_path = it_map->first;
				std::string path = p_file_path.substr(0, p_file_path.size()-38);
				std::string check_md5 = p_file_path.substr(p_file_path.size()-32, 32);
				if(file_path==path && file_md5!=check_md5 && access(temp_file_path.c_str(), F_OK)==0)
				{
					std::string rm_cmd = "rm -rf " + temp_file_path;
					system(rm_cmd.c_str());
				}
			}
		}
		//临时文件不存在，且正式文件也不存在
		if(access(file_path.data(), F_OK)!=0 && access(temp_file_path.data(), F_OK)!=0)
		{
			update_list.emplace_back(*it);
		}
		//temp文件存在
		else if(access(temp_file_path.data(), F_OK)==0)
		{
			if(pilotmode==1)//计算md5的时候判断自动驾驶状态
			{
				while(pilotmode==1)
				{
					sleep(1);
				}
			}
			//to do
			//因为temp文件不确定是否下载完成，所以需要去实际计算跟云端的对比
			MD5 p_md5;
			p_md5.reset();
			ifstream in(temp_file_path.data(), std::ios::binary);
			p_md5.update(in);
			std::string temp_file_md5 = p_md5.toString();
			if(temp_file_md5 != file_md5)
			{
				update_list.emplace_back(*it);
			}
			else
			{
				updated_list.emplace_back(*it);
			}
		}
		//正式文件存在，但是md5不一样，也是需要更新的
		else if(access(file_path.data(), F_OK)==0)
		{
			if(file_md5_map[file_path]!=file_md5)
			{
				update_list.emplace_back(*it);
			}
			else
			{
				updated_list.emplace_back(*it);
			}
		}
	}
	FILE *fp_temp_w = fopen("/home/mogo/data/temp_path.list", "w+");
	if(fp_temp_w)
	{
		for(auto it=update_list.begin(); it!=update_list.end(); it++)
		{
			std::string file_path = (*it).file_path + ".temp." + (*it).md5_str;;
			int pos = file_path.find_last_of("/");
			std::string file_name = file_path.substr(pos+1, file_path.size());
			std::string line = file_path + ":" + file_name + "\n";
			fputs(line.c_str(), fp_temp_w);
		}
		fclose(fp_temp_w);
	}
	return true;
}

void DowloadFileThread(std::string check_url, std::string mac_addr, std::string SN)
{
	while(1)
	{
		sleep(10);
		check_lock.lock();
		if(pilotmode == 1)
		{
			check_lock.unlock();
			continue;
		}

		//需要把文件下载到固定的temp目录下面
		for(auto it=update_list.begin(); it!=update_list.end(); it++)
		{
			if(pilotmode == 1)//检测到自动驾驶状态 就不再继续下载
			{
				break;
			}
			//如果第一次下载失败需要尝试4次
			bool download_flag = pCurl->DownloadBinaryFile(check_url, SN, mac_addr, *it, 1024*1024*2);
			int times = 0;
			while(!download_flag && times++<4)
			{
				sleep(1);
				download_flag = pCurl->DownloadBinaryFile(check_url, SN, mac_addr, *it, 1024*1024*2);
			}
			if(!download_flag)
			{
				ROS_ERROR("download binary file %s error", (*it).file_path);
			}
		}
		update_list.clear();
		all_list.clear();
		check_lock.unlock();
	}
}



void GetFileListThread(std::string update_url, std::string sync_url,  std::string mac_addr, std::string SN)
{
	while(1)
	{
		sleep(10);
		
		check_lock.lock();
		//如果发现是自动驾驶状态 就暂时不检测
		if(pilotmode == 1)
		{
			check_lock.unlock();
			continue;
		}

		GetUpdateFileList(update_url, sync_url, mac_addr, SN, all_list, update_list, updated_list);
		check_lock.unlock();
	}
}

bool MoveTempFile()
{
	FILE *fpw = fopen("/home/mogo/data/all_file_md5.list", "w+");
	if(!fpw)
	{
		ROS_ERROR("move temp file open md5 file list error");
		return false;
	}

	for(auto it=updated_list.begin(); it!=updated_list.end(); )
	{
		std::string file_path = (*it).file_path;
		std::string file_md5 = (*it).md5_str;
		int pos = file_path.find_last_of("/");
		std::string file_name = file_path.substr(pos, file_path.size());
		std::string temp_file_path = "/home/mogo/data/temp/" + file_name + ".temp." + file_md5;
		if(access(temp_file_path.c_str(), F_OK) == 0)//确认文件存在才执行move动作
		{
			std::string mv_cmd = "mv " + temp_file_path + " " + file_path;
			system(mv_cmd.data());
		}
		std::string line = file_path + ":" + file_md5 + "\n";
		fputs(line.c_str(), fpw);
		ROS_INFO("update file %s success", file_path.c_str());
		it = updated_list.erase(it);
	}
	fclose(fpw);
	return true;
}

void LinkFile(std::string file_path)
{
	std::map<std::string, std::string> file_link_map;
	std::string SN = pCurl->GetPlate();
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
		std::string rm_cmd = "rm -rf " + link_file;
		std::string link_cmd = "ln -s " + src_file + " " + link_file;
		system(rm_cmd.c_str());
		system(link_cmd.c_str());
	}

}
void UpdateOtherFile()
{
	 FILE *fpw = fopen("/home/mogo/data/download.txt", "w+");
	 if(fpw)
	 {
		 fputs("moved:0", fpw);
		 fclose(fpw);
	 }
	std::string url_list = "https://mdev-qa.zhidaohulian.com/config/file/list";
	std::string url_sync = "https://mdev-qa.zhidaohulian.com/config/file/sync";
	std::string SN = pCurl->GetPlate();
	char szMac[18];
	int nRtn = get_mac(szMac, sizeof(szMac));
	for(int i=0; i<strlen(szMac); i++)
	{
		szMac[i] = tolower(szMac[i]);
	}
	std::string mac_str = szMac;
	bool flag = true;

	//move 操作只在进程起来的时候做一次
	if(!GetUpdateFileList(url_list, url_sync, mac_str, SN, all_list, update_list, updated_list))
	{
		ROS_ERROR("get update file list error");
		return;
	}
	if(!MoveTempFile()) 
	{
		ROS_ERROR("move temp file error");
		return;
	}

	LinkFile("/home/mogo/autopilot/share/config/vehicle/slinks.cfg");
	LinkFile("/home/mogo/data/vehicle_monitor/slinks.cfg");
	
	fpw = fopen("/home/mogo/data/download.txt", "w+");	
	if(fpw)
	{
		fputs("moved:1", fpw);
		fclose(fpw);
	}
	std::thread t1(DowloadFileThread, url_sync, mac_str, SN);
	t1.detach();
	std::thread t2(GetFileListThread, url_list, url_sync, mac_str, SN);
	t2.detach();
}


int main(int argc, char **argv)
{
	signal(SIGINT, catch_signal_sigint);
	//signal(SIGUSR1, catch_signal_sigusr1);
	//signal(SIGUSR2, catch_signal_sigusr2);
	pCurl = new MogoCurl;
	pCurl->Init();
	
	UpdateOtherFile();
		
	//gflags::ParseCommandLineFlags(&argc, &argv, true);
	ros::init(argc, argv, "update_config_cpp");
	ros::NodeHandle n("~");
	ros::Subscriber sub_pilot = n.subscribe("/system_master/SysVehicleState", 10, ChassisStateCallback);
	ros::NodeHandle h_node;
	ros::Rate loop_rate(1);

	while(ros::ok())
	{
		loop_rate.sleep();
		ROS_INFO("ROS is ok!");
		ros::spin();
	}
	ROS_INFO("ROS exit!");
	delete pCurl;
	return 0;
}
