#include "tree.h"
#include <stdio.h>
#include <stdlib.h>

void print_node(int * id, hashmap * nodes){

	node * curr_node;
	node * curr_neighbour;
	llist * out_neighbours;
	llist * in_neighbours;
	int i;
	int j;



	curr_node =  hmap_get(nodes,id);
	if(curr_node != NULL){
		printf("Id  = %d, " ,curr_node->id);
		out_neighbours = curr_node->get_out_neighbours();
		in_neighbours = curr_node->get_in_neighbours();
		printf("Out Neighbours : < ");
		for(j = 0; j < out_neighbours->size; j++){
			curr_neighbour = llist_get(out_neighbours,j);
			if(curr_neighbour != NULL)
				printf("%d ", curr_neighbour->id);
		}
		
		printf("> In Neighbours : < ");
		for(j = 0; j < in_neighbours->size; j++){
			curr_neighbour = llist_get(in_neighbours,j);
			if(curr_neighbour != NULL)
				printf("%d ", curr_neighbour->id);
		}
		printf("> \n");
	}


}

void print_node_info(node * curr_node, void * args){
	node * curr_neighbour;
	llist * out_neighbours;
	llist * in_neighbours;
	int i;
	int j;

	if(curr_node != NULL){
		printf("Id  = %d, " ,curr_node->id);
		out_neighbours = curr_node->get_out_neighbours();
		in_neighbours = curr_node->get_in_neighbours();
		printf("Out Neighbours : < ");
		for(j = 0; j < out_neighbours->size; j++){
			curr_neighbour = llist_get(out_neighbours,j);
			if(curr_neighbour != NULL)
				printf("%d ", curr_neighbour->id);
		}
		
		printf("> In Neighbours : < ");
		for(j = 0; j < in_neighbours->size; j++){
			curr_neighbour = llist_get(in_neighbours,j);
			if(curr_neighbour != NULL)
				printf("%d ", curr_neighbour->id);
		}
		printf("> \n");
	}


}

void print_edge(int * id, hashmap * edges){

	edge * curr_edge;
	curr_edge =  hmap_get(edges,id);

	if(curr_edge != NULL)
		printf("Id = %d, Src Node = %d, Dst Node = %d \n" ,curr_edge->id, curr_edge->get_src()->id, curr_edge->get_dst()->id);
}

display(tree * g){

	hashmap * nodes;
	hashmap * edges;
	

	int n_nodes;
	int n_edges;
	
	
	llist * active_nodes;
	llist * active_edges;


	node * curr_node;
	edge * curr_edge;
	node * curr_neighbour;

	nodes = g->get_nodes();
	edges = g->get_edges();

	n_nodes = g->get_n_nodes();
	n_edges = g->get_n_edges();

	active_nodes = g->get_active_nodes();
	active_edges = g->get_active_edges();
		
	printf("\n\nTree contains %d nodes and %d edges \n\n", n_nodes, n_edges);

	printf("Nodes : \n");
	llist_iterate(active_nodes,print_node,nodes);

	printf("\n\n");

	printf("Edges : \n");
	llist_iterate(active_edges,print_edge,edges);


	printf("\n");
}

int main(){

	
	tree* g = new tree();
	node  * n1 = new node(1);
	node * n2 = new node(2);
	node * n3 = new node(3);
	node * n4 = new node(4);	

	node * parent;
	llist * children;
	hashmap * nodes;

	g->set_root(n1);
	g->add_child(n1,n2);
	g->add_child(n2,n3);
	g->add_child(n1,n4);
	
	display(g);

	parent = g->get_parent(n2);
	printf("parent of %d is %d\n", n2->id,parent->id);

	children = g->get_children(n1);
	printf("children of %d are :\n", n1->id);
	llist_iterate(children,print_node_info,NULL);
	
	delete n1;
	delete n2;
	delete n3;
	delete n4;
	delete g;
	return 0;

}

