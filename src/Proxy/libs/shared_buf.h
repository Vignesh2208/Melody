
#include "includes.h"

#define INIT_MAGIC 12345

typedef struct __attribute__((packed)) sharedBufferStruct {

	sem_t lock;
	uint32_t flow  : 1;  // direction of information flow. 0: mininet host -> proxy; 1: proxy->mininet host
	uint32_t ack   : 1;  // 1 - information flow acked; 0 - information flow unacked
	uint32_t dirty : 1;  // set if new data is available to read. cleared on ack.
	uint32_t pad   : 5;  // all 0s
	uint32_t isInit  ;   // set if buffer has been initialized
	uint32_t dstID ;	 // ID of dst which can finally consume information
	uint32_t pktLen;
	char pkt[MAXPKTSIZE];


}sharedPacketBuf;


void init();
bool addNewSharedBuffer(char * bufName, bool isProxy);
sharedPacketBuf * getSharedBuffer(char * bufName);
bool pollProxyRead(sharedPacketBuf * buf);
bool pollHostRead(sharedPacketBuf * buf);
int bufRead(char * bufName, char * storeBuf, bool isProxy);
int bufWrite(char * bufName, char * data, int len, bool isProxy, uint32_t dstID);





