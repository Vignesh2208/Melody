all: reader_process gettime

reader_process: reader.c
	gcc -o reader reader.c


gettime: gettimepid.c
	gcc -o gettimepid gettimepid.c

thread_spawn: thread_spawner.c
	gcc -o thread_spawner thread_spawner.c -lpthread

clean:
	rm *.o
	rm reader 
	rm gettimepid

