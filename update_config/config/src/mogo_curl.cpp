#include <ros/ros.h>
#include<sys/types.h>  /*提供类型pid_t,size_t的定义*/

#include<sys/stat.h>

#include<fcntl.h>
#include<stdio.h>
#include<stdlib.h>
#include<unistd.h>

#include "mogo_curl.h"
#include "mogo_json.h"
#include "md5.h"
#include <fstream>

MogoCurl::MogoCurl()
{}

MogoCurl::~MogoCurl()
{
	curl_easy_cleanup(m_curl_handle);
	curl_global_cleanup();
}

CURLcode MogoCurl::Init()
{
	CURLcode error;
	curl_global_init(CURL_GLOBAL_ALL);
	m_curl_handle = curl_easy_init();
	curl_easy_setopt(m_curl_handle, CURLOPT_WRITEFUNCTION, write_data);
}

CURLcode MogoCurl::Get(const std::string &url, std::string &rstr)
{
	std::stringstream out;
	curl_easy_setopt(m_curl_handle, CURLOPT_WRITEDATA, &out);
	CURLcode res = curl_easy_perform(m_curl_handle);
	if(res != CURLE_OK)
	{
		return res;
	}
	rstr = out.str();
	return res;
}

CURLcode MogoCurl::Post(const std::string &url, const std::string &pstr, std::string &rstr)
{
	curl_easy_setopt(m_curl_handle, CURLOPT_DNS_SERVERS, "8.8.8.8");
	curl_easy_setopt(m_curl_handle, CURLOPT_URL, url.c_str());
	curl_easy_setopt(m_curl_handle, CURLOPT_POST, 1);
	curl_easy_setopt(m_curl_handle, CURLOPT_POSTFIELDS, pstr.c_str());
	//curl_easy_setopt(m_curl_handle, CURLOPT_READFUNCTION, NULL);
	//curl_easy_setopt(m_curl_handle, CURLOPT_NOSIGNAL, 1);
	//curl_easy_setopt(m_curl_handle, CURLOPT_CONNECTTIMEOUT_MS, 200);
	//curl_easy_setopt(m_curl_handle, CURLOPT_TIMEOUT, 200);

	//curl_easy_setopt(m_curl_handle, CURLOPT_FOLLOWLOCATION, 1);
	//curl_easy_setopt(m_curl_handle, CURLOPT_TCP_KEEPALIVE, 1L);  // enable TCP keep-alive for this transfer 
	//curl_easy_setopt(m_curl_handle, CURLOPT_TCP_KEEPIDLE, 120L);	// keep-alive idle time to 120 seconds 
	//curl_easy_setopt(m_curl_handle, CURLOPT_TCP_KEEPINTVL, 60L);

	struct curl_slist* headers = NULL;
	headers = curl_slist_append(headers, "Content-Type:application/json;charset=UTF-8");
	curl_easy_setopt(m_curl_handle, CURLOPT_HTTPHEADER, headers);
	curl_easy_setopt(m_curl_handle, CURLOPT_POST, 1);// set post

	MemoryStruct oDataChunk;
	curl_easy_setopt(m_curl_handle, CURLOPT_WRITEDATA, &oDataChunk);
	curl_easy_setopt(m_curl_handle, CURLOPT_WRITEFUNCTION, write_data);
	CURLcode res = curl_easy_perform(m_curl_handle);
	rstr = oDataChunk.memory;
	return res;
}


CURLcode MogoCurl::Download(const std::string &url, std::string &file_path)
{
	string download_cmd = "curl -o " + file_path + " " + url;
        system(download_cmd.c_str());
        return CURLE_OK;
	/*
	m_curl_handle = curl_easy_init();
        int outfile;
        CURLcode res;
        const char *progress_data = "* ";
        outfile = open(file_path.c_str(), O_RDWR|O_CREAT, 0777);

        if(m_curl_handle)
        {
		curl_easy_setopt(m_curl_handle, CURLOPT_DNS_SERVERS, "8.8.8.8");
                curl_easy_setopt(m_curl_handle, CURLOPT_URL, url.data());
                curl_easy_setopt(m_curl_handle, CURLOPT_WRITEDATA, (void *)&outfile);
                curl_easy_setopt(m_curl_handle, CURLOPT_WRITEFUNCTION, my_write_func);
                curl_easy_setopt(m_curl_handle, CURLOPT_NOPROGRESS, 0);
                curl_easy_setopt(m_curl_handle, CURLOPT_PROGRESSFUNCTION, my_progress_func);
                curl_easy_setopt(m_curl_handle, CURLOPT_PROGRESSDATA, progress_data);

                res = curl_easy_perform(m_curl_handle);

        }
        close(outfile);
        return res;
	*/
}

