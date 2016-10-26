#include "shared_buf.h"


hashmap sharedBufMap;
llist sharedBufNames;


void __flushBuffer(char * buf, int length){
	int i;
	for(i = 0; i < length; i++)
		buf[i] = '\0';
}

void __init() {
	
	hmap_init(&sharedBufMap,"string",0);
	llist_init(&sharedBufNames);

}

/*
Called by proxy
*/
void __initNewSharedBuffer(sharedPacketBuf * newBuf) {
	if(newBuf == NULL)
		return;

	
	sem_init(&newBuf->lock,IS_SHARED,UNLOCKED);
	sem_wait(&newBuf->lock);
	newBuf->flow = PROXY_TO_HOST;
	newBuf->ack = TRUE;
	newBuf->dirty = FALSE;
	newBuf->pad = 0;
	newBuf->dstID = 0;
	newBuf->pktLen = 0;
	__flushBuffer(newBuf->pkt,MAXPKTSIZE);
	newBuf->isInit = INIT_MAGIC;
	sem_post(&newBuf->lock);

}

void display(llist * l){
	int i;
    char  * p;
	for(i = 0; i < l->size; i++){
		p = llist_get(l,i);
		printf("%s",p);
	}
	printf("\n");
}

/*
Called by host/proxy
*/
bool __addNewSharedBuffer(char * bufName, bool isProxy) {
	int length = strlen(bufName) + 1;
	char * newBufName = (char *)malloc(sizeof(char)*length);
	__flushBuffer(newBufName,length+1);
	//shm_unlink(bufName);
    int fd = shm_open(bufName,O_CREAT|O_RDWR,S_IRUSR | S_IWUSR);
    if(fd == -1){
		printf("Error in shm open\n");
		return FAILURE;
    }

    ftruncate(fd,sizeof(sharedPacketBuf));
    sharedPacketBuf * newBufPtr = mmap(NULL,sizeof(sharedPacketBuf),PROT_READ|PROT_WRITE,MAP_SHARED,fd, 0);
    close(fd);
	

	if(bufName == NULL || newBufName == NULL || newBufPtr == NULL)
		return FAILURE;

	strncpy(newBufName,bufName,length-1);
	assert(strlen(newBufName) == length - 1);

	llist_append(&sharedBufNames,newBufName);
	hmap_put(&sharedBufMap,newBufName,newBufPtr);

	if(isProxy) {
		__initNewSharedBuffer(newBufPtr);
    }
	return SUCCESS;


}


/*
Called by host/proxy
*/
void __destroyAllSharedBuffers() {
	while(llist_size(&sharedBufNames) > 0) {
		char * bufName = llist_pop(&sharedBufNames);
		sharedPacketBuf * bufPtr = hmap_get(&sharedBufMap,bufName);
		assert(bufName != NULL && bufPtr != NULL);

		munmap(bufPtr,sizeof(sharedPacketBuf));
		//shm_unlink(bufName);
		free(bufName);
	}
}



sharedPacketBuf * __getSharedBuffer(char * bufName){
	return hmap_get(&sharedBufMap,bufName);
}

/*
Assumes the buffer lock is held prior to call
*/
bool __PollProxyRead(sharedPacketBuf * buf) {
	if (buf->flow == HOST_TO_PROXY && buf->ack == FALSE && buf->dirty == TRUE )
		return TRUE;
	return FALSE;
}

/*
Assumes the buffer lock is held prior to call
*/
bool __PollHostRead(sharedPacketBuf * buf) {
	if (buf->flow == PROXY_TO_HOST && buf->ack == FALSE && buf->dirty == TRUE )
		return TRUE;
	return FALSE;
}

/*
Called by host/proxy to read any new available data
bufName  - specifies the name assigned to shared buffer
storeBuf - buffer to hold read data;
isProxy  - indicates if the proxy is initiating the read request

returns: number of bytes read

*/
int __bufRead(char * bufName, char * storeBuf, bool isProxy) {
	sharedPacketBuf * bufPtr = __getSharedBuffer(bufName);
	int nRead = 0;
	if(bufPtr == NULL || storeBuf == NULL)
		return BUF_NOT_INITIALIZED;

	if(bufPtr->isInit != INIT_MAGIC)
	    return 0;

	__flushBuffer(storeBuf,MAXPKTSIZE);


	if (isProxy == TRUE) {

		sem_wait(&bufPtr->lock);
		
		if(__PollProxyRead(bufPtr)) {
			memcpy(storeBuf,bufPtr->pkt,MAXPKTSIZE);
			nRead = bufPtr->dstID + 1;
			bufPtr->ack = TRUE;
			bufPtr->dirty = FALSE;
			bufPtr->pktLen = 0;
		}
		else
			nRead = 0;
		
		sem_post(&bufPtr->lock);

	}
	else{

		sem_wait(&bufPtr->lock);
		
		if(__PollHostRead(bufPtr)) {
			memcpy(storeBuf,bufPtr->pkt,MAXPKTSIZE);
			nRead = bufPtr->dstID + 1;
			bufPtr->ack = TRUE;
			bufPtr->dirty = FALSE;
			bufPtr->pktLen = 0;
		}
		else {
			nRead = 0;
		}
		sem_post(&bufPtr->lock);

	}

	return nRead;
}

