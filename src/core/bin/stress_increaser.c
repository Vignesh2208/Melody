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

int main(){
	int pid;
	int i = 0;
	unsigned long long int fact = 1;

	/*for(i = 0; i < 100; i++){
		pid = fork();
		if(pid == 0){
			while(1);
			return 0;
		}
	}/
	/*
	while(1){

		for(i = 1; i < 1000000000; i++){
			if(fact == 0)
				fact = 1;
			fact = fact*i;
		}

	}*/

	//while(1);
	return 0;

}
