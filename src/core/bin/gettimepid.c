#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <signal.h>
#include <sys/syscall.h>
#include <stdarg.h>
#include <sys/time.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/socket.h>
#include <linux/netlink.h>
#include <errno.h>
#include <fcntl.h>
#include <sys/select.h>

/*
Returns the virtual time of an LXC, given it's pid
*/
int gettimepid(int pid, struct timeval *tv, struct timezone *tz) {
	#ifdef __x86_64
	return syscall(315, pid, tv, tz);
	#endif
	return syscall(352, pid, tv , tz);
}

int main(int argc, char * argv[] ){

	struct timeval tv;
	struct timezone tz;

	if(argc == 1){

		//printf("Not enough arguments\n");
		exit(-1);
	}

	int pid = atoi(argv[1]);
	gettimepid(pid, &tv, &tz);
	
	printf("%ld\n",tv.tv_sec);
	return 0;
	
}

