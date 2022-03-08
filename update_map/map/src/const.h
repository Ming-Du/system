#ifndef CONST_H_
#define CONST_H_

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <string.h>
#include <string>

#define HEADER_SIZE 8
#define MAX_BODY_SIZE 1024*4-8



typedef char    int8;
typedef short   int16;
typedef int     int32;
//typedef long int  int64;

typedef unsigned char   uint8;
typedef unsigned short    uint16;
typedef unsigned int    uint32;
//typedef unsigned long long  uint64;

typedef int8  TCHAR;
typedef uint8 BYTE;
typedef uint16  WORD;
typedef uint32  DWORD;
//typedef uint64  DDWORD;

//typedef int16 BOOL;
static int CreateDir(const char *sPathName)
{
	std::string mkdir_cmd = "mkdir -p ";
	mkdir_cmd += sPathName;
	system(mkdir_cmd.data());
}



#endif
