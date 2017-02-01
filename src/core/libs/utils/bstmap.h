#include "bst.h"
#include <stdio.h>
#include <stdlib.h>

typedef int (*key_hash_fn)(void * key);
typedef int (*compare_fn)(void * elem1, void * elem2);

class bstmap 
{

	protected :
		bst ** bstarray;
		int size;
		llist * active_keys;
		int n_removed;
		key_hash_fn key_hash;
		int * initialized;
		char * type;
		compare_fn compare;
		int is_compare_fn_set;
	
	public :

		bstmap(char * type = "default", int size = 0);
		~bstmap();
		
		void set_key_comparer(int (*compare_fn)(void * elem1, void * elem2));
		void * get(void *key);
		void put(void * key, void * value);
		void remove(void * key);
		int exists(void * key);
		llist * keys();
		


};
