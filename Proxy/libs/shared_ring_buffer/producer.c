
#include "producer.h"

uint32_t packet_hash(const char * s,int size)
{

    //http://stackoverflow.com/questions/114085/fast-string-hashing-algorithm-with-low-collision-rates-with-32-bit-integer
    uint32_t hash = 0;
    char * ptr = s;
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

void get_ip_addresses(const u_char * Buffer, int Size)
{
      
    unsigned short iphdrlen;
         
    struct iphdr *iph = (struct iphdr *)(Buffer  + sizeof(struct ethhdr) );
    iphdrlen =iph->ihl*4;
     
    memset(&source, 0, sizeof(source));
    source.sin_addr.s_addr = iph->saddr;
     
    memset(&dest, 0, sizeof(dest));
    dest.sin_addr.s_addr = iph->daddr;

    memset(src_ip,0,sizeof(src_ip));
    memset(dst_ip,0,sizeof(dst_ip));

    sprintf(src_ip,"%s",inet_ntoa(source.sin_addr));
    sprintf(dst_ip,"%s",inet_ntoa(dest.sin_addr));

}


/* callback function that is passed to pcap_loop(..) and called each time 
 * a packet is recieved                                                    */
void my_callback(const struct pcap_pkthdr* pkthdr,const u_char*  packet)
{
    
    timestamp entry;
    struct timeval tv;
    int size = pkthdr->len;
     
    
    
    get_ip_addresses(packet,size);
    printf("Packet Src IP = %s, Dst IP = %s\n",src_ip,dst_ip);
    if(strcmp(dev_ip_address,src_ip) == 0){
	
	     sem_wait(&buffer_ptr->empty);
	     sem_wait(&buffer_ptr->mutex);
 

	     gettimeofday(&tv,0);    
	     entry.secs = tv.tv_sec;
	     entry.u_secs = tv.tv_usec;
	     entry.n_secs = 0;
	     entry.is_read = 0;
	     entry.pkt_hash_code = (long)packet_hash(packet,size);

	     
	     printf("Buffering : secs = %d, u_secs = %d, n_secs = %d, pkt_hash_code = %d\n",entry.secs,entry.u_secs,entry.n_secs,entry.pkt_hash_code);
	     put(buffer_ptr,&entry);
 	
	     sem_post(&buffer_ptr->mutex);
 	     sem_post(&buffer_ptr->full);
    }


}

pcap_t* producer_init(){

	int found = 0;
        pcap_if_t *alldevs;
	pcap_if_t *d;
	pcap_addr_t *a;
	pcap_t* descr;
	dev_name = "wlan0";
	int status = pcap_findalldevs(&alldevs, errbuf);
	if(status != 0) {
	        printf("%s\n", errbuf);
	        return NULL;
   	}
	for(d =alldevs; d!=NULL; d=d->next) {
 	       printf("%s:", d->name);
		if(strcmp(d->name,dev_name) == 0){
		       printf("Device found\n");
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
		printf("Device not found or IP address not defined for device. Run as root.\n");
		return NULL;
 	}

        pcap_freealldevs(alldevs);
        printf("Device ip address: %s\n",dev_ip_address);

	/* open device for reading */
 	descr = pcap_open_live(dev_name,BUFSIZ,0,-1,errbuf);
	if(descr == NULL)
	{ 
		printf("pcap_open_live(): %s\n",errbuf); 
		return NULL; 
	}
	return descr;
 
}

int run(pcap_t * descr){	
	
	struct pcap_pkthdr *header;
	u_char  *packet;
	int res;

	/* allright here we call pcap_loop(..) and pass in our callback function */
	/* int pcap_loop(pcap_t *p, int cnt, pcap_handler callback, u_char *user)*/
   
	//pcap_loop(descr,MAX_NO_OF_ENTRIES,my_callback,NULL);
	
	while(1){
		res = pcap_next_ex(descr, &header, &packet);
		if (res == 0) // Timeout expired. Retry. Examine stop condition.
		{
			if(sem_trywait(&buffer_ptr->stop) == 0) // Check if stop semaphore was set.
			{
				printf("Stopping producer ..\n");
				return 1;
			}
			continue;
		}
		if (res == -1) // Error 
		{
			printf("Error reading the packets: %s\n", pcap_geterr(descr));
			return -1;
		}
		else{
			my_callback(header,packet);

		}
	}

	printf("\nDone processing packets\n");

	return 1;

}

