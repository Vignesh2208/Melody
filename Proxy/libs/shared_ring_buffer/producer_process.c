#include "producer.h"


int main(int argc, char** argv)
{
    int shmid;
    int fd;
    pid_t prod_pid;
    pcap_t *descr;

        
    fd = shm_open("test",O_CREAT|O_RDWR,S_IRUSR | S_IWUSR);
    if(fd == -1){
	printf("Error in open\n");
	return 0;
    }
    
    buffer_ptr = mmap(NULL,sizeof(ringBufS),PROT_READ|PROT_WRITE,MAP_SHARED,fd,0);
    close(fd);
  
        
    descr = producer_init();
    if(descr == NULL){
	return 0;
    }    
    else {
	run(descr);
    }
   munmap(buffer_ptr,sizeof(ringBufS));
	

 
return 0;

}
