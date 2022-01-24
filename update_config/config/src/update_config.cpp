//#include <ros/ros.h>

#include "mogo_curl.h"
#include "const.h"
#include "md5.h"

bool UpdatePbFile()
{
	MogoCurl *pCurl = new MogoCurl;
	pCurl->Init();
	std::string url_list = "https://mdev-qa.zhidaohulian.com/config/driver/list";
	std::string url_pull = "https://mdev-qa.zhidaohulian.com/config/driver/pull";
	std::string url_sync = "https://mdev-qa.zhidaohulian.com/config/driver/sync";
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
			usleep(50);
			flag = pCurl->DownloadFileContentImpl(url_list, url_pull, url_sync, szMac, SN);
			if(flag ==true) break;
		}
	}
	delete pCurl;
	return flag;
}

int main(int argc, char **argv)
{
	bool flag = UpdatePbFile();
	std::cout << "update pb file success" << flag << std::endl;
	return 0;
}
