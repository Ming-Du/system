/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
#ifndef __OUTPUTTIMEJSON_HPP_
#define __OUTPUTTIMEJSON_HPP_

#include <string>
#include <jsoncpp/json/json.h>
#include <jsoncpp/json/value.h>
#include <fstream>
#include <iostream>
#include <pthread.h>
#include <ros/time.h>
#include <string.h>
#include <stdio.h>


using namespace std;

/**
 * {
    "type":0/1,                                	   //埋点类型，0为send处的点，1为callback触发处的点
    "stamp":{"sec":123123,"nsec":123123},          //当前时间戳，非空
    "header_stamp":{"sec":123123,"nsec":123123},   //包中的时间戳，可空
    "topic":"/testnode/testtopic",                 //topic名称，非空
    "node":"/testnode",                            //当前node名称，非空
    "thread":1234,                                 //线程id，非空
    "link":{"src":"/testnode","dst":"/testnode2"}, //tcp连接中node名，可空    
    "recv_stamp":{"sec":123123,"nsec":123123}      //为类型1的扩展字段，接收时间戳
  }
 */


class  OutputTimeJson
{
public:
  std::string strSrcApp;
  std::string strDstApp; 
  std::string strMd5Sum;
  std::string strTopic;
  uint32_t recv_sec; 
  uint32_t recv_nsec;
  pthread_t  luTreadId;
  uint32_t cur_sec;
  uint32_t cur_nsec;
  uint32_t packet_send_sec;
  uint32_t packet_send_nsec;
  uint32_t type;
  string strNodeName;
  int msg_checksum;
  
  
  OutputTimeJson():strSrcApp(),strDstApp(),strMd5Sum(),strTopic(),recv_sec(0),recv_nsec(0),luTreadId(0),cur_sec(0),cur_nsec(0),packet_send_sec(0),packet_send_nsec(0),type(0),strNodeName(),
                    msg_checksum(0)
  {
    
  }
  ~ OutputTimeJson()
  {
    
  }
  int getJsonStr(std::string & strOutJson)
 {
    ros::Time tempTimeTool;
    tempTimeTool.toNSec();
    Json::Value root;
    Json::FastWriter writer;
    root["type"]=Json::Value(this->type);
#if 0 
    root["stamp"]["sec"]=Json::Value(this->cur_sec);
    root["stamp"]["nsec"]=Json::Value(this->cur_nsec);
#endif
    tempTimeTool.sec = this->cur_sec; 
    tempTimeTool.nsec = this->cur_nsec;
    root["stamp"]=Json::Value((Json::UInt64)tempTimeTool.toNSec());
    
#if 0 
    root["header_stamp"]["sec"]=Json::Value(this->packet_send_sec);
    root["header_stamp"]["nsec"]=Json::Value(this->packet_send_nsec);
#endif
    tempTimeTool.sec= this->packet_send_sec; 
    tempTimeTool.nsec= this->packet_send_nsec;
    root["header_stamp"]=Json::Value((Json::UInt64)tempTimeTool.toNSec());
    
    root["topic"]=Json::Value(this->strTopic);
    root["node"]=Json::Value(this->strNodeName);
    root["thread"]=Json::Value((Json::UInt64 )pthread_self());
    root["link"]["src"]= Json::Value(this->strSrcApp); 
    root["link"]["dst"]=Json::Value(this->strDstApp);
#if 0 
    root["recv_stamp"]["sec"]=Json::Value(this->recv_sec);
    root["recv_stamp"]["nsec"]=Json::Value(this->recv_nsec);  
#endif
    tempTimeTool.sec = this->recv_sec; 
    tempTimeTool.nsec = this->recv_nsec ; 
    root["recv_stamp"]=Json::Value((Json::UInt64)tempTimeTool.toNSec());
    root["feature"]=Json::Value(this->msg_checksum );
    strOutJson.assign( writer.write(root));
    return 0 ; 
 }
  int fillUpCurTime()
  {
      ros::Time  tmpCurrentTime = ros::Time::now();
      this->cur_sec =  tmpCurrentTime.sec;
      this->cur_nsec = tmpCurrentTime.nsec;
      return 0;
  }
  int getJsonWithTimeHeader(std::string&  strOutTimeInfo)
  {
      std::string strTempJson = "";
      getJsonStr(strTempJson);
      char szTime[1024] = {0};
      snprintf(szTime,sizeof(szTime),"[ INFO] [%u.%u]: #key-log#",this->cur_sec,this->cur_nsec);
      strOutTimeInfo.assign(szTime);
      strOutTimeInfo.append(strTempJson);
      return 0;
  }

  int checkSubStr(const char* str, const char* substr) {
        int ret = -1;
        do {
            if ((str == NULL) || (substr == NULL)) {
                ret = -2;
                break;
            }
            char *ret_out = strstr((char*)str, (char*)substr);
            if (ret_out == NULL) {
                ret = -1;
                break;
            }
            ret = 0;
        } while (0);
        return ret;
    }
};
#endif