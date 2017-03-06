all: reader_process gettime timerfd

reader_process: reader.c
	gcc -o reader reader.c


gettime: gettimepid.c
	gcc -o gettimepid gettimepid.c

thread_spawn: thread_spawner.c
	gcc -o thread_spawner thread_spawner.c -lpthread

timerfd: timerfd_test.c
	gcc -o timerfd_test timerfd_test.c

clean:
	rm *.o
	rm reader 
	rm gettimepid

