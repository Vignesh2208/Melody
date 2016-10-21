

#include <stdio.h>
#include <stdlib.h>

typedef int (*comparefn) (void * elem1, void * elem2);
typedef void (*acton) (void * item, void * args); 

typedef struct skiplist_elem_struct{

	skiplist_elem_struct * up;
	skiplist_elem_struct * down;
	skiplist_elem_struct * next;
	void * item; 

}
skipl_elem;


class skiplist 
{

	protected :

		int M;
		char type[100];
		comparefn compare;
		skipl_elem ** head_ptrs;

	public :
		skiplist(int M, char * type = "int");
		~skiplist();
		void set_compare_fn(int (*comparer)(void * e1, void * e2));
		void insert(void * item);
		int exists(void * item);
		void iterate(void (*acton_fn)(void * item, void * args));				
		skipl_elem ** get_head_ptrs();
		int get_n_leves();


};
