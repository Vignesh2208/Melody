#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <stdarg.h>
#include <fcntl.h>
#include <sys/select.h>
#include <Python.h>
#include <sys/ioctl.h>

#define TK_IOC_MAGIC  'k'
#define TK_IO_GET_CURRENT_VIRTUAL_TIME _IOW(TK_IOC_MAGIC,  4, int)

/*
Returns the virtual time of an experiment, given it's pid. If pid == 0, it queries Kronos anyway for expected_virtual_time
*/
int gettimepid(int pid, struct timeval *tv, struct timezone *tz) {

        int res, fp;

	if (pid == 0) {
		fp = open("/proc/status", O_RDWR);
		if (fp == -1) {
			return -1;
		}
		res = ioctl(fp, TK_IO_GET_CURRENT_VIRTUAL_TIME, tv);
		close(fp);
		return res;
	}

	
	#ifdef __x86_64
	return syscall(327, pid, tv, tz);
	#endif
	return syscall(378, pid, tv , tz);
	
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
	if (gettimepid(pid,&tv,&tz) >= 0 )
		sprintf(result,"%ld.%ld\n",tv.tv_sec,tv.tv_usec);
	else
		sprintf(result,"0.0\n");
   	
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

