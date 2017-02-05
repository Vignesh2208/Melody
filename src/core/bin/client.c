/* 
 * udpclient.c - A simple UDP client
 * usage: udpclient <host> <port>
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <sys/time.h> 
#include "../definitions.h"

#define BUFSIZE 1200

const char *PATH_TO_DATA = PATH_TO_EXPERIMENT_DATA;
const char *EMANE_DIR = EMANE_TIMEKEEPER_DIR;

void flush_buffer(char * buf, int size){
	int i = 0;
	for(i = 0; i < size; i++)
		buf[i] = '\0';

}

/* 
 * error - wrapper for perror
 */
void error(char *msg) {
    perror(msg);
    exit(0);
}

int main(int argc, char **argv) {
    int sockfd, portno, n;
    int serverlen;
    struct sockaddr_in serveraddr;
    struct hostent *server;
    char *hostname;
    char buf[BUFSIZE];
    int pid;
    char command[200];
    long timeout;

    char * dev_name;
    char * src_ip_to_monitor;
    char * dst_ip_to_monitor;
 
    /* check command line arguments */
    if (argc != 8) {
       fprintf(stderr,"usage: %s <hostname> <port> <numMessages> <devname> <src_ip_to_monitor> <dst_ip_to_monitor> <Timeout between messages in microseconds>\n", argv[0]);
       exit(0);
    }
    
   int numMessages = atoi(argv[3]);
    
    hostname = argv[1];
    portno = atoi(argv[2]);
    dev_name = argv[4];
    src_ip_to_monitor = argv[5];
    dst_ip_to_monitor = argv[6];
    timeout = atol(argv[7]);

    fprintf(stdout,"Hostname : %s\n",hostname);
    fprintf(stdout,"Port no : %d\n",portno);
    fprintf(stdout,"Src_IP_to_monitor : %s\n",src_ip_to_monitor);
    fprintf(stdout,"Dst_IP_to_monitor : %s\n",dst_ip_to_monitor);
    fprintf(stdout,"Num Messages : %d\n", numMessages);
    fprintf(stdout,"Timeout : %lu\n",timeout);

    fflush(stdout);

    /* socket: create the socket */
    sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0) 
        error("ERROR opening socket");

    /* gethostbyname: get the server's DNS entry */
    server = gethostbyname(hostname);
    if (server == NULL) {
        fprintf(stderr,"ERROR, no such host as %s\n", hostname);
        exit(0);
    }

    /*pid = fork();
    if (pid == 0) { //in child
		
		    sprintf(command, "echo Starting... > %s/client_log.txt", PATH_TO_EXPERIMENT_DATA);
		    system(command);
 
		    sprintf(command, "%s/lxc-command/pcap_packet_sniffer %s %s %s >> %s/client_log.txt 2>&1", EMANE_DIR, dev_name, src_ip_to_monitor, dst_ip_to_monitor,PATH_TO_EXPERIMENT_DATA);
		    system(command);
		    return 0;
     }*/

    /* build the server's Internet address */
    bzero((char *) &serveraddr, sizeof(serveraddr));
    serveraddr.sin_family = AF_INET;
    bcopy((char *)server->h_addr, 
	  (char *)&serveraddr.sin_addr.s_addr, server->h_length);
    serveraddr.sin_port = htons(portno);

    /* get a message from the user */
    
    int cc = 0;
		
   

	//For debugging SocketHook
    	//FILE *fp;
	// Enter your fav path here.
	//fp = fopen("<path>/client.txt","a");

	printf("Process PID = %d\n",getpid());
	fflush(stdout);
   
	int j  = 0;
	int k = 0;
	for (cc = 0; cc < numMessages; cc++)
	{
		
		bzero(buf, BUFSIZE);

		/* send the message to the server */

		// For debugging SocketHook		
		struct timeval sendTimeStamp,JAS_Timestamp;
		gettimeofday(&sendTimeStamp, NULL);
		
		long sendTS = sendTimeStamp.tv_sec * 1000000 + sendTimeStamp.tv_usec;

		sprintf(buf,"%lu,%lu",sendTimeStamp.tv_sec,sendTimeStamp.tv_usec);

		serverlen = sizeof(serveraddr);
		n = sendto(sockfd, buf, BUFSIZE, 0, &serveraddr, serverlen);
		
		fprintf(stdout,"Sent ping message no : %d\n", cc);
		fflush(stdout);
		usleep(500000);
		//for(k=0; k < 100000000; k++);


		//for(k = 0; k < 100000000; k++);
		flush_buffer(buf,BUFSIZE);

		if (n < 0){ 
			// fOR DEBUGGING SOCKEThOOK
			//fclose(fp);
		  error("ERROR in sendto");
		}
		
		
		/* print the server's reply */
		
	
	}

	//For debugging SocketHook
	//fclose(fp);
	return 0;
}
