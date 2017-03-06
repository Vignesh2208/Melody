#include <fcntl.h>
#include <stdio.h>
#include <sys/stat.h>
#include <unistd.h>
#include <sys/poll.h>
#include <stdlib.h>
#include <string.h>
#include <sys/resource.h>

#define MAX_BUF 1024

void flush_buffer(char * buf, int size) {

	int i = 0;
	for(i = 0; i < size; i++)
		buf[i] = '\0';

}


int main(int argc, char ** argv)
{
    int fd;
    char buf[MAX_BUF];
    char output_buf[MAX_BUF];
    char log_file[MAX_BUF];
    char debug[MAX_BUF];
    char command[MAX_BUF];
    char myfifo[MAX_BUF];
	
    if(argc != 3){
	    printf("Not enough arguments : ./reader <hostname> <log_dir>\n");
	    exit(1);
    }
    
    char * log_dir = argv[2];
    char * hostname = argv[1];
    int my_pid = getpid();
    
    printf("Starting Debug for %s. Reader Process pid = %d\n", hostname, my_pid);
    fflush(stdout);



    //flush_buffer(debug,MAX_BUF);
    //sprintf(debug, "sudo iptables -I INPUT -p icmp -j ACCEPT &");
    //system(debug);


    //flush_buffer(debug,MAX_BUF);
    //sprintf(debug, "sudo iptables -I OUTPUT -p icmp -j ACCEPT &");
    //system(debug);	

	
    sprintf(myfifo, "/tmp/%s-reader", hostname);
    mkfifo(myfifo, 0666);
    /* open, read, and display the message from the FIFO */
    fd = open(myfifo, O_RDWR | O_NONBLOCK );
    struct pollfd ufds;
    int result;
    int rv;
    int pid;
    
    sprintf(log_file, "%s/%s", log_dir,hostname);

    
    ufds.fd = fd;
    ufds.events = POLLIN;
    while (1) {
    	rv = poll(&ufds, 1, -1);
		if (rv == -1) {
	    		perror("poll"); // error occurred in poll()
		} else if (rv == 0) {
	   		//printf("rv is 0\n");
		} else {
	    	// check for events on s1:
	    	if (ufds.revents & POLLIN) {

			int evt_no = 0;
			for(evt_no = 0; evt_no < 1; evt_no ++){
				memset(buf,0,MAX_BUF);
				result = read(fd, buf, MAX_BUF); // receive normal data
		 		if (strcmp(buf, "exit") == 0) {
			       		printf("Exiting..\n");
			       		break;
		    		}
		    		pid = fork();
				if (pid == 0) { //in child	
					my_pid  = getpid();
					printf("\nRunning New Command %s\n", buf);
					fflush(stdout);
					
					sprintf(command, "%s >> %s/%s 2>&1", buf, log_dir, hostname);
					system(command);
					fflush(stdout);


					return 0;
	    			}
			}
   		}
	}

}
    close(fd);

    return 0;
}
