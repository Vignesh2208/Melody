
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <sys/time.h>
#include <unistd.h>
#define N_THREADS 10

typedef struct thread_arg_struct {

	int thread_no;
	
} thread_arg;

int count_array[N_THREADS];

void print_time(char * output){
    time_t rawtime;
    struct timeval now;
    struct tm localtm;
    
    struct tm * timeinfo;

    //time ( &rawtime );
    //timeinfo = localtime ( &rawtime );
	gettimeofday(&now, NULL);
	localtime_r(&(now.tv_sec), &localtm);

    //sprintf(output, "[%d %d %d %d:%d:%d]",timeinfo->tm_mday, timeinfo->tm_mon + 1, timeinfo->tm_year + 1900, timeinfo->tm_hour, timeinfo->tm_min, timeinfo->tm_sec);
    sprintf(output, "[%d:%02d:%02d %ld]",localtm.tm_hour, localtm.tm_min, localtm.tm_sec, now.tv_usec);
    
}

void flush_buffer(char * buf, int size) {
	int i = 0;
	for(i = 0; i < size; i++)
		buf[i] = '\0';
}

void * threadFn( void * ptr) {

	thread_arg * arg = ptr;
	int i = 0;

	//sleep(5);
	
	//usleep(5000000);
	char time_buffer[100];
	flush_buffer(time_buffer,100);
	print_time(time_buffer);
	fprintf(stdout, "Thread %d: Resumed at %s\n", arg->thread_no,time_buffer);
	fflush(stdout)	;

	for(i = 0; i >=0 ; i ++){
		int j = 0;
		char time_buf[100];
		flush_buffer(time_buf,100);
		print_time(time_buf);
		
		for(j = 0; j < 1000000; j++);

		count_array[arg->thread_no -1] = i;

		//fprintf(stdout,"Thread %d: Count = %d, Curr Time = %s\n", arg->thread_no,i,time_buf);		
		//fflush(stdout);
	}
		
}

thread_arg args[N_THREADS];

int main(){

	pthread_t tid[N_THREADS];
	int i = 0;
	int j = 0;
	char time_buf[100];
	flush_buffer(time_buf,100);
	print_time(time_buf);

	for(i =0; i < N_THREADS; i++)
		count_array[i] = 0;

	fprintf(stdout,"Started Thread spawner at : %s\n", time_buf);
	fflush(stdout);
	for(i = 0; i < N_THREADS; i++) {
		args[i].thread_no = i + 1;
		//if(i == 0)
		pthread_create(&tid[i],NULL,threadFn,&args[i]);
	}


	while(1) {

		printf("----------------------------------------------------------------------------------------------\n");
		printf("\n");
		for(j = 0; j < N_THREADS; j++)
			printf("%d ",count_array[j]);
		flush_buffer(time_buf,100);
		print_time(time_buf);
		printf("Time = %s",time_buf);
		printf("\n");
		printf("\n");
		fflush(stdout);
		//sleep(1);
		//usleep(1000000);
		for(j=0; j < 200000000; j++);

	}

	for(i = 0; i < N_THREADS; i++) {
		pthread_join(tid[i],NULL);

	}

	fprintf(stdout,"Exiting Thread spawner ... \n");
	fflush(stdout);
	return 0;
}
