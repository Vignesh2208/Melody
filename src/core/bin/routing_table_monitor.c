#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
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

#define IP 1
#define NOT_IP 2
#define NOT_SUPPORTED -1
#define TRUE 1
#define FALSE 0


static char * radio_IP_start = "10.100.0.0";
static float read_interval = 0.1;

unsigned long IP2Int(char* ipAddress) {
  unsigned int ipbytes[10];
  //sscanf(ipAddress, "%uhh.%uhh.%uhh.%uhh", &ipbytes[3], &ipbytes[2], &ipbytes[1], &ipbytes[0]);
  sscanf(ipAddress, "%d.%d.%d.%d", &ipbytes[3], &ipbytes[2], &ipbytes[1], &ipbytes[0]);
  //printf("ipbytes 0 = %d\n", ipbytes[0]);
  //printf("ipbytes 1 = %d\n", ipbytes[1]);
  //printf("ipbytes 2 = %d\n", ipbytes[2]);
  //printf("ipbytes 3 = %d\n", ipbytes[3]);
  return (ipbytes[0]&0xFF) | ((ipbytes[1]&0xFF) << 8) | ((ipbytes[2]&0xFF) << 16) | ((ipbytes[3]&0xFF) << 24);
}


int Int2IP(int ip, char * ip_string)
{
    unsigned char bytes[4];
    bytes[0] = ip & 0xFF;
    bytes[1] = (ip >> 8) & 0xFF;
    bytes[2] = (ip >> 16) & 0xFF;
    bytes[3] = (ip >> 24) & 0xFF;	
    sprintf(ip_string,"%d.%d.%d.%d\n", bytes[3], bytes[2], bytes[1], bytes[0]);        
}

void usage(){

	printf("Incorrect usage. Correct usage : ./routing_table_monitor <This-node-IP> <number of nodes> <number of secs to run >");
	exit(-1);
}

void flush_buffer(char * buf, int size){

	int i = 0;
	for(i = 0; i < size; i++)
		buf[i] = '\0';

}


