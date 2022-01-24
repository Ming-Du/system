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


#include <ros/this_node.h>
#include <std_msgs/Header.h>

#include "ros/subscription_queue.h"
//#include "ros/message_deserializer.h"
#include "../../../roscpp/include/ros/message_deserializer.h"
#include "ros/subscription_callback_helper.h"
#include "ros/easylogging++.h"
#include "ros/OutputTimeJson.hpp"
#include "../../../roscpp/include/ros/CrcUtils.hpp"

namespace ros
{

SubscriptionQueue::SubscriptionQueue(const std::string& topic, int32_t queue_size, bool allow_concurrent_callbacks)
: topic_(topic)
, size_(queue_size)
, full_(false)
, queue_size_(0)
, allow_concurrent_callbacks_(allow_concurrent_callbacks)
{}

SubscriptionQueue::~SubscriptionQueue()
{

}

void SubscriptionQueue::push(const SubscriptionCallbackHelperPtr& helper, const MessageDeserializerPtr& deserializer,
                                 bool has_tracked_object, const VoidConstWPtr& tracked_object, bool nonconst_need_copy,
                                 ros::Time receipt_time, bool* was_full)
{
  boost::mutex::scoped_lock lock(queue_mutex_);

  if (was_full)
  {
    *was_full = false;
  }

  if(fullNoLock())
  {
    queue_.pop_front();
    --queue_size_;

    if (!full_)
    {
      ROS_DEBUG("Incoming queue was full for topic \"%s\". Discarded oldest message (current queue size [%d])", topic_.c_str(), (int)queue_.size());
    }

    full_ = true;

    if (was_full)
    {
      *was_full = true;
    }
  }
  else
  {
    full_ = false;
  }

  Item i;
  i.helper = helper;
  i.deserializer = deserializer;
  i.has_tracked_object = has_tracked_object;
  i.tracked_object = tracked_object;
  i.nonconst_need_copy = nonconst_need_copy;
  i.receipt_time = receipt_time;
  queue_.push_back(i);
  ++queue_size_;
}

void SubscriptionQueue::clear()
{
  boost::recursive_mutex::scoped_lock cb_lock(callback_mutex_);
  boost::mutex::scoped_lock queue_lock(queue_mutex_);

  queue_.clear();
  queue_size_ = 0;
}

CallbackInterface::CallResult SubscriptionQueue::call()
{
  // The callback may result in our own destruction.  Therefore, we may need to keep a reference to ourselves
  // that outlasts the scoped_try_lock
  boost::shared_ptr<SubscriptionQueue> self;
  boost::recursive_mutex::scoped_try_lock lock(callback_mutex_, boost::defer_lock);

  if (!allow_concurrent_callbacks_)
  {
    lock.try_lock();
    if (!lock.owns_lock())
    {
      return CallbackInterface::TryAgain;
    }
  }

  VoidConstPtr tracker;
  Item i;

  {
    boost::mutex::scoped_lock lock(queue_mutex_);

    if (queue_.empty())
    {
      return CallbackInterface::Invalid;
    }

    // queue_里的内容，是在Subscription::handleMessage的流程里push进去的
    i = queue_.front();

    if (queue_.empty())
    {
      return CallbackInterface::Invalid;
    }

    if (i.has_tracked_object)
    {
      tracker = i.tracked_object.lock();

      if (!tracker)
      {
        return CallbackInterface::Invalid;
      }
    }

    queue_.pop_front();
    --queue_size_;
  }

  // 解码消息，这个deserializer是在Subscription::handleMessage里构造，调SubscriptionQueue::push的时候传进来的
  // 实际上是MessageDeserializer类，这个类就是中间封装了一层，最终还是调helper->deserialize
  SerializedMessage ptrRawMsg = i.deserializer->getRawMes();
  VoidConstPtr msg = i.deserializer->deserialize();

  // msg can be null here if deserialization failed
  if (msg)
  {
    try
    {
      self = shared_from_this();
    }
    catch (boost::bad_weak_ptr&) // For the tests, where we don't create a shared_ptr
    {}

    SubscriptionCallbackHelperCallParams params;
    // msg 原始数据
    // getConnectionHeader 从connection类获得的请求头
    // receipt_time SubscriptionQueue::push的时间
    
    params.event = MessageEvent<void const>(msg, i.deserializer->getConnectionHeader(), i.receipt_time, i.nonconst_need_copy, MessageEvent<void const>::CreateFunction());

#if 0 
    unsigned char szSec[4] = {0};
    unsigned char szUsec[4] = {0};
    memcpy(szSec,msg.get()+4,4);
    memcpy(szUsec,msg.get()+8,4);
#endif
#if 0
    printf("parse sec = sec:%u\n",(*(unsigned int*)szSec));
    printf("parse usec = usec:%u\n",(*(unsigned int*)szUsec));
#endif
#if 1
    std_msgs::Header *h = NULL;
    unsigned  int temp_sec = 0;
    unsigned  int temp_usec = 0;
    if (i.helper->hasHeader())
    {
        //std_msgs::Header* h = reinterpret_cast<std_msgs::Header*>(const_cast<void*>(msg.get()));
        h = (std_msgs::Header *)(msg.get());
        temp_sec  = h->stamp.sec;
        temp_usec  = h->stamp.nsec;        
    }
    
    int checksum = 0;
    if(!(i.helper->hasHeader()))
    {
      CrcUtils::cacuCrc16((const void*)((ptrRawMsg.buf.get()+0)),ptrRawMsg.num_bytes,checksum);
    }
    
    string strLogContent = "";
    // MOGO 考虑在这里对spin callback打日志
    OutputTimeJson outLogObject;
    outLogObject.strDstApp.assign(ros::this_node::getName());
    if ( (*((i.deserializer)->getConnectionHeader())).count("callerid") > 0 )
    {
      outLogObject.strSrcApp.assign((*((i.deserializer)->getConnectionHeader()))["callerid"]);
    }
    if( ( (*((i.deserializer)->getConnectionHeader())).count("md5sum") > 0 )   )
    {
      outLogObject.strMd5Sum.assign((*((i.deserializer)->getConnectionHeader()))["md5sum"]);
    }
    if(( (*((i.deserializer)->getConnectionHeader())).count("topic") > 0 ) )
    {
      outLogObject.strTopic.assign((*((i.deserializer)->getConnectionHeader()))["topic"]);
    }
    outLogObject.recv_sec  = i.receipt_time.sec ; 
    outLogObject.recv_nsec = i.receipt_time.nsec ;
    outLogObject.packet_send_sec =  temp_sec; 
    outLogObject.packet_send_nsec = temp_usec; 
    outLogObject.strNodeName=ros::this_node::getName();
    outLogObject.fillUpCurTime();
    outLogObject.type = 1;
    outLogObject.msg_checksum = checksum;
    //printf("dst checksum:%d\n",checksum);
    do
        {
          if ( (outLogObject.strSrcApp == "/rosout") || ( outLogObject.strDstApp == "/rosout")  )
          {
            break;
          }
          if ( ( outLogObject.checkSubStr(outLogObject.strDstApp.c_str(),"/rostopic")==0) && ( outLogObject.checkSubStr(outLogObject.strSrcApp.c_str(),"/rostopic") == 0) )
          {           
            break;
          }
          outLogObject.getJsonWithTimeHeader(strLogContent);
          LOG(INFO) << strLogContent;
        } while (0);
#endif
    
    
    // 在subscribe最开始就创建了的helper，这个类记录了真正的回调函数
    i.helper->call(params);
  }

  return CallbackInterface::Success;
}

bool SubscriptionQueue::ready()
{
  if (allow_concurrent_callbacks_)
  {
    return true;
  }
  boost::recursive_mutex::scoped_try_lock lock(callback_mutex_, boost::try_to_lock);
  return lock.owns_lock();
}

bool SubscriptionQueue::full()
{
  boost::mutex::scoped_lock lock(queue_mutex_);
  return fullNoLock();
}

bool SubscriptionQueue::fullNoLock()
{
  return (size_ > 0) && (queue_size_ >= (uint32_t)size_);
}

}

