
#include <pcap/pcap.h>
#include <arpa/inet.h>
#include <netinet/if_ether.h>
#include <sys/socket.h>
#include <sys/mman.h>
#include <net/ethernet.h>
#include <netinet/ip_icmp.h>	//Provides declarations for icmp header
#include <netinet/udp.h>   	//Provides declarations for udp header
#include <netinet/tcp.h>   	//Provides declarations for tcp header
#include <netinet/ip.h>    	//Provides declarations for ip header
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <sys/uio.h>
#include <sys/shm.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#include <pthread.h>
#include <math.h>
#include <signal.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/syscall.h>
#include <sys/mount.h>
#include <sys/utsname.h>
#include <linux/sched.h>
#include <time.h>
#include <sys/time.h>
#include "../dilation-code/scripts/TimeKeeper_functions.h"
#include <sys/stat.h>
#include <sys/poll.h>


#define IP 1
#define NOT_IP 2
#define NOT_SUPPORTED -1
#define TRUE 1
#define FALSE 0


static char * dev_name;
static n_required_packets_processed = 0;
char dev_ip_address[100];
char errbuf[PCAP_ERRBUF_SIZE];
struct sockaddr_in source,dest;
char src_ip[100];
char dst_ip[100];
static char * src_ip_to_monitor;
static char * dst_ip_to_monitor;
static float sum_TTL = 0.0;
static float sumsquare_TTL = 0.0;
static float avg_TTL = 0.0;
static float stddev_TTL = 0.0;

struct timeval tv;


static unsigned short compute_checksum(unsigned short *addr, unsigned int count) {

	  register unsigned long sum = 0;
	  while (count > 1) {
		sum += * addr++;
	        count -= 2;
	  }

	  //if any bytes left, pad the bytes and add
	  if(count > 0) {
	    sum += ((*addr)&htons(0xFF00));
	  }

	  //Fold sum to 16 bits: add carrier to result
	  while (sum>>16) {
	      sum = (sum & 0xffff) + (sum >> 16);
	  }

	  //one's complement
	  sum = ~sum;

	  return ((unsigned short)sum);

}

/* set ip checksum of a given ip header*/

void compute_ip_checksum(struct iphdr* iphdrp){

  	iphdrp->check = 0;
	iphdrp->check = compute_checksum((unsigned short*)iphdrp, iphdrp->ihl<<2);

}

/* Compute checksum for count bytes starting at addr, using one's complement of one's complement sum*/
/* set tcp checksum: given IP header and tcp segment */

void compute_tcp_checksum(struct iphdr *pIph, unsigned short *ipPayload, FILE* fp) {

	register unsigned long sum = 0;
	unsigned short tcpLen = ntohs(pIph->tot_len) - (pIph->ihl<<2);
	struct tcphdr *tcphdrp = (struct tcphdr*)(ipPayload);

	//add the pseudo header 
	//the source ip
	sum += (pIph->saddr>>16)&0xFFFF;
	sum += (pIph->saddr)&0xFFFF;
	//the dest ip
	sum += (pIph->daddr>>16)&0xFFFF;
	sum += (pIph->daddr)&0xFFFF;
	//protocol and reserved: 6
	sum += htons(IPPROTO_TCP);
	//the length
	sum += htons(tcpLen);

	//add the IP payload
	//initialize checksum to 0

	tcphdrp->check = 0;

	while (tcpLen > 1) {
	        sum += * ipPayload++;
	        tcpLen -= 2;
	}

	//if any bytes left, pad the bytes and add
	if(tcpLen > 0) {
        //printf("+++++++++++padding, %d\n", tcpLen);
	       sum += ((*ipPayload)&htons(0xFF00));
        }

    	//Fold 32-bit sum to 16 bits: add carrier to result

	while (sum>>16) {
          sum = (sum & 0xffff) + (sum >> 16);
	}
	
        sum = ~sum;

	//set computation result

	tcphdrp->check = (unsigned short)sum;

}

/* set tcp checksum: given IP header and UDP datagram */

void compute_udp_checksum(struct iphdr *pIph, unsigned short *ipPayload,FILE* fp) {

    register unsigned long sum = 0;
    struct udphdr *udphdrp = (struct udphdr*)(ipPayload);
    unsigned short udpLen = htons(udphdrp->len);
    fprintf(fp,"Udp len = %d\n",udpLen);



    //add the pseudo header 
    //the source ip
    sum += (pIph->saddr>>16)&0xFFFF;
    sum += (pIph->saddr)&0xFFFF;

    //the dest ip
    sum += (pIph->daddr>>16)&0xFFFF;
    sum += (pIph->daddr)&0xFFFF;

    //protocol and reserved: 17
    sum += htons(IPPROTO_UDP);

    //the length
    sum += udphdrp->len; 

    //add the IP payload
    //initialize checksum to 0

    udphdrp->check = 0;
    while (udpLen > 1) {
        sum += * ipPayload++;
        udpLen -= 2;
    }

    //if any bytes left, pad the bytes and add

    if(udpLen > 0) {
        sum += ((*ipPayload)&htons(0xFF00));
    }

    while (sum>>16) {
         sum = (sum & 0xffff) + (sum >> 16);
    }
    sum = ~sum;
    fprintf(fp,"UDF Checksum = %d\n",(unsigned short)sum);

    //set computation result
    udphdrp->check = ((unsigned short)sum == 0x0000)?0xFFFF:(unsigned short)sum;

}


