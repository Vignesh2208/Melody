#ifndef __INCLUDES_H
#define __INCLUDES_H

#include <Python.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <semaphore.h>
#include <fcntl.h>
#include <sys/uio.h>
#include <sys/shm.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#include <pthread.h>
#include <assert.h>
#include <sys/socket.h>
#include <sys/mman.h>
#include "utils/hashmap.h"
#include "utils/linkedlist.h"


#define MAXPKTSIZE 10000 // bytes
#define MAX_BUF_NAME_LEN 100

typedef int int32_t;
typedef unsigned int uint32_t;

typedef short int16_t;
typedef unsigned short uint16_t;


typedef unsigned char uint8_t;
typedef int bool;

#define PROXY_NODE_ID 0
#define SUCCESS 1
#define FAILURE 0
#define TRUE 1
#define FALSE 0
#define IS_SHARED 1
#define LOCKED 0
#define UNLOCKED 1
#define PROXY_TO_HOST 1
#define HOST_TO_PROXY 0
#define BUF_NOT_INITIALIZED -1
#define TEMP_ERROR -2 

#endif