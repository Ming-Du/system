/*
 * Copyright (C) 2009, Willow Garage, Inc.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *   * Redistributions of source code must retain the above copyright notice,
 *     this list of conditions and the following disclaimer.
 *   * Redistributions in binary form must reproduce the above copyright
 *     notice, this list of conditions and the following disclaimer in the
 *     documentation and/or other materials provided with the distribution.
 *   * Neither the names of Willow Garage, Inc. nor the names of its
 *     contributors may be used to endorse or promote products derived from
 *     this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 */


#include "ros/message_deserializer.h"
#include "ros/subscription_callback_helper.h"
#include <ros/console.h>
#include "ros/easylogging++.h"
#include "ros/OutputTimeJson.hpp"
#include "../../include/ros/CrcUtils.hpp"
#include "ros/this_node.h"

namespace ros
{

MessageDeserializer::MessageDeserializer(const SubscriptionCallbackHelperPtr& helper, const SerializedMessage& m, const boost::shared_ptr<M_string>& connection_header)
: helper_(helper)
, serialized_message_(m)
, connection_header_(connection_header)
{
  if (serialized_message_.message && *serialized_message_.type_info != helper->getTypeInfo())
  {
    serialized_message_.message.reset();
  }
}

VoidConstPtr MessageDeserializer::deserialize()
{
  boost::mutex::scoped_lock lock(mutex_);

  if (msg_)
  {
    return msg_;
  }

  if (serialized_message_.message)
  {
    msg_ = serialized_message_.message;
    return msg_;
  }

  if (!serialized_message_.buf && serialized_message_.num_bytes > 0)
  {
    // If the buffer has been reset it means we tried to deserialize and failed
    return VoidConstPtr();
  }

  try
  {
    SubscriptionCallbackHelperDeserializeParams params;
    params.buffer = serialized_message_.message_start;
    params.length = serialized_message_.num_bytes - (serialized_message_.message_start - serialized_message_.buf.get());
    params.connection_header = connection_header_;
    // 实质上还是通过helper做的反序列化
    msg_ = helper_->deserialize(params);
  }
  catch (std::exception& e)
  {
    ROS_ERROR("Exception thrown when deserializing message of length [%d] from [%s]: %s", (uint32_t)serialized_message_.num_bytes, (*connection_header_)["callerid"].c_str(), e.what());
  }
  
#if 0 
  //add get msg feature
  unsigned char szSec[4] = {0};
    unsigned char szUsec[4] = {0};
    memcpy(szSec,msg_.get()+4,4);
    memcpy(szUsec,msg_.get()+8,4);


    
    unsigned  int temp_sec =(*(unsigned int*)szSec); 
    unsigned  int temp_usec = (*(unsigned int*)szUsec);
    string strLogContent = "";
    // MOGO 考虑在这里对spin callback打日志
    OutputTimeJson outLogObject;
    outLogObject.strDstApp.assign(ros::this_node::getName());
    if ( (*connection_header_).count("callerid") > 0 )
    {
      outLogObject.strSrcApp.assign( (*connection_header_)["callerid"]);
    }
    if( (*connection_header_).count("md5sum") > 0 )
    {
      outLogObject.strMd5Sum.assign((*connection_header_)["md5sum"]);
    }
    if( (*connection_header_).count("topic") > 0  ) 
    {
      outLogObject.strTopic.assign((*connection_header_)["topic"]);
    }
#if 0 
    outLogObject.recv_sec  = i.receipt_time.sec ; 
    outLogObject.recv_nsec = i.receipt_time.nsec ;
#endif
    int checksum = 0 ;
    CrcUtils::cacuCrc16(serialized_message_.buf.get(),serialized_message_.num_bytes,checksum);
            
    outLogObject.packet_send_sec =  temp_sec; 
    outLogObject.packet_send_nsec = temp_usec; 
    outLogObject.strNodeName=ros::this_node::getName();
    outLogObject.fillUpCurTime();
    outLogObject.type = 1;
    outLogObject.msg_checksum = checksum  ; 
    outLogObject.getJsonWithTimeHeader(strLogContent);
    LOG(INFO) <<  strLogContent; 
#endif

  serialized_message_.buf.reset();

  return msg_;
}

}
