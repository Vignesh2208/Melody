build:
	@gcc -c -Wall -fpic gtod.c
	@gcc -shared -o libgtod.so gtod.o

clean:
	@rm -f gtod.o
	@rm -f libgtod.so
