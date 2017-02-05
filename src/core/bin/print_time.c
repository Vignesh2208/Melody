#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <math.h>
#include <stdlib.h>

int main(int argc, char ** argv){

int i = 0;
for(i = 0; i < 50; i++){

	fprintf(stdout,"%d secs elapsed\n",i);
	fflush(stdout);
	usleep(1000000);

}

return 0;

}
