
#include <stdio.h>
#include <stdlib.h>
#include "tree.h"


tree::tree()
:graph(){
	root = NULL;
	edges_copy_list = (llist * ) malloc(sizeof(llist));
}


tree::~tree()
{	
	edge * curr_edge;
	while(edges_copy_list->size > 0){
		curr_edge = llist_pop(edges_copy_list);
		if(curr_edge != NULL)
			delete curr_edge;
	}
	free(edges_copy_list);
	
}


void tree::set_root(node * root){

	this->root = root;
	if(n_nodes == 0){
		graph::add_node(root);
		n_nodes = 1;
	}
}

void tree::add_child(node * parent, node * child){
	
	llist * in_neighbours;
	

	if(child != NULL){
		edge * new_edge = new edge(n_edges + 1,parent,child);
		in_neighbours = child->get_in_neighbours();
		if(in_neighbours->size > 0){
			delete new_edge;
			return;
		}
		graph::add_edge(new_edge);
		llist_append(edges_copy_list,new_edge);

	}
}

node * tree::get_root(){
	return this->root;
}


node * tree::get_parent(node * curr_node){

	llist * in_neighbours;
	node * parent;
	if(curr_node != NULL){
		in_neighbours = curr_node->get_in_neighbours();
		parent = llist_get(in_neighbours,0);
		return parent;
	}
	
	return NULL;		

}

llist * tree::get_children(node * curr_node){
	if(curr_node != NULL){
		return curr_node->get_out_neighbours();
	}
	return NULL;
}

node * tree::get_child_no(node * curr_node, int child_no){

	llist * out_neighbours;
	node * child;
	if(curr_node != NULL && child_no > 0){
		out_neighbours = curr_node->get_out_neighbours();
		child = llist_get(out_neighbours,child_no - 1);
		return child;
	}
	return NULL;

}

void tree::add_node(node * new_node){
	// do nothing, overridden
}

void tree::add_edge(edge * new_edge){
	// do nothing, overridden
}