bool MogoCurl::GetUpdateBinaryFileList(const std::string &update_url, const std::string &mac_addr, 
		const std::string &SN, std::list<DownloadFile> &file_list)
{
	Json::Value root;
	Json::FastWriter fast_writer;
	root["sn"]=SN;
	root["mac"] = mac_addr;
	std::string pstr = fast_writer.write(root);
	ROS_INFO("update config GetUpdateBinaryFileList post str [%s]", pstr.data());
	std::string rstr;
	if(Post(update_url, pstr, rstr) != CURLE_OK) 
	{
		ROS_ERROR("update config GetBinaryUpdateFileList post str [%s] error", pstr.data());
		return false;
	}
	ROS_INFO("update config GetUpdateBinaryFileList response str [%s]", rstr.data());
	MyJson pJson;
	if(!pJson.parse(rstr)) 
	{
		ROS_ERROR("update config GetUpdateBinaryFileList parse json rstr [%s] error", rstr.data());
		return false;
	}

	int errcode = -1;
	if(!pJson.getInt("errcode", errcode) || errcode!=0) 
	{
		ROS_ERROR("update config GetUpdateBinaryFileList parse json get errcode rstr [%s] error", rstr.data());
		return false;
	}
	Json::Value arrayObj;
	if(!pJson.getArray("data", arrayObj)) 
	{
		ROS_ERROR("update config GetUpdateBinaryFileList parse json get data rstr [%s] error", rstr.data());
		return false;
	}
	MyJson pArrayJson(arrayObj);
	int list_size = pArrayJson.getSize();
	for(size_t i=0; i<list_size; i++)
	{
		Json::Value obj = pJson.getObjectIndex("data", i);
		MyJson pObjJson(obj);
		std::string file_path;
		if(!pObjJson.getString("filepath", file_path)) 
		{
			ROS_ERROR("update config GetUpdateBinaryFileList parse json get filepath rstr [%s] error", rstr.data());
			return false;
		}
		std::string md5_str;
		if(!pObjJson.getString("md5", md5_str)) 
		{
			ROS_ERROR("update config GetUpdateBinaryFileList parse json get md5 rstr [%s] error", rstr.data());
			return false;
		}
		int update;
		if(!pObjJson.getInt("update", update)) 
		{
			ROS_ERROR("update config GetUpdateBinaryFileList parse json get update rstr [%s] error", rstr.data());
			return false;
		}

		std::string map_url;
		if(!pObjJson.getString("content", map_url))
		{
			ROS_ERROR("update config GetUpdateBinaryFileList parse json get content rstr [%s] error", rstr.data());
			return false;
		}

		std::string version;
		if(!pObjJson.getString("version", version))
                {
                        ROS_ERROR("update config GetUpdateBinaryFileList parse json get version rstr [%s] error", rstr.data());
                        return false;
                }

		DownloadFile pFile = {file_path, map_url, version};
		if(access(file_path.data(), F_OK)!=0)
		{
			file_list.emplace_back(pFile);
		}
		else
		{
			m_md5.reset();
			ifstream in(file_path.data(), std::ios::binary);
			m_md5.update(in);
			if(m_md5.toString()!=md5_str)
			{
				file_list.emplace_back(pFile);
			}
		}
	}
	return true;
}


bool MogoCurl::DownloadBinaryFile(const std::string check_url, const std::string &SN, const std::string &mac_addr, const DownloadFile &pFile)
{
	Json::Value root;
	root["sn"]=SN;
	root["mac"] = mac_addr;

	std::string file_path = pFile.file_path;
	int pos = file_path.find_last_of("/");
	std::string path_str = file_path.substr(0, pos);
	if(access(path_str.data(), NULL) != 0)
	{
		ROS_WARN("update config DownloadBinaryFile create dir [%s] error", path_str.data());
		CreateDir(path_str.data());
	}

	std::string file_url = pFile.map_url;
	std::string version = pFile.version;

	std::string mv_cmd = "mv " + file_path + " " + file_path + "_bak";
        system(mv_cmd.data());

	std::string pstr;
	std::string rstr;
	if(Download(file_url, file_path) != CURLE_OK)
        {
		ROS_ERROR("update config DownloadBinaryFile download map [%s] error", file_path.data());
                return false;
        }

	m_md5.reset();
	ifstream in(file_path.data(), std::ios::binary);
	m_md5.update(in);
	//get file md5
	root["md5"] = Json::Value(m_md5.toString());
	root["version"] = Json::Value(version);
	root["filepath"] = file_path;
	Json::FastWriter fast_writer;
	pstr = fast_writer.write(root);
	if(Post(check_url, pstr, rstr) != CURLE_OK) 
	{
		mv_cmd = "mv " + file_path + "_bak " + file_path;
                system(mv_cmd.data());
		return false;
	}

	MyJson pJson;
	if(!pJson.parse(rstr)) return false;
	int res_code = -1;
	if(!pJson.getInt("errcode", res_code) || res_code!=0)
	{
		mv_cmd = "mv " + file_path + "_bak " + file_path;
		system(mv_cmd.data());
		return false;
	}
	return true;
}


