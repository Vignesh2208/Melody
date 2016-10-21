#ifndef __AVL_H
#define __AVL_H

#include "tree.h"
#include <stdio.h>
#include <stdlib.h>
#include <cstring>

typedef struct avl_elem_struct {

	void * key;
	void * value;
	int bf;
	int left_size;
	int right_size;
	node * parent;
	node * left;
	node * right;

}
avl_elem;

typedef int (*avl_key_comparer) (void * key1, void * key2);


class avl
{
	protected :
		tree * avl_tree;
		avl_key_comparer compare;
		void insert_recurse(node * curr_node,void * key, void * value);
		void* search_recurse(node * curr_node, void * key);
		void rotate_right(node * curr_node);
		void rotate_left(node * curr_node);
		void balance_up(node * curr_node);
		node * tree_min(node * curr_node);
		node * tree_max(node * curr_node);
	public :

		avl(char * type = "default");
		~avl();
		void set_key_comparer(int (*key_comparer)(void * key1, void * key2));
		void insert(void * key,void * value);
		void * get(void * key);
		int  search(void * key);
		void remove(void * key);
		node * get_root();
		tree * get_tree();
		

};

#endif
