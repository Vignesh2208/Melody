#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <math.h>
#include <stdlib.h>


void flush_buffer(char * buf, int size){

        int i = 0;
        for(i = 0; i < size; i++)
                buf[i] = '\0';

}



int main(int argc, char ** argv){

FILE * fd;
int my_Index = 0;
char read_lock_file_name[100];
char write_lock_file_name[100];
char route_table_file[100];

if(argc !=2){
	printf("Not enough arguments. Usage ./routing_table_reader <this node index>\n");
	exit(1);
}

my_Index = atoi(argv[1]);

sprintf(read_lock_file_name,"/tmp/emane/lxc/%d/route_read_lock.txt",my_Index);
sprintf(write_lock_file_name,"/tmp/emane/lxc/%d/route_write_lock.txt",my_Index);
sprintf(route_table_file,"/tmp/emane/lxc/%d/route_table.txt",my_Index);

int spin = 0;
char line[1000];

flush_buffer(line,1000);
int i = 0;

while(1){
	fd = popen("/sbin/route -n","r");
	if(fd == NULL){
		printf("Failed to run command\n");
		exit(1);	
	}

	spin = 1;
        while(spin){
              if( access(read_lock_file_name, F_OK ) != -1 ) {
                    // file exists
        	    spin = 1;
               } else {
                    spin = 0;
               }
        }

	 FILE * temp = fopen(write_lock_file_name,"w");

         FILE * fp = fopen(route_table_file,"w");
	 if(fp != NULL){

		while (fgets(line, 1000, fd) != NULL) {
			fprintf(fp,line);
			flush_buffer(line,1000);
		}
	}	 

	fclose(fp);
	pclose(fd);
	remove(write_lock_file_name);

	usleep(100000);
	i++;

}
}