bool MogoCurl::DownloadBinaryFileImpl(const std::string &update_url, const std::string &check_url, const std::string &mac_addr, const std::string &SN)
{
	bool flag = true;
	std::list<DownloadFile> file_list;
	if(!GetUpdateBinaryFileList(update_url, mac_addr, SN, file_list)) return false;
	
	for(auto it=file_list.begin(); it!=file_list.end(); it++)
	{
		if(!DownloadBinaryFile(check_url, SN, mac_addr, *it))
		{
			flag = false;
		}
	}
	return flag;
}


bool MogoCurl::GetUpdateFileList(const std::string &update_url, const std::string &mac_addr, const std::string &SN, std::list<std::string> &file_list)
{
	Json::Value root;
	Json::FastWriter fast_writer;
	root["sn"]=SN;
	root["mac"] = mac_addr;
	std::string pstr = fast_writer.write(root);
	ROS_INFO("update config GetUpdateFileList post str [%s]", pstr.data());
	std::string rstr;
	if(Post(update_url, pstr, rstr) != CURLE_OK) 
	{
		ROS_ERROR("update config GetUpdateFileList post str [%s] error", pstr.data());
		return false;
	}
	ROS_INFO("update config GetUpdateFileList response str [%s]", rstr.data());
	MyJson pJson;
	if(!pJson.parse(rstr)) 
	{
		ROS_ERROR("update config GetUpdateFileList parse json rstr [%s] error", rstr.data());
		return false;
	}

	int errcode = -1;
	if(!pJson.getInt("errcode", errcode) || errcode!=0) 
	{
		ROS_ERROR("update config GetUpdateFileList parse json get errcode rstr [%s] error", rstr.data());
		return false;
	}
	Json::Value arrayObj;
	if(!pJson.getArray("data", arrayObj)) 
	{
		ROS_ERROR("update config GetUpdateFileList parse json get data rstr [%s] error", rstr.data());
		return false;
	}
	MyJson pArrayJson(arrayObj);
	int list_size = pArrayJson.getSize();
	for(size_t i=0; i<list_size; i++)
	{
		Json::Value obj = pJson.getObjectIndex("data", i);
		MyJson pObjJson(obj);
		std::string file_path;
		if(!pObjJson.getString("filepath", file_path)) 
		{
			ROS_ERROR("update config GetUpdateFileList parse json get filepath rstr [%s] error", rstr.data());
			return false;
		}
		std::string md5_str;
		if(!pObjJson.getString("md5", md5_str)) 
		{
			ROS_ERROR("update config GetUpdateFileList parse json get md5 rstr [%s] error", rstr.data());
			return false;
		}
		int update;
		if(!pObjJson.getInt("update", update)) 
		{
			ROS_ERROR("update config GetUpdateFileList parse json get update rstr [%s] error", rstr.data());
			return false;
		}

		if(access(file_path.data(), NULL)!=0)
		{
			file_list.emplace_back(file_path);
		}
		else 
		{
			m_md5.reset();
			ifstream in(file_path.data(), std::ios::binary);
			m_md5.update(in);
			if(m_md5.toString()!=md5_str)
			{
				file_list.emplace_back(file_path);
				//size_t pos = file_path.find_last_of("/");
				//file_list.emplace_back(file_path.substr(pos, file_path.size()));
			}
		}
	}
	return true;
}


