#pragma once

#include "../proto/header.pb.h"

namespace common {

inline double TimeToSecond(const Time& t)
{
    //refer to ros::Time::toSec
    return static_cast<double>(t.sec()) + 1e-9*static_cast<double>(t.nsec());
}

}