int main(int argc, char ** argv){


	FILE * fp;
	FILE * fd;
	char * my_IP;
	int my_IP_index;
	int n_nodes;
	int n_secs;
	int total_no_of_oscillations = 0;

	
	float * node_count;
	float * node_count_variance;
	float * node_available;
	long * node_down_time;
	int i = 0, j = 0;
	char line[1000];
	char ** tokens;
	char * entry_IP;
	int entry_IP_index;
	int prev_present_IP_index = -1;
	int k;
	float sum_value;
	float variance_value;
	float sum;
	float variance;
	float mean;
	int count = 0;
	int node_downs = 0;
	struct timeval downTimeStamp,currTimeStamp;
	long downTS, currTS;
	long max_down_time = 0;
	int max_down_node = 0;
	fp = stdout;
	int spin = 1;
	char read_lock_file_name[100];
	char write_lock_file_name[100];
	char route_table_file[100];

	struct timeval now;	
	struct timeval later;
	struct timeval now1;
        struct timeval later1;
	struct tm localtm;
	struct tm origtm;

	
	if(argc != 4)
		usage();

	my_IP = argv[1];
	n_nodes = atoi(argv[2]);
	n_secs = atoi(argv[3]);
	

	if(n_nodes <= 1){
		printf("Number of nodes must be greater than 1\n");
		exit(-1);
	}


	
	fprintf(fp,"My IP : %s, N_nodes = %d, N_secs = %d\n", my_IP, n_nodes, n_secs);
	node_count = (float *) malloc(sizeof(float)*n_nodes);
	node_count_variance = (float *) malloc(sizeof(float)*n_nodes);
	node_available = (float *) malloc(sizeof(float) * n_nodes);
	node_down_time = (long *) malloc(sizeof(long) * n_nodes);

	if(node_count == NULL || node_count_variance == NULL || node_available == NULL){
		printf("Malloc failed\n");
		exit(-1);
	}

	for(i = 0; i < n_nodes; i++){
		node_count[i] = 0;
		node_available[i] = -1;
		node_count_variance[i] = 0;

	}

	
	my_IP_index = IP2Int(my_IP)  - IP2Int(radio_IP_start) - 1;	
	sprintf(read_lock_file_name,"/tmp/emane/lxc/%d/route_read_lock.txt",my_IP_index + 1);
	sprintf(write_lock_file_name,"/tmp/emane/lxc/%d/route_write_lock.txt",my_IP_index + 1);
	sprintf(route_table_file,"/tmp/emane/lxc/%d/route_table.txt",my_IP_index + 1);

	//int n_units = (int) 10/read_interval;
	int n_units = (int) 1/read_interval;
	

	for(i = 0 ; i < (int)(n_secs/read_interval); i++){

		count = 0;
		usleep((int)(1000000*read_interval));
		if( i % n_units == 0){

			//fprintf(fp,"%d Secs elapsed\n", (i/n_units + 1)*10);
			fprintf(fp,"%d Secs elapsed\n", (i/n_units + 1)*1);

			gettimeofday(&later, NULL);
			gettimeofdayoriginal(&later1, NULL);
			localtime_r(&(later.tv_sec), &localtm);
			localtime_r(&(later1.tv_sec),&origtm);
	

			printf("localtime: %d:%02d:%02d %ld, orig_time : %d:%02d:%02d %ld\n", localtm.tm_hour, localtm.tm_min, localtm.tm_sec, later.tv_usec, origtm.tm_hour, origtm.tm_min, origtm.tm_sec, later1.tv_usec);
			fflush(stdout);

		}
/*		spin = 1;
		while(spin){
			if( access( write_lock_file_name, F_OK ) != -1 ) {
		    		// file exists
				spin = 1;
			} else {
		    		spin = 0;
			}
		}
		if( access(route_table_file, F_OK ) != -1 ) 
		{
		    		// file exists
		} else {
			continue;
		}


		FILE * temp = fopen(read_lock_file_name,"w");

		fd = fopen(route_table_file,"r");

                if(fd == NULL){
			printf("Failed to open route_table_File\n");
			remove(read_lock_file_name);
			continue;

		}*/
 		fd = popen("/sbin/route -n", "r");
		if (fd == NULL) {
			printf("Failed to run command\n" );
			exit(1);
		}
		prev_present_IP_index = -1;
		/* Read the output a line at a time - output it. */
		while (fgets(line, 1000, fd) != NULL) {
			

			if(count < 2){
				count++;
				flush_buffer(line,1000);
				continue;
			}
			j = 0;
			while(line[j] != ' '){
				j++;
			}
			line[j] = '\0';

			entry_IP = line;
			entry_IP_index = IP2Int(entry_IP) - IP2Int(radio_IP_start) - 1;
			k = prev_present_IP_index + 1;
			while( k < entry_IP_index && entry_IP_index >= 0 && entry_IP_index < n_nodes && k >= 0){
				if(node_available[k] == 1){
					fprintf(fp,"Node-%d Went down\n", k+1);
					node_available[k] = 0;
					gettimeofday(&downTimeStamp, NULL);		
					downTS = downTimeStamp.tv_sec * 1000000 + downTimeStamp.tv_usec;

					node_down_time[k] = downTS;
					node_downs ++;
				}				
				k = k + 1;
			}

			if( entry_IP_index >= 0 && entry_IP_index < n_nodes && node_available[entry_IP_index] == 0){
				fprintf(fp,"Node-%d Came back up. Number of oscillations: %d\n",entry_IP_index + 1,total_no_of_oscillations + 1);
				gettimeofday(&downTimeStamp, NULL);		
				downTS = downTimeStamp.tv_sec * 1000000 + downTimeStamp.tv_usec;
				node_down_time[entry_IP_index] = downTS - node_down_time[entry_IP_index];
				if(node_down_time[entry_IP_index] > max_down_time){
					max_down_time = node_down_time[entry_IP_index];
					max_down_node = entry_IP_index + 1;
				}
				node_downs --;
				node_available[entry_IP_index] = 1;
				total_no_of_oscillations = total_no_of_oscillations + 1;
			}	
			else if(entry_IP_index >= 0 && entry_IP_index < n_nodes && node_available[entry_IP_index] == -1)
				node_available[entry_IP_index] = 1;
			
			if(entry_IP_index >= 0 && entry_IP_index < n_nodes){
				node_count[entry_IP_index] = node_count[entry_IP_index] + 1;
				prev_present_IP_index = entry_IP_index;
			}			
			flush_buffer(line,1000);
				

		}
		fflush(stdout);
		/* close */
		pclose(fd);
		//fclose(fd);
		//remove(read_lock_file_name);
	}


	
	sum_value = 0.0;
	variance_value = 0.0;
	gettimeofday(&currTimeStamp,NULL);

	for(i = 0;  i < n_nodes; i++){
		if( i != my_IP_index ){
			sum_value = sum_value + node_count[i];
			variance_value = variance_value + (node_count[i]*node_count[i]);

			node_count[i] = node_count[i]/(float)(n_secs/read_interval);
			node_count_variance[i] = (float)node_count[i]*(1 - node_count[i]);
			fprintf(fp,"Node : %d, Mean Availability (per Sec) : %f, Variance of Availablility (per Sec) : %f\n", i + 1, node_count[i], node_count_variance[i]);
		}	
		if(node_available[i] == 0){
			currTS = currTimeStamp.tv_sec * 1000000 + currTimeStamp.tv_usec;
			if(max_down_time < currTS - node_down_time[i]){
				max_down_time = currTS - node_down_time[i];
				max_down_node = i + 1;
			}
			
		}	
	
	}

	if(n_nodes > 1){
		mean = (float)(sum_value*read_interval)/(n_nodes - 1);
		variance = (float)(variance_value*read_interval*read_interval)/(n_nodes - 1);
		variance = variance - (mean*mean);
		fprintf(fp,"Total Mean Availablity (Secs) : %f\n", mean);
		fprintf(fp,"Total Std deviation of Availability (Secs) : %f\n", sqrt(variance));
		fprintf(fp,"Total number of oscillations : %d\n", total_no_of_oscillations);
		fprintf(fp,"Number of Nodes down : %d\n",node_downs);
		fprintf(fp,"Max Down Time: (usec) %lu\n", max_down_time);
		fprintf(fp,"Max Down Node : %d\n",max_down_node);
	}

	fflush(stdout);
	free(node_count);
	free(node_count_variance);
	free(node_available);
	free(node_down_time);

}




