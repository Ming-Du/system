#ifndef MOGO_CURL_H_
#define MOGO_CURL_H_

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <curl/curl.h>
#include <sstream>
#include <iostream>
#include <list>
#include <string>
#include <functional>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <net/if.h>

#include "md5.h"

struct FileInfo 
{
 const char *filename;
 FILE *stream;
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

static size_t my_fwrite(void *buffer, size_t size, size_t nmemb, void *stream)
{
	struct FileInfo *out=(struct FileInfo *)stream;
	if(out && !out->stream) 
	{
		out->stream=fopen(out->filename, "wb");
		if(!out->stream)
			return -1;
	}
	return fwrite(buffer, size, nmemb, out->stream);
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

	return snprintf (mac, len_limit, "%X:%X:%X:%X:%X:%X", (unsigned char) ifreq.ifr_hwaddr.sa_data[0], (unsigned char) ifreq.ifr_hwaddr.sa_data[1], (unsigned char) ifreq.ifr_hwaddr.sa_data[2], (unsigned char) ifreq.ifr_hwaddr.sa_data[3], (unsigned char) ifreq.ifr_hwaddr.sa_data[4], (unsigned char) ifreq.ifr_hwaddr.sa_data[5]);
}


/*
static size_t write_data(void *ptr, size_t size, size_t nmemb, void *stream) 
{
	std::string data((const char*) ptr, (size_t) size * nmemb);
	*((std::stringstream*) stream) << data << std::endl;
	return size * nmemb;
}
*/

class MogoCurl
{
	public:
		MogoCurl();
		~MogoCurl();
		CURLcode Init();
		std::string GetPlate();
		bool DownloadFileContentImpl(const std::string &update_url, const std::string &download_url, const std::string &check_url, const std::string &mac_addr, const std::string &SN);
	private:
		bool GetUpdateFileList(const std::string &update_url, const std::string &mac_addr, 
				const std::string &SN, std::list<std::string> &file_list);

		bool DownloadFileContent(const std::string &download_url, const std::string check_url, const std::string &SN, const std::string &mac_addr, const std::string &fileName);
	private:
		CURLcode Get(const std::string &url, std::string &rstr);
		CURLcode Post(const std::string &url, const std::string &pstr, std::string &rstr);
	private:
		CURL *m_curl_handle;
		MD5 m_md5;
};
#endif
