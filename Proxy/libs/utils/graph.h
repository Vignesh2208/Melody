#ifndef __GRAPH_H

#define __GRAPH_H
#include "linkedlist.h"
#include "hashmap.h"
#include <stdio.h>
#include <stdlib.h>

class node
{
	public :
		node(int id);
		~node();
		
		void add_out_neighbour(node * neighbour);
		void add_in_neighbour(node * neighbour);
		void set_node_params(void * param);
		void * get_node_params();
		void set_id(int id);
		llist * get_out_neighbours();
		llist * get_in_neighbours();
		

		int id;
		void * params;
		llist * out_neighbours;
		llist * in_neighbours;

		


};

class edge  
{

	public :
		edge(int id, node * src, node * dst);
		~edge();
		
		node * src;
		node * dst;
		void * params;
		int id;
		void set_edge_params(void * param);
		void * get_edge_params();
		node * get_src();
		node * get_dst();
		void set_id(int id);		

};


class graph 
{

	protected :
		int n_nodes;
		int n_edges;
		llist * active_nodes;
		llist * active_edges;

		hashmap * edges;
		hashmap * nodes;
	public :
		graph();
		~graph();

		

		
		virtual void   add_node(node * new_node);
		virtual void   add_edge(edge * new_edge);
		void   set_node_params(int node_id, void * new_params);
		void * get_node_params(int node_id);
		void   set_edge_params(int edge_id, void * new_params);
		void * get_edge_params(int edge_id);
		node * get_node(int node_id);
		edge * get_edge(int edge_id);
		edge * get_edge(node * src_node, node * dst_node);
		void   remove_edge(node * src_node, node * dst_node);
		void   remove_edge(edge * edge_to_rem);
		void   remove_edge(int edge_id);
		void   remove_node(int node_id);
		void   remove_node(node * node_to_rem);
		hashmap * get_nodes();
		hashmap * get_edges();
		llist * get_active_nodes();
		llist * get_active_edges();
			int get_n_nodes();
		int get_n_edges();
		void reset();

};


#endif
