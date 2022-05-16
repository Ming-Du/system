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

SYSVehicleState STATE;

static MogoCurl *pCurl = NULL;

void catch_signal_sigint(int sig)
{
        ROS_ERROR("get signal signal");
}


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
			//std::cout << "pid is " << cur_pid << std::endl;
		}
	}
	else
	{
		//std::cout << "not find this pid " << std::endl;
		return -1;
	}
	pclose(fp);
	return pid;
}


//pilotmode 作为一个全局变量可以供下载线程使用
void ChassisStateCallback(const autopilot_msgs::BinaryDataConstPtr& msg)
{
	RosToProto<SYSVehicleState>(*msg, STATE);
	pilotmode = STATE.pilot_mode();
	//if(pilotmode == 1)
	//{
		//pid_t pid = getProcessId("curl");
		//if(pid != -1)
		//{
		//	kill(pid, 9);
		//}
	//}
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

	//这个file list 是指的云端获取的全量文件列表
	for(auto it=file_list.begin(); it!=file_list.end(); it++)
	{
		std::string file_path = (*it).file_path;
		std::string file_md5 = (*it).md5_str;
		std::string temp_file_path = file_path + ".temp." + file_md5;
		//临时文件不存在，且正式文件也不存在
		if(access(file_path.data(), F_OK)!=0 && access(temp_file_path.data(), F_OK)!=0)
		{
			update_list.emplace_back(*it);
		}
		//temp文件存在
		else if(access(temp_file_path.data(), F_OK)==0)
		{
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
		//if(getProcessId("curl") != -1)
		//{
		//	check_lock.unlock();
		//	continue;
		//}
		//std::cout << "update list is " << update_list.size() << std::endl;
		for(auto it=update_list.begin(); it!=update_list.end();)
		{
			if(pilotmode == 1)//检测到自动驾驶状态 就不再继续下载
			{
				break;
			}
			//如果第一次下载失败需要尝试4次
			bool download_flag = pCurl->DownloadBinaryFile(check_url, SN, mac_addr, *it, 1024*1024*2);
			//std::cout << "download file " << (*it).file_path <<  download_flag << std::endl;
			int times = 0;
			while(!download_flag && times++<4)
			{
				download_flag = pCurl->DownloadBinaryFile(check_url, SN, mac_addr, *it, 1024*1024*2);
			}
			if(!download_flag)
			{
				ROS_ERROR("download binary file error");
			}
			it = update_list.erase(it);
		}
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
		//如果发现有下载的东西 就暂时不检测
		//if(getProcessId("curl") != -1) 
		//{
		//	check_lock.unlock();
		//	continue;
		//}
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

	for(auto it=updated_list.begin(); it!=updated_list.end(); it++)
	{
		std::string file_path = (*it).file_path;
		std::string file_md5 = (*it).md5_str;
		std::string temp_file_path = file_path + ".temp." + file_md5;
		if(access(temp_file_path.c_str(), F_OK) == 0)
		{
			std::string mv_cmd = "mv " + temp_file_path + " " + file_path;
			system(mv_cmd.data());
		}
		std::string line = file_path + ":" + file_md5 + "\n";
		fputs(line.c_str(), fpw);
	}
	updated_list.clear();
	fclose(fpw);
	return true;
}

void UpdateOtherFile()
{
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
	SN = "DFHYD00799";
	mac_str = "48:b0:2d:3c:8b:1c";
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

	std::thread t1(DowloadFileThread, url_sync, mac_str, SN);
	t1.detach();
	std::thread t2(GetFileListThread, url_list, url_sync, mac_str, SN);
	t2.detach();
}


int main(int argc, char **argv)
{
	signal(SIGINT, catch_signal_sigint);
	signal(SIGUSR1, catch_signal_sigusr1);
	signal(SIGUSR2, catch_signal_sigusr2);
	pCurl = new MogoCurl;
	pCurl->Init();
	//gflags::ParseCommandLineFlags(&argc, &argv, true);
	ros::init(argc, argv, "update_config_cpp");
	ros::NodeHandle n("~");
	ros::Subscriber sub_pilot = n.subscribe("/system_master/SysVehicleState", 10, ChassisStateCallback);
	ros::NodeHandle h_node;
	ros::Rate loop_rate(1);

	UpdateOtherFile();
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
