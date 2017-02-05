
#include <fcntl.h>
#include <stdio.h>
#include <sys/stat.h>
#include <unistd.h>
#include <sys/poll.h>
#include <signal.h>
#include <stdlib.h>
#include <sys/syscall.h>
#include <sys/mount.h>
#include <sys/utsname.h>
#include <linux/sched.h>
#include <time.h>
#include <sys/time.h>

#define LEN 100

int main(int argc, char *argv[]){

char line[LEN];
char kill_cmd[LEN];
FILE *cmd = popen("pidof olsrd", "r");
struct timeval now;
struct tm localtm;

fgets(line, LEN, cmd);
pid_t pid = strtoul(line, NULL, 10);

pclose(cmd);

if(pid != 0){

	printf("PID of olsrd = %d\n",pid);
	sprintf(kill_cmd,"sudo kill %d\n",pid);
	system(kill_cmd);
	gettimeofday(&now, NULL);
	localtime_r(&(now.tv_sec), &localtm);
	printf("olsrd killed at localtime: %d:%02d:%02d %ld\n", localtm.tm_hour, localtm.tm_min, localtm.tm_sec, now.tv_usec);
}


}
