/* 
 * udpserver.c - A simple UDP echo server 
 * usage: udpserver <port>
 */

#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <netdb.h>
#include <sys/types.h> 
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include "../definitions.h"

#define BUFSIZE 1200

const char *PATH_TO_DATA = PATH_TO_EXPERIMENT_DATA;
const char *EMANE_DIR = EMANE_TIMEKEEPER_DIR;


/*
 * error - wrapper for perror
 */
void error(char *msg) {
  perror(msg);
  exit(1);
}

int main(int argc, char **argv) {
  int sockfd; /* socket */
  int portno; /* port to listen on */
  int clientlen; /* byte size of client's address */
  struct sockaddr_in serveraddr; /* server's addr */
  struct sockaddr_in clientaddr; /* client addr */
  struct hostent *hostp; /* client host info */
  char buf[BUFSIZE]; /* message buf */
  char *hostaddrp; /* dotted decimal host addr string */
  int optval; /* flag value for setsockopt */
  int n; /* message byte size */
  int numExpectedPings;
  int pid;
  char command[200];
  double avg_transmit_time = 0.0;
  double std_dev_transmit_time = 0.0;
  char * dev_name;
  char * src_ip_to_monitor;
  char * dst_ip_to_monitor;
  
  /* 
   * check command line arguments 
   */
  if (argc != 6) {
    fprintf(stderr, "usage: %s <port> <numPings> <devname> <src_ip_to_monitor> <dst_ip_to_monitor>\n", argv[0]);
    exit(1);
  }
  
  numExpectedPings = atoi(argv[2]);
  
  portno = atoi(argv[1]);

  dev_name = argv[3];
  src_ip_to_monitor = argv[4];
  dst_ip_to_monitor = argv[5];

 	

  /* 
   * socket: create the parent socket 
   */
  sockfd = socket(AF_INET, SOCK_DGRAM, 0);
  if (sockfd < 0) 
    error("ERROR opening socket");


  pid = fork();
	if (pid == 0) { //in child
		    
		    sprintf(command, "echo Starting... > %s/server_log.txt", PATH_TO_EXPERIMENT_DATA);
		    system(command);
		    
		    sprintf(command, "%s/lxc-command/pcap_packet_sniffer %s %s %s >> %s/server_log.txt 2>&1", EMANE_DIR, dev_name, src_ip_to_monitor, dst_ip_to_monitor, PATH_TO_EXPERIMENT_DATA);
		    system(command);
		    return 0;
     }
  /* setsockopt: Handy debugging trick that lets 
   * us rerun the server immediately after we kill it; 
   * otherwise we have to wait about 20 secs. 
   * Eliminates "ERROR on binding: Address already in use" error. 
   */
  optval = 1;
  setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, 
	     (const void *)&optval , sizeof(int));

  /*
   * build the server's Internet address
   */
  bzero((char *) &serveraddr, sizeof(serveraddr));
  serveraddr.sin_family = AF_INET;
  serveraddr.sin_addr.s_addr = htonl(INADDR_ANY);
  serveraddr.sin_port = htons((unsigned short)portno);

  /* 
   * bind: associate the parent socket with a port 
   */
  if (bind(sockfd, (struct sockaddr *) &serveraddr, 
	   sizeof(serveraddr)) < 0) 
    error("ERROR on binding");

  /* 
   * main loop: wait for a datagram, then echo it
   */
  int numReceived = 0;
  clientlen = sizeof(clientaddr);
  struct timeval startTimeStamp;
  gettimeofday(&startTimeStamp, NULL);
	
  long StartTS = startTimeStamp.tv_sec * 1000000 + startTimeStamp.tv_usec;
  double avg_throughput = 0.0;
  while (1) {

    /*
     * recvfrom: receive a UDP datagram from a client
     */
    bzero(buf, BUFSIZE);
    fflush(stdout);

    n = recvfrom(sockfd, buf, BUFSIZE, 0,
		 (struct sockaddr *) &clientaddr, &clientlen);
    if (n < 0)
      error("ERROR in recvfrom");
	

	numReceived++;
	fprintf(stdout,"Server received datagram : %s\n", buf);
	struct timeval RecvTimeStamp;
	gettimeofday(&RecvTimeStamp, NULL);
		
	char * ptr;
	long RecvTS = RecvTimeStamp.tv_sec * 1000000 + RecvTimeStamp.tv_usec;
	int i = 0;
	while(buf[i] != ',')
		i++;
	buf[i] = '\0';
	long SendTS_sec =  atol(buf);
	long SendTS_usec = atol(buf + i + 1);
	long SendTS = SendTS_sec* 1000000 + SendTS_usec;

	if(RecvTS < SendTS){
		numReceived --; // ignore
		continue;
	}
	else{
	double transit_time = (float)(RecvTS - SendTS)/(float)1000000; 
	avg_transmit_time += transit_time;
	std_dev_transmit_time += transit_time*transit_time;
	avg_throughput += ((float)numReceived/(float)(RecvTS - StartTS))*1000000.0;
	}

	

    /* 
     * gethostbyaddr: determine who sent the datagram
     */
    //hostp = gethostbyaddr((const char *)&clientaddr.sin_addr.s_addr, 
	//		  sizeof(clientaddr.sin_addr.s_addr), AF_INET);
    //if (hostp == NULL)
    //  error("ERROR on gethostbyaddr");
    hostaddrp = inet_ntoa(clientaddr.sin_addr);
    if (hostaddrp == NULL)
      error("ERROR on inet_ntoa\n");
    fprintf(stdout,"server received datagram no %d from (%s)\n", numReceived,hostaddrp);
   
    fprintf(stdout,"RecvTime : %lu\n",RecvTS);
    fprintf(stdout,"SendTime : %lu\n",SendTS);
    fprintf(stdout,"Transmit time : %lu\n", RecvTS - SendTS);
    fprintf(stdout,"Avg Transmit time (sec) : %f\n", avg_transmit_time/numReceived);
    fprintf(stdout,"Std Dev Transmit time (sec) : %f\n", sqrt(std_dev_transmit_time/numReceived - ((avg_transmit_time/numReceived)*(avg_transmit_time/numReceived))));
    fprintf(stdout,"Avg throughput : %f\n", avg_throughput/numReceived);
    fprintf(stdout,"#####################################################\n"); 
    /* 
     * sendto: echo the input back to the client 
     */
    n = sendto(sockfd, buf, strlen(buf), 0, 
	       (struct sockaddr *) &clientaddr, clientlen);
    if (n < 0) 
      error("ERROR in sendto");
      
    if (numExpectedPings == numReceived)
		break;  
  }
}
