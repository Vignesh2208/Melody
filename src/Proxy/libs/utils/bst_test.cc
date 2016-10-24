#include "bst.h"
#include <stdio.h>
#include <stdlib.h>


void display(node * root){

	if(root == NULL)
		return;

	bst_elem * params;
	params = root->get_node_params();
	if(params != NULL){
		node * left = NULL;
		node * right = NULL;

		left = params->left;
		right = params->right;

		bst_elem * left_params;
		bst_elem * right_params;

		if(left != NULL && right != NULL){
			left_params = left->get_node_params();
			right_params = right->get_node_params();
			
			if(left_params == NULL)
				printf("Left params is NULL\n");

			if(right_params == NULL)
				printf("Right params is NULL\n");

			
			printf("ID : %d, key = %d, left id : %d, right id : %d, left key : %d, right key %d\n", root->id, *(int *)params->key, left->id, right->id, *(int *)left_params->key, *(int *)right_params->key);
			display(left);
			display(right);

		}
		if(left == NULL && right != NULL){
			
			right_params = right->get_node_params();
			if(right_params == NULL)
				printf("Right params is NULL\n");
			printf("ID : %d, key = %d, left id : NULL, right id :%d,  left key : NULL, right key %d\n", root->id, *(int *)params->key, right->id, *(int *)right_params->key);

			display(right);
		}

		if(left != NULL && right == NULL){

			
			left_params = left->get_node_params();

			if(left_params == NULL)
				printf("Left params is NULL\n");

			printf("ID : %d, key = %d, left id : %d, right id : NULL, left key : %d, right key :NULL\n", root->id, *(int *)params->key, left->id, *(int *)left_params->key);
			display(left);

		}
		
		if(left == NULL && right == NULL){
			
			printf("ID : %d, key = %d, left id : NULL, right id : NULL, left key : NULL, right key NULL\n",root->id,*(int *)params->key);
		}

		
	}


}


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

display_tree(tree * g){

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


	bst * t;
	t = new bst("int");

	int keys[10] = {8,4,2,3,6,7,12,9,10,-1};
	int values[10] = {10,20,30,40,50,60,70,80,90,100};
	int i =0 ;

	for(i = 0; i < 10; i++)
		t->insert(&keys[i],&values[i]);
	printf("Insertion complete\n");
	display(t->get_root());	

	int * val = t->get(&keys[4]);
	printf("Val = %d, key = %d\n", *val, keys[4]);


	display_tree(t->get_tree());
	printf("Number of nodes left = %d\n", t->get_tree()->get_n_nodes());
	printf("\n\nFirst remove. key = %d\n\n", keys[4]);
	t->remove(&keys[4]);
	display(t->get_root());
	printf("Number of nodes left = %d\n", t->get_tree()->get_n_nodes());


	printf("\n\nSecond remove. key = %d\n\n", keys[0]);
	t->remove(&keys[0]);
	display(t->get_root());
	printf("Number of nodes left = %d\n", t->get_tree()->get_n_nodes());	


	printf("\n\nThird remove. key = %d\n\n", keys[5]);
	t->remove(&keys[5]);
	display(t->get_root());
	printf("Number of nodes left = %d\n", t->get_tree()->get_n_nodes());


	printf("\n\nFourth remove. key = %d\n\n", keys[2]);
	t->remove(&keys[2]);
	display(t->get_root());
	printf("Number of nodes left = %d\n", t->get_tree()->get_n_nodes());


	printf("\n\nFifth remove. key = %d\n\n", keys[1]);
	t->remove(&keys[1]);
	display(t->get_root());
	printf("Number of nodes left = %d\n", t->get_tree()->get_n_nodes());

	printf("\n\nSixth remove. key = %d\n\n", keys[6]);
	t->remove(&keys[6]);
	display(t->get_root());
	printf("Number of nodes left = %d\n", t->get_tree()->get_n_nodes());


	printf("\n\nSeventh remove. key = %d\n\n", keys[7]);
	t->remove(&keys[7]);
	display(t->get_root());
	printf("Number of nodes left = %d\n", t->get_tree()->get_n_nodes());

	printf("\n\nEigth remove. key = %d\n\n", keys[8]);
	t->remove(&keys[8]);
	display(t->get_root());
	printf("Number of nodes left = %d\n", t->get_tree()->get_n_nodes());


	printf("\n\nNineth remove. key = %d\n\n", keys[9]);
	t->remove(&keys[9]);
	display(t->get_root());
	printf("Number of nodes left = %d\n", t->get_tree()->get_n_nodes());


	printf("\n\nTenth remove. key = %d\n\n", keys[3]);
	t->remove(&keys[3]);
	display(t->get_root());
	printf("Number of nodes left = %d\n", t->get_tree()->get_n_nodes());


	printf("Inserting...\n");
	for(i = 0; i < 10; i++)
		t->insert(&keys[i],&values[i]);
	printf("Insertion complete\n");
	display(t->get_root());
	
	

	printf("\n\ncleaning up...\n\n");
	delete t;
	return 0;
}
