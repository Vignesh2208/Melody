 #ifndef __RINGBUFS_H
    
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

    #define __RINGBUFS_H
    #define RBUF_SIZE 1


    typedef struct timestamp_entry{
	
	long secs;
	long u_secs;
	long n_secs;
	int is_read;
	long pkt_hash_code;
	


    } timestamp;

    typedef struct  ringBufS
    {
      timestamp buf[RBUF_SIZE];
      int head;
      int tail;
      int count;
      sem_t full;
      sem_t empty;
      sem_t mutex;
      sem_t stop;
    } ringBufS;

    #ifdef  __cplusplus
      extern  "C" {
    #endif
      void  init  (ringBufS *_this);
      int   is_empty (ringBufS *_this);
      int   is_full  (ringBufS *_this);
      timestamp*   get   (ringBufS *_this);
      timestamp*   get_w_hash   (ringBufS *_this, long hash_code);
      void  put   (ringBufS *_this, timestamp* c);
      void  flush (ringBufS *_this, const int clearBuffer);
    #ifdef  __cplusplus
      }
    #endif
#endif
