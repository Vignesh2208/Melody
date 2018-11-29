build: reader_process gettime timerfd

reader_process: reader.c
	gcc -o reader reader.c
	chmod 777 reader


gettime: gettimepid.c
	gcc -o gettimepid gettimepid.c -I/usr/include/python2.7 -lpython2.7
	chmod 777 gettimepid

thread_spawn: thread_spawner.c
	gcc -o thread_spawner thread_spawner.c -lpthread
	chmod 777 thread_spawner

timerfd: timerfd_test.c
	gcc -o timerfd_test timerfd_test.c
	chmod 777 timerfd_test

clean:
	@rm -f reader 
	@rm -f gettimepid
	@rm -f timerfd_test

