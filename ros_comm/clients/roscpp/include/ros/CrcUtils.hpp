/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

/* 
 * File:   check_data.hpp
 * Author: user
 *
 * Created on 2022年1月19日, 上午11:35
 */

#ifndef CHECK_DATA_HPP
#define CHECK_DATA_HPP

#include <boost/crc.hpp>
#include <iostream>
using namespace boost;
using namespace std;

class CrcUtils
{
public:
    static int cacuCrc16(const void* buffer, size_t byte_count, int &  checksum) {
        crc_optimal<16, 0x8005, 0, 0, true, true> crc16;
        crc16.process_bytes(buffer,byte_count);
        checksum=crc16.checksum();
        return 0;
    }
};












#endif /* CHECK_DATA_HPP */