void print_packet(u_char * s,int size,FILE * fp){

    const u_char * ptr = s;
    int i = 0;
    fprintf(fp,"Packet :");
    for(i = 0; i < size; i++)
    {
    	fprintf(fp,"%02x",*ptr);
	++ptr;
    }
    fprintf(fp,"\n");

}
int packet_hash(u_char * s,int size)
{

    //http://stackoverflow.com/questions/114085/fast-string-hashing-algorithm-with-low-collision-rates-with-32-bit-integer
    int hash = 0;
    u_char * ptr = s;
    int i = 0;
    
    for(i = 0; i < size; i++)
    {
    	hash += *ptr;
    	hash += (hash << 10);
    	hash ^= (hash >> 6);

        ++ptr;
    }

    hash += (hash << 3);
    hash ^= (hash >> 11);
    hash += (hash << 15);


    return hash;
}

int get_ip_addresses(const u_char * Buffer, int Size)
{
    
    unsigned short iphdrlen;
         
    struct iphdr *iph; 
    struct ether_header * eptr = (struct ether_header *) Buffer;
    u_short ether_type    = ntohs(eptr->ether_type);
    int dstIPAddr_offset = 0;
    int srcIPAddr_offset = 0;
    int ether_offset = 0;
    u_char* ptrToIPAddr;
    unsigned int dstIP;
    int is_IP = 0;

    u_char* ptrToSrcIPAddr;
    unsigned int srcIP;
    int is_ARP = 0;


    switch(ether_type){

	case ETHERTYPE_IP : 	ether_offset = 14;
				dstIPAddr_offset = 16;
				srcIPAddr_offset = 12;
				is_IP = 1;
				break;
	case ETHERTYPE_ARP :	is_ARP = 1;
				//printf("ETHER ARP\n");
				ether_offset = 14;
				dstIPAddr_offset = 24;
				srcIPAddr_offset = 14;
				break;

	case ETHERTYPE_REVARP :	//printf("ETHER REVARP\n");

				ether_offset = 14;
				dstIPAddr_offset = 24;
				srcIPAddr_offset = 14;
				
				break;
	case ETHERTYPE_IPV6:	return NOT_SUPPORTED;
				break;
	
	default :		
				return NOT_SUPPORTED;
				break;


    }

	

    ptrToIPAddr = (u_char*)(Buffer + ether_offset + dstIPAddr_offset);
    dstIP = *(unsigned int*)(ptrToIPAddr);

    ptrToSrcIPAddr = (u_char*)(Buffer + ether_offset + srcIPAddr_offset);
    srcIP = *(unsigned int*)(ptrToSrcIPAddr);
       
    memset(src_ip,0,sizeof(src_ip));
    memset(dst_ip,0,sizeof(dst_ip));

    inet_ntop(AF_INET, &dstIP,dst_ip,sizeof(dst_ip));
    inet_ntop(AF_INET, &srcIP,src_ip,sizeof(src_ip));

    if(is_ARP){
	if(strcmp(src_ip,dev_ip_address) == 0){
		printf("Sent ARP request for dst IP : %s\n",dst_ip);
	}
	else if(strcmp(dst_ip,dev_ip_address) == 0){
		printf("Received ARP request from Src IP : %s\n",src_ip);
	}
    }

    if(is_IP){
	return IP;
    }
	
    return NOT_IP;

}

void PrintData(int startOctet, int endOctet, const u_char *data)
{
    int i = 0;
    for (i = startOctet; i <= endOctet; i++)
    {
        // Print each octet as hex (x), make sure there is always two characters (.2).
        printf("%.2x ", data[i]);
    }
    printf("\n");
}


/* callback function that is passed to pcap_loop(..) and called each time 
 * a packet is recieved                                                    */
