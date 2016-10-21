#include "ring_buffer.h"
#include <pcap/pcap.h>
#include <arpa/inet.h>
#include <netinet/if_ether.h>
#include <sys/socket.h>
#include <sys/mman.h>
#include <time.h>

#define TRUE 1
#define FALSE 0
#define MAX_NO_OF_ENTRIES 10


int exec_system_command(char* cmd)
{
    // see
	// http://stackoverflow.com/questions/478898/how-to-execute-a-command-and-get-output-of-command-within-c

	FILE* pipe = popen(cmd, "r");
    	if (!pipe){

		printf("exec system command Error!\n");
		return -1;
	}
    	

    return 1;
}

ringBufS * buffer_ptr;

int main(int argc, char** argv)
{
    int shmid;
    pid_t prod_pid;
    timestamp* entry;
    int max_no_of_unbuffered_entries = MAX_NO_OF_ENTRIES;
    int no_of_unbuffered_entries = 0;
    char cmd[100] ;
    int fd;


   


    shm_unlink("test");
    fd = shm_open("test",O_CREAT|O_RDWR,S_IRUSR | S_IWUSR);
    if(fd == -1){
		printf("Error in open\n");
		return 0;
    }


    ftruncate(fd,sizeof(ringBufS));

    buffer_ptr = mmap(NULL,sizeof(ringBufS),PROT_READ|PROT_WRITE,MAP_SHARED,fd, 0);
    close(fd);

    
 
    /* initialise the buffer */
    buffer_ptr->head = 0;
    buffer_ptr->tail = 0;
 
    /* initialise our semaphores (2nd param 1 means shared betweeen processes */
    sem_init(&buffer_ptr->empty, 1, RBUF_SIZE);
    sem_init(&buffer_ptr->full, 1, 0);
    sem_init(&buffer_ptr->mutex, 1, 1);
    sem_init(&buffer_ptr->stop,1,0);

	
        printf("Consumer started\n");
	while (TRUE)
        {
            if(no_of_unbuffered_entries >= max_no_of_unbuffered_entries){
		sem_post(&buffer_ptr->stop);
		sleep(100);
		break;
            }
	    
            sem_wait(&buffer_ptr->full);
            
            sem_wait(&buffer_ptr->mutex);
 
            printf("Unbuffered entry : ");
            entry = get(buffer_ptr);
            if(entry != NULL){

	        printf("secs = %d ",entry->secs);
		printf("u_secs = %d ",entry->u_secs);
        	printf("n_secs = %d ",entry->n_secs);
	        printf("pkt_hash_code = %d\n",entry->pkt_hash_code);
            	entry->is_read = 1;
            }
            no_of_unbuffered_entries++;
            sem_post(&buffer_ptr->mutex);
            sem_post(&buffer_ptr->empty);
        }

    /* detach the shared memory and deallocate the memory segment */

    munmap(buffer_ptr,sizeof(ringBufS));

 
    return 0;
 


}