/*
Called by proxy/host to write new data if space is available
bufName - name of shared buffer
data - data to be written
len  - length in bytes of data to be written
isProxy - indicates if write is performed by proxy
routeDestID - specifies the final destination of the message. Equals proxyID if written by host.
*/
int __bufWrite(char * bufName, char * data, int len, bool isProxy, uint32_t routeDestID) {
	sharedPacketBuf * bufPtr = __getSharedBuffer(bufName);
	int nWrite = 0;

	//printf("display = \n");
	//display(&sharedBufNames);
	
	if(bufPtr == NULL || data == NULL) {
		
		return BUF_NOT_INITIALIZED;
	}

    if(bufPtr->isInit != INIT_MAGIC)
	    return 0;

	assert(len > 0 && len < MAXPKTSIZE);

	if(isProxy) {

		sem_wait(&bufPtr->lock);
		
		if(__PollProxyRead(bufPtr) || __PollHostRead(bufPtr)) {
			nWrite = TEMP_ERROR; // some data is there to be read first either by proxy read thread or host read thread. so retry later.
		}
		else {
			bufPtr->flow = PROXY_TO_HOST;
			bufPtr->ack = FALSE;
			bufPtr->dirty = TRUE;
			bufPtr->dstID = routeDestID;
			__flushBuffer(bufPtr->pkt,MAXPKTSIZE);
			memcpy(bufPtr->pkt,data,len);
			bufPtr->pktLen = len;
			nWrite = len;
		}

		sem_post(&bufPtr->lock);
		

	}
	else{

		sem_wait(&bufPtr->lock);
		
		if(__PollProxyRead(bufPtr) || __PollHostRead(bufPtr)) {
			nWrite = TEMP_ERROR; // some data is there to be read first either by proxy read thread or host read thread. so retry later.
		}
		else {
			bufPtr->flow = HOST_TO_PROXY;
			bufPtr->ack = FALSE;
			bufPtr->dirty = TRUE;
			bufPtr->dstID = PROXY_NODE_ID;
			__flushBuffer(bufPtr->pkt,MAXPKTSIZE);
			memcpy(bufPtr->pkt,data,len);
			bufPtr->pktLen = len;
			nWrite = len;
		}

		sem_post(&bufPtr->lock);
	}


	return nWrite;

}

/*
Called by host/proxy
*/
int __bufOpen(char * bufName, bool isProxy) {
	
	return __addNewSharedBuffer(bufName,isProxy);
}

/*
Called by host/proxy
*/
int __closeAll() {
	__destroyAllSharedBuffers();
	return SUCCESS;
}

// python wrapper for init
static PyObject * py_init_shared_buf (PyObject * self, PyObject * args){
	__init();
	Py_RETURN_NONE; 
}

// python wrapper for bufOpen
static PyObject * py_bufOpen(PyObject * self, PyObject * args){
	char * bufName = NULL;
	int isProxy;
	int res;

	if (!PyArg_ParseTuple(args, "si", &bufName, &isProxy)) {
        Py_RETURN_NONE;
   	}

   	assert(bufName != NULL);

   	res = __bufOpen(bufName,isProxy);
   	return Py_BuildValue("i", res); 

}

// python wrapper for closeAll
static PyObject * py_closeAll(PyObject * self, PyObject * args){
   	__closeAll();
   	Py_RETURN_NONE; 
}


// python wrapper for bufread
static PyObject * py_bufRead(PyObject * self, PyObject * args){
	char * bufName = NULL;
	char storeBuf[MAXPKTSIZE];
	int isProxy;
	int res;
	__flushBuffer(storeBuf,MAXPKTSIZE);

	if (!PyArg_ParseTuple(args, "si", &bufName, &isProxy)) {
        Py_RETURN_NONE;
   	}

   	assert(bufName != NULL);

   	res = __bufRead(bufName,storeBuf,isProxy);
   	if(res > 0) {
		return Py_BuildValue("(i,s)", res-1,storeBuf);   	

   	}
	return Py_BuildValue("(i,s)", res, "");   	

}

// python wrapper for bufwrite
static PyObject * py_bufWrite(PyObject * self, PyObject * args){
	char * bufName = NULL;
	char * data = NULL;
	int isProxy;
	int dstID;
	int dataLen;
	int res;
	

	if (!PyArg_ParseTuple(args, "ssiii", &bufName, &data, &dataLen, &isProxy, &dstID)) {
        Py_RETURN_NONE;
   	}

   	assert(bufName != NULL && data != NULL && (dataLen > 0 && dataLen < MAXPKTSIZE) && dstID >= 0);

   	/*printf("bufWirte name %s\n",bufName);
   	printf("bufWrite data %s\n",data);
   	printf("bufWrite dataLen %d\n",dataLen);
   	printf("bufWrite isProxy %d\n",isProxy);
   	printf("bufWrite dstID %d\n",dstID);*/

   	res = __bufWrite(bufName,data,dataLen,isProxy,dstID);
   	
	return Py_BuildValue("i", res);   	

}


// PYTHON Module definition functions

static PyMethodDef shared_buf_methods[] = {
   { "init", py_init_shared_buf, METH_VARARGS, NULL },
   { "open", py_bufOpen, METH_VARARGS, NULL },
   { "close", py_closeAll, METH_VARARGS, NULL },
   { "read", py_bufRead, METH_VARARGS, NULL },
   { "write", py_bufWrite, METH_VARARGS, NULL }
   
};





#if PY_MAJOR_VERSION <= 2

	void initshared_buf(void)
	{
    	Py_InitModule3("shared_buf", shared_buf_methods,
                   "shared buffer");
	}


#elif PY_MAJOR_VERSION >= 3 

	static struct PyModuleDef shared_buf_definition = { 
    	PyModuleDef_HEAD_INIT,
    	"shared_buf",
    	"A Python module that mmap's a shared_buf between 2 processes",
    	-1, 
    	shared_buf_methods
	};
	PyMODINIT_FUNC PyInit_shared_buf(void)
	{
    	Py_Initialize();
	    return PyModule_Create(&shared_buf_definition);
	}

#endif


