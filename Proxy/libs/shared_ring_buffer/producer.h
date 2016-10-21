#ifndef __PRODUCER_H
#define __PRODUCER_H

#include "ring_buffer.h"
#include <pcap/pcap.h>
#include <arpa/inet.h>
#include <netinet/if_ether.h>
#include <sys/socket.h>
#include <sys/mman.h>
#include <net/ethernet.h>
#include <netinet/ip_icmp.h>   //Provides declarations for icmp header
#include <netinet/udp.h>   //Provides declarations for udp header
#include <netinet/tcp.h>   //Provides declarations for tcp header
#include <netinet/ip.h>    //Provides declarations for ip header



ringBufS * buffer_ptr;
char *dev_name;
char dev_ip_address[100];
char errbuf[PCAP_ERRBUF_SIZE];
struct sockaddr_in source,dest;
char src_ip[100];
char dst_ip[100];




#ifdef  __cplusplus
      extern  "C" {
#endif

void my_callback(const struct pcap_pkthdr* pkthdr,const u_char*  packet);
pcap_t* producer_init();
int run(pcap_t *descr);


#ifdef  __cplusplus
      }
#endif
#endif

