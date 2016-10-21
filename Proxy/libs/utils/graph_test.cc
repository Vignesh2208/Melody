#include "graph.h"
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

void print_edge(int * id, hashmap * edges){

	edge * curr_edge;
	curr_edge =  hmap_get(edges,id);

	if(curr_edge != NULL)
		printf("Id = %d, Src Node = %d, Dst Node = %d \n" ,curr_edge->id, curr_edge->get_src()->id, curr_edge->get_dst()->id);
}

display( graph * g){

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
		
	printf("\n\nCurrent Graph contains %d nodes and %d edges \n\n", n_nodes, n_edges);

	printf("Nodes : \n");
	llist_iterate(active_nodes,print_node,nodes);

	printf("\n\n");

	printf("Edges : \n");
	llist_iterate(active_edges,print_edge,edges);


	printf("\n");
}

int main(){

	
	graph * g = new graph();
	node  * n1 = new node(1);
	node * n2 = new node(2);
	node * n3 = new node(3);
	
	edge * e1 = new edge(1,n1,n2);
	edge * e2 = new edge(2,n1,n3);
	edge * e3 = new edge(3,n2,n1);

	g->add_node(n1);
	g->add_node(n2);
	g->add_node(n3);

	g->add_edge(e2);
	g->add_edge(e1);

	

	display(g);

	g->remove_node(n2);

	display(g);


	g->add_node(n2);
	g->add_edge(e1);
	g->add_edge(e3);
	display(g);
	
	delete n1;
	delete n2;
	delete n3;
	delete e1;
	delete e2;
	delete e3;
	delete g;
	
	return 0;

}