void my_callback(const struct pcap_pkthdr* pkthdr,const u_char*  packet,FILE* fp)
{
    
    int size = pkthdr->len;
    int result;
    unsigned short *payload;
    u_char * packet_copy;
    struct iphdr *iph; 
    struct udphdr *udphdrp;
    int ether_offset = 14;
    int should_buffer = TRUE;
    u_short udp_src_port;    
    result = get_ip_addresses(packet,size);

    struct timeval now;
    struct timeval later;
    struct timeval now1;
    struct timeval later1;
    struct tm localtm;
    struct tm origtm;

    if(strcmp(dst_ip,"10.100.255.255") == 0 && strcmp(src_ip,dev_ip_address) != 0){ // Note time of arrival of routing updates from other nodes

	gettimeofday(&now, NULL);
	gettimeofdayoriginal(&now1, NULL);
        gettimeofday(&later, NULL);
        gettimeofdayoriginal(&later1, NULL);
	localtime_r(&(later.tv_sec), &localtm);
	localtime_r(&(later1.tv_sec),&origtm);
	//fprintf(fp,"Arrival from %s, localtime: %d:%02d:%02d %ld, orig_time : %d:%02d:%02d %ld\n", src_ip, localtm.tm_hour, localtm.tm_min, localtm.tm_sec, later.tv_usec, origtm.tm_hour, origtm.tm_min, origtm.tm_sec, later1.tv_usec);
	

    }

    if(strcmp(dst_ip,"10.100.255.255") == 0 && strcmp(src_ip,dev_ip_address) == 0){ // Note time of arrival of routing updates from other nodes

	gettimeofday(&now, NULL);
	gettimeofdayoriginal(&now1, NULL);
        gettimeofday(&later, NULL);
        gettimeofdayoriginal(&later1, NULL);
	localtime_r(&(later.tv_sec), &localtm);
	localtime_r(&(later1.tv_sec),&origtm);
	//fprintf(fp,"Send from %s at, localtime: %d:%02d:%02d %ld, orig_time : %d:%02d:%02d %ld\n", src_ip, localtm.tm_hour, localtm.tm_min, localtm.tm_sec, later.tv_usec, origtm.tm_hour, origtm.tm_min, origtm.tm_sec, later1.tv_usec);
	

    }

    
    if((strcmp(dst_ip,dst_ip_to_monitor) == 0) && (strcmp(src_ip,src_ip_to_monitor) == 0)){ // Consider only monitored packets

		if(result == IP){
			struct ether_header * eptr = (struct ether_header *) packet;
			
	    		fprintf(fp,"MAC src: ");
			PrintData(0,5,eptr->ether_shost);
	
		    	fprintf(fp,"MAC dest: ");
			PrintData(0,5,eptr->ether_dhost);
			
		}

    switch(result){

	case NOT_SUPPORTED : 	
				return;				
				break;
	case NOT_IP :
				break;

	case IP :		
				packet_copy = (u_char *) packet;
				iph = (struct iphdr *)(packet_copy  + sizeof(struct ethhdr) );
				payload = (unsigned short*) (packet_copy + ether_offset + 20);
				fprintf(fp,"########################################################\n");

				gettimeofday(&now, NULL);
				gettimeofdayoriginal(&now1, NULL);
        			gettimeofday(&later, NULL);
        			gettimeofdayoriginal(&later1, NULL);
				localtime_r(&(later.tv_sec), &localtm);
				localtime_r(&(later1.tv_sec),&origtm);
				fprintf(fp,"Received at, localtime: %d:%02d:%02d %ld, orig_time : %d:%02d:%02d %ld\n", localtm.tm_hour, localtm.tm_min, localtm.tm_sec, later.tv_usec, origtm.tm_hour, origtm.tm_min, origtm.tm_sec, later1.tv_usec);
				fprintf(fp,"IP packet TTL = %d\n",(unsigned int)iph->ttl);
				sum_TTL += (64 - iph->ttl);					// Avg number of hops
				sumsquare_TTL += ((64 - iph->ttl) * (64 - iph->ttl));		// Stddev of number of hops		
				break;
	default	:		return;
				break;


    }

   if(result == IP){
	n_required_packets_processed ++;
	avg_TTL = sum_TTL/n_required_packets_processed;

	stddev_TTL = sumsquare_TTL/n_required_packets_processed;
	stddev_TTL = stddev_TTL - (avg_TTL * avg_TTL);
	stddev_TTL = sqrt(stddev_TTL);
	
	
   }
    
    #ifdef DEBUG
    if(result == IP)
    fprintf(fp,"Src Ip = %s, Dst Ip = %s\n",src_ip,dst_ip);
    #endif

		
     if(result == IP){
	compute_ip_checksum(iph);
	switch(iph->protocol){
		case IPPROTO_TCP :	
					#ifdef DEBUG
					compute_tcp_checksum(iph,payload,fp);
					#endif
					fprintf(fp,"Protocol Type : TCP\n");
					break;
		case IPPROTO_UDP :	
					udphdrp = (struct udphdr*)(payload);				                
					udp_src_port = ntohs(udphdrp->source);
					#ifdef DEBUG
					compute_udp_checksum(iph,payload,fp);
					#endif
					fprintf(fp,"Protocol Type : UDP, Src port: %d\n", udp_src_port);
					break;

		case IPPROTO_ICMP :	fprintf(fp,"Protocol Type : ICMP\n");
					break;

		default :	
					fprintf(fp,"Protocol Type : Other\n");
					break;
	}

	fprintf(fp,"Avg Number of Hops : %f, STD DEV : %f\n",avg_TTL,stddev_TTL);
	fprintf(fp,"Number of packets observed : %d\n", n_required_packets_processed);
	fprintf(fp,"########################################################\n");

     }

     	
	    
     }


}

