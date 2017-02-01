#ifndef __TREE_H

#define __TREE_H

#include "graph.h"
#include <stdio.h>
#include <stdlib.h>

class graph;

class tree : public graph
{
	private :
		llist * edges_copy_list;

	public :
		tree();
		~tree();
	
		node * root;


		void set_root(node * root);
		void add_child(node * parent, node * child);
		node * get_root();
		node * get_parent(node * curr_node);
		llist * get_children(node * curr_node);
		node * get_child_no(node * curr_node, int child_no);
		void add_node(node * new_node);
		void add_edge(edge * new_edge);
};

#endif
