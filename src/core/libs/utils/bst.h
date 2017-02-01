#ifndef __BST_H
#define __BST_H

#include "tree.h"
#include <stdio.h>
#include <stdlib.h>
#include <cstring>

typedef struct bst_elem_struct {

	void * key;
	void * value;
	node * left;
	node * right;

}
bst_elem;

typedef int (*bst_key_comparer) (void * key1, void * key2);


class bst
{
	protected :
		tree * bst_tree;
		bst_key_comparer compare;
		void insert_recurse(node * curr_node,void * key, void * value);
		void* search_recurse(node * curr_node, void * key);
		//void destroy_node(int * id, hashmap * nodes);
		node * tree_min(node * curr_node);
		node * tree_max(node * curr_node);
	public :

		bst(char * type = "default");
		~bst();
		void set_key_comparer(int (*key_comparer)(void * key1, void * key2));
		void insert(void * key,void * value);
		void * get(void * key);
		int  search(void * key);
		void remove(void * key);
		node * get_root();
		tree * get_tree();
		

};

#endif
