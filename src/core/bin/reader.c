#include <fcntl.h>
#include <stdio.h>
#include <sys/stat.h>
#include <unistd.h>
#include <sys/poll.h>
#include <stdlib.h>
#define MAX_BUF 1024


int main(int argc, char ** argv)
{
    int fd;
    char buf[MAX_BUF];
    char debug[MAX_BUF];
    char command[MAX_BUF];
    char myfifo[MAX_BUF];
	
    if(argc != 3){
	    printf("Not enough arguments : ./reader <hostname> <log_dir>\n");
	    exit(1);
    }
    
    char * log_dir = argv[2];
    char * hostname = argv[1];
    
    sprintf(debug, "echo Starting Debug for %s > %s/%s", hostname, log_dir, hostname);
    system(debug);

	
    sprintf(myfifo, "/tmp/%s-reader", hostname);
    mkfifo(myfifo, 0666);
    /* open, read, and display the message from the FIFO */
    fd = open(myfifo, O_RDWR | O_NONBLOCK );
    struct pollfd ufds;
    int result;
    int rv;
    int pid;
    

    
    ufds.fd = fd;
    ufds.events = POLLIN;
    while (1) {
    	rv = poll(&ufds, 1, 100);
		if (rv == -1) {
	    	perror("poll"); // error occurred in poll()
		} else if (rv == 0) {
	   		//printf("rv is 0\n");
		} else {
	    	// check for events on s1:
	    	if (ufds.revents & POLLIN) {
        		result = read(fd, buf, MAX_BUF); // receive normal data
         		if (strcmp(buf, "exit") == 0) {
		       		printf("Exiting..\n");
		       		break;
	    		}
	    		pid = fork();
				if (pid == 0) { //in child
			
		    		sprintf(debug, "echo Running Command %s >> %s/%s", buf, log_dir, hostname);
		    		sprintf(command, "%s >> %s/%s 2>&1 &", buf, log_dir, hostname);
		    		system(debug);	
		    		system(command);
		    		return 0;
	    		}
   		}
	}

}
    close(fd);

    return 0;
}
