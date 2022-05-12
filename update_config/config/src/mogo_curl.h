#ifndef MOGO_CURL_H_
#define MOGO_CURL_H_

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <curl/curl.h>
#include <sys/stat.h>
#include <sstream>
#include <iostream>
#include <list>
#include <map>
#include <string>
#include <functional>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <net/if.h>

#include "md5.h"

extern std::atomic<int> pilotmode;


struct DownloadFile
{
	std::string file_path;
	std::string map_url;
	std::string version;
	std::string md5_str;
	std::string file_id;
};

struct MemoryStruct 
{
	char *memory;
	size_t size;
	MemoryStruct()
	{
		memory = (char *)malloc(1);  
		size = 0;
	}
	~MemoryStruct()
	{
		free(memory);
		memory = NULL;
		size = 0;
	}
};


static size_t my_write_func(void *ptr, size_t size, size_t nmemb, int *stream)
{
	int ret = 0;	
	do
	{
		if(pilotmode == 1) break;
		ret = write(*stream, ptr, size*nmemb);
	}while(0);
	return ret;
}

static int my_progress_func(char *progress_data,
		double t, /* dltotal */
		double d, /* dlnow */
		double ultotal,
		double ulnow)
{
	printf("%s %g / %g (%g %%)\n", progress_data, d, t, d*100.0/t);
	return 0;
}

static size_t getcontentlength_func(void *ptr, size_t size, size_t nmemb, void *stream) 
{
	int r;
	long len = 0;
	r = sscanf((char *)ptr, "Content-Length: %ld/n", &len);
	if (r) *((long *) stream) = len;
	return size * nmemb;
}

static size_t write_data(void *ptr, size_t size, size_t nmemb, void *data)
{
	size_t realsize = size * nmemb;
	struct MemoryStruct *mem = (struct MemoryStruct *)data;

	mem->memory = (char *)realloc(mem->memory, mem->size + realsize + 1);
	if (mem->memory) 
	{
		memcpy(&(mem->memory[mem->size]), ptr, realsize);
		mem->size += realsize;
		mem->memory[mem->size] = 0;
	}
	return realsize;
}

static off_t getLocalFileLength(std::string path)
{
	off_t ret = -1;
	struct stat fileStat;
	ret = stat(path.c_str(), &fileStat);
	if (ret == 0)
	{
		return fileStat.st_size;
	}
	return ret;
}


static int get_mac(char * mac, int len_limit)
{
	struct ifreq ifreq;
	int sock;

	if ((sock = socket (AF_INET, SOCK_STREAM, 0)) < 0)
	{
		perror ("socket");
		return -1;
	}
	strcpy (ifreq.ifr_name, "eth0");    //Currently, only get eth0

	if (ioctl (sock, SIOCGIFHWADDR, &ifreq) < 0)
	{
		perror ("ioctl");
		return -1;
	}

	return snprintf (mac, len_limit, "%02X:%02X:%02X:%02X:%02X:%02X", (unsigned char) ifreq.ifr_hwaddr.sa_data[0], (unsigned char) ifreq.ifr_hwaddr.sa_data[1], (unsigned char) ifreq.ifr_hwaddr.sa_data[2], (unsigned char) ifreq.ifr_hwaddr.sa_data[3], (unsigned char) ifreq.ifr_hwaddr.sa_data[4], (unsigned char) ifreq.ifr_hwaddr.sa_data[5]);
}


class MogoCurl
{
	public:
		MogoCurl();
		~MogoCurl();
		CURLcode Init();
		std::string GetPlate();
		bool GetUpdateBinaryFileList(const std::string &update_url, const std::string &mac_addr, const std::string &SN, 
				std::list<DownloadFile> &file_list);

		bool DownloadBinaryFile(const std::string check_url, const std::string &SN, const std::string &mac_addr, const DownloadFile &pFile, int rate);

		bool DownloadFileContentImpl(const std::string &update_url, const std::string &download_url, const std::string &check_url, const std::string &mac_addr, const std::string &SN);
	private:


		bool GetUpdateFileList(const std::string &update_url, const std::string &mac_addr, 
				const std::string &SN, std::list<std::string> &file_list);


		bool DownloadFileContent(const std::string &download_url, const std::string check_url, const std::string &SN, const std::string &mac_addr, const std::string &fileName);
	private:
		CURLcode Download(const std::string &url, std::string &file_path, int rate);
		CURLcode Get(const std::string &url, std::string &rstr);
		CURLcode Post(const std::string &url, const std::string &pstr, std::string &rstr);
	private:
		CURL *m_curl_handle;
		MD5 m_md5;
};
#endif