pcap_t* producer_init(FILE* fp){

	int found = 0;
        pcap_if_t *alldevs;
	pcap_if_t *d;
	pcap_addr_t *a;
	pcap_t* descr;
	int status = pcap_findalldevs(&alldevs, errbuf);
	if(status != 0) {
	        fprintf(fp,"%s\n", errbuf);
	        return NULL;
   	}
	for(d =alldevs; d!=NULL; d=d->next) {
   	        fprintf(fp,"%s:", d->name);
		if(strcmp(d->name,dev_name) == 0){
		       fprintf(fp,"Device found\n");
 		       for(a = d->addresses; a!=NULL; a=a->next) {
 		           if(a->addr->sa_family == AF_INET){
 		               sprintf(dev_ip_address,"%s", inet_ntoa(((struct sockaddr_in*)a->addr)->sin_addr));
 		               found = 1;
			       break;
				
			    }
 		       }
 	       
	       }
	       printf("\n");
 	}
        if(found == 0 ){
		fprintf(fp,"Device not found or IP address not defined for device. Run as root.\n");
		return NULL;
 	}

        pcap_freealldevs(alldevs);
        fprintf(fp,"Device ip address: %s\n",dev_ip_address);

	/* open device for reading */
 	descr = pcap_open_live(dev_name,BUFSIZ,0,-1,errbuf);
	if(descr == NULL)
	{ 
		fprintf(fp,"pcap_open_live(): %s\n",errbuf); 
		return NULL; 
	}
	return descr;
 
}

int run(pcap_t * descr, FILE* fp){	
	
	struct pcap_pkthdr *header;
	const u_char  *packet;
	int res;

	/* allright here we call pcap_loop(..) and pass in our callback function */
	/* int pcap_loop(pcap_t *p, int cnt, pcap_handler callback, u_char *user)*/
   
	//pcap_loop(descr,MAX_NO_OF_ENTRIES,my_callback,NULL);
	
	while(1){

				
		res = pcap_next_ex(descr, &header, &packet);
		
		if (res == 0) // Timeout expired. Retry. Examine stop condition.
		{
			fflush(stdout);
			continue;
		}
		if (res == -1) // Error 
		{
			fprintf(fp,"Error reading the packets: %s\n", pcap_geterr(descr));
			return -1;
		}
		else{
			my_callback(header,packet,fp);

		}
	}

	printf("\nDone processing packets\n");

	return 1;

}


int main(int argc, char** argv)
{
    int shmid;
    int fd;
    pid_t prod_pid;
    pcap_t *descr;
    char * shm_object_name;
    FILE * fp;

    struct timeval now;
    struct timeval later;
    struct timeval now1;
    struct timeval later1;
    struct tm localtm;
    struct tm origtm;


    if(argc != 4){

	//printf("Not enough arguments\n");
	//printf("Usage : ./pcap_packet_sniffer <Interface name> <Src IP to monitor> <Dst IP to monitor> \n");
	//return 0;
	dev_name = "emane0";
	src_ip_to_monitor = "10.100.0.41";
	dst_ip_to_monitor = "10.100.0.1";


    }
    else{
    dev_name = argv[1];
    src_ip_to_monitor = argv[2];
    dst_ip_to_monitor = argv[3];  
    }

    printf("Monitoring : %s, Src IP : %s, Dst IP %s\n",dev_name,src_ip_to_monitor,dst_ip_to_monitor);     
    gettimeofday(&now, NULL);
    gettimeofdayoriginal(&now1, NULL);
    gettimeofday(&later, NULL);
    gettimeofdayoriginal(&later1, NULL);
    localtime_r(&(later.tv_sec), &localtm);
    localtime_r(&(later1.tv_sec),&origtm);
	

    fp = stdout;
    fprintf(fp,"Started at, localtime: %d:%02d:%02d %ld, orig_time : %d:%02d:%02d %ld\n", localtm.tm_hour, localtm.tm_min, localtm.tm_sec, later.tv_usec, origtm.tm_hour, origtm.tm_min, origtm.tm_sec, later1.tv_usec);
    descr = producer_init(fp);

    if(descr == NULL){
	 fprintf(fp,"Descr is NULL\n");
	 return 0;
    }    
    else {
	run(descr,fp);
    }
    fclose(fp);

 
    return 0;

}