bool MogoCurl::DownloadFileContent(const std::string &download_url, const std::string check_url, const std::string &SN, const std::string &mac_addr, const std::string &fileName)
{
	Json::Value root;
	Json::FastWriter fast_writer;
	root["sn"]=SN;
	root["mac"] = mac_addr;
	root["filepath"] = fileName;
	std::string pstr = fast_writer.write(root);
	std::string rstr;
	ROS_INFO("update config DownloadFileContent post str [%s]", pstr.data());
	if(Post(download_url, pstr, rstr) != CURLE_OK) 
	{
		ROS_ERROR("update config DownloadFileContent post str [%s] error", pstr.data());
		return false;
	}
	ROS_INFO("update config DownloadFileContent  response str [%s]", rstr.data());
	MyJson pJson;
	if(!pJson.parse(rstr)) 
	{
		ROS_ERROR("update config DownloadFileContent parse json rstr [%s] error", rstr.data());
		return false;
	}

	int errcode = -1;
        if(!pJson.getInt("errcode", errcode) || errcode!=0) 
	{
		ROS_ERROR("update config DownloadFileContent parse json get errcode rstr [%s] error", rstr.data());
		return false;
	}

	Json::Value dataObj;
	if(!pJson.getObject("data", dataObj));
	MyJson pDataObjJson(dataObj);
	
	std::string file_path;
	if(!pDataObjJson.getString("filepath", file_path))
	{
		ROS_ERROR("update config DownloadFileContent parse json get file_path rstr [%s] error", rstr.data());
		return false;
	}

	int pos = file_path.find_last_of("/");
	std::string path_str = file_path.substr(0, pos);
	if(access(path_str.data(), NULL) != 0)
	{
		ROS_WARN("update config DownloadFileContent create dir [%s]", path_str.data());
		CreateDir(path_str.data());
	}

	std::string file_buf;
	if(!pDataObjJson.getString("content", file_buf))
	{
		ROS_ERROR("update config DownloadFileContent parse json get content rstr [%s] error", rstr.data());
		return false;
	}

	std::string version;
        if(!pDataObjJson.getString("version", version))
        {
		ROS_ERROR("update config DownloadFileContent parse json get version rstr [%s] error", rstr.data());
                return false;
	}

	if(access(file_path.data(), NULL)==0)
	{
		std::string mv_cmd = "mv " + file_path + " " + file_path + "_bak";
		system(mv_cmd.data());
	}
	FILE *fp = fopen(file_path.data(), "wb+");
	if(!fp) return false;
	fwrite(file_buf.data(), 1, file_buf.size(), fp);
	fclose(fp);
	
	m_md5.reset();
	ifstream in(file_path.data(), std::ios::binary);
	m_md5.update(in);
	//get file md5
	root["md5"] = Json::Value(m_md5.toString());
	root["version"] = Json::Value(version);
	pstr = fast_writer.write(root);
	if(Post(check_url, pstr, rstr) != CURLE_OK) 
	{
		std::string mv_cmd = "mv " + file_path + "_bak " + file_path;
                system(mv_cmd.data());
		return false;
	}
	if(!pJson.parse(rstr)) return false;
	int res_code = -1;
	if(!pJson.getInt("errcode", res_code) || res_code!=0)
	{
		ROS_ERROR("update config DownloadFileContent parse json get check code rstr [%s] error", rstr.data());
		std::string mv_cmd = "mv " + file_path + "_bak " + file_path;
		system(mv_cmd.data());
		return false;
	}
	return true;
}

bool MogoCurl::DownloadFileContentImpl(const std::string &update_url, const std::string &download_url, const std::string &check_url, const std::string &mac_addr, const std::string &SN)
{
	bool flag = true;
	std::list<std::string> file_list;
	if(!GetUpdateFileList(update_url, mac_addr, SN, file_list)) return false;
	
	for(auto it=file_list.begin(); it!=file_list.end(); it++)
	{
		if(!DownloadFileContent(download_url, check_url, SN, mac_addr, *it))
		{
			flag = false;
		}
	}
	return flag;
}

std::string MogoCurl::GetPlate()
{
	std::ifstream fin("/home/mogo/data/vehicle_monitor/vehicle_config.txt");
	if(!fin.is_open())
	{
		return "";
	}
	std::string line;
	while(std::getline(fin, line))
	{
		int pos = line.find(":", 0);
		if(pos==std::string::npos)
		{
			continue;
		}
		std::string key = line.substr(0, pos);
		if(key.find("plate") == std::string::npos)
		{
			continue;	
		}
		int pos_start = line.find_first_of("\"")+1;
		int pos_end = line.find_last_of("\"");
		std::string value = line.substr(pos_start, pos_end-pos_start);
		fin.close();
		return value;
	}
	fin.close();
	return "";
}
