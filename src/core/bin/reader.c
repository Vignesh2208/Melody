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
    //setpriority(PRIO_PROCESS,0,-5);
    sprintf(debug, "echo Starting Debug for %s. Reader Process pid = %d > %s/%s", hostname, my_pid, log_dir, hostname);
    system(debug);

	flush_buffer(debug,MAX_BUF);
	sprintf(debug, "sudo iptables -I INPUT -p icmp -j ACCEPT &");
    system(debug);


	flush_buffer(debug,MAX_BUF);
	sprintf(debug, "sudo iptables -I OUTPUT -p icmp -j ACCEPT &");
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
    	rv = poll(&ufds, 1, -1);
		if (rv == -1) {
	    	perror("poll"); // error occurred in poll()
		} else if (rv == 0) {
	   		//printf("rv is 0\n");
		} else {
	    	// check for events on s1:
	    	if (ufds.revents & POLLIN) {
				flush_buffer(buf,MAX_BUF);
        		result = read(fd, buf, MAX_BUF); // receive normal data
         		if (strcmp(buf, "exit") == 0) {
		       		printf("Exiting..\n");
		       		break;
	    		}
	    		pid = fork();
				if (pid == 0) { //in child
			
					
					my_pid  = getpid();
					flush_buffer(debug,MAX_BUF);
		    		sprintf(debug, "echo Running Command %s >> %s/%s", buf, log_dir, hostname);
					system(debug);
					flush_buffer(debug,MAX_BUF);
					sprintf(debug,"echo Reader Child Process pid = %d >> %s/%s", my_pid, log_dir, hostname);
					system(debug);

					sprintf(log_file, "%s/%s", log_dir,hostname);


		    		sprintf(command, "%s >> %s/%s 2>&1", buf, log_dir, hostname);
					system(command);

					/*
					sprintf(command, "%s 2>&1", buf);					
		    
                    FILE *cm_pipe = popen(command, "r");
					int num_bytes_received = 0;
					int start_idx = 0;                    
                    while(fgets(output_buf + start_idx, MAX_BUF - num_bytes_received, cm_pipe) != NULL) {
						num_bytes_received = strlen(output_buf);
						start_idx = num_bytes_received; 

					}
					FILE * fp = fopen(log_file,"a");
					if(fp != NULL) {
						fprintf(fp,"%s\n",output_buf);
					}
					pclose(cm_pipe);
					fclose(fp);
					*/

		    		
		    		return 0;
	    		}
   		}
	}

}
    close(fd);

    return 0;
}
