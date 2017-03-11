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
#include <Python.h>

/*
Returns the virtual time of an LXC, given it's pid
*/
int gettimepid(int pid, struct timeval *tv, struct timezone *tz) {

    long double res;
	#ifdef __x86_64
	return syscall(315, pid, tv, tz);
	#endif
	return syscall(352, pid, tv , tz);
	
}

static PyObject * py_gettimepid(PyObject * self, PyObject * args){
	int pid;
	struct timeval tv;
	struct timezone tz;
	char result[100];
		
	if (!PyArg_ParseTuple(args, "i", &pid)) {
        Py_RETURN_NONE;
   	}
   	
   	memset(result,0,100);
	gettimepid(pid,&tv,&tz);
	sprintf(result,"%ld.%ld\n",tv.tv_sec,tv.tv_usec);
   	
   	return Py_BuildValue("s", result); 
   	
   	


}


// PYTHON Module definition functions
static PyMethodDef gettimepid_methods[] = {
   { "gettimepid", py_gettimepid, METH_VARARGS, NULL },   
};





#if PY_MAJOR_VERSION <= 2

void initgettimepid(void)
{
   	Py_InitModule3("gettimepid", gettimepid_methods,"gettimepid");
}


#elif PY_MAJOR_VERSION >= 3 

static struct PyModuleDef gettimepid_definition = { 
   	PyModuleDef_HEAD_INIT,
   	"gettimepid",
   	"A Python module that performs gettimepid",
   	-1, 
   	gettimepid_methods
};
PyMODINIT_FUNC PyInit_gettimepid(void)
{
   	Py_Initialize();
    return PyModule_Create(&gettimepid_definition);
}

#endif



int main(int argc, char * argv[] ){

	struct timeval tv;
	struct timezone tz;

	if(argc == 1){
		//printf("Not enough arguments\n");
		exit(-1);
	}

	int pid = atoi(argv[1]);
	gettimepid(pid, &tv, &tz);
	
	printf("%ld.%ld\n",tv.tv_sec,tv.tv_usec);
	return 0;
	
}

