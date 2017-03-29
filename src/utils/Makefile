all:
	gcc -c -Wall -fpic gtod.c
	gcc -shared -o libgtod.so gtod.o

clean:
	rm gtod.o
	rm libgtod.so
