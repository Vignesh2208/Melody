#include "graph.h"


int node_equality_checker(node * node1, node * node2){
	if(node1->id == node2->id)
		return 0;
	else
		return 1;
}

int int_equality_checker(int * key1, int * key2){
	
	
	if(*key1 == *key2)
		return 0;
	else
		return 1;
	
}

node::node(int node_id){

	id = node_id;
	out_neighbours = (llist *)malloc(sizeof(llist));
	in_neighbours = (llist *)malloc(sizeof(llist));

	llist_init(out_neighbours);
	llist_init(in_neighbours);

	llist_set_equality_checker(out_neighbours,node_equality_checker);
	llist_set_equality_checker(in_neighbours,node_equality_checker);

	params = NULL;

}

void node::add_out_neighbour(node * neighbour){
	
	if(neighbour == NULL)
		return;


	int index;
	index = llist_get_pos(out_neighbours,neighbour);
	if(index < 0)
		llist_append(out_neighbours,neighbour);

}

void node::add_in_neighbour(node * neighbour){

	if(neighbour == NULL)
		return;

	int index;
	index = llist_get_pos(in_neighbours,neighbour);
	if(index < 0)
		llist_append(in_neighbours,neighbour);

}

llist * node::get_out_neighbours(){

	return out_neighbours;
}

llist * node::get_in_neighbours(){

	return in_neighbours;
}

void node::set_node_params(void * node_params){

	params = node_params;
}

void node::set_id(int id){
	this->id = id;
}

node::~node(){

	llist_destroy(in_neighbours);
	llist_destroy(out_neighbours);
	free(in_neighbours);
	free(out_neighbours);

}


void* node::get_node_params(){

	return params;
}




edge::edge(int edge_id, node * src_node, node * dst_node){

	src = src_node;
	dst = dst_node;
	params = NULL;
	id = edge_id;

}

edge::~edge(){

}


void edge::set_edge_params(void * params){
	params = params;
}

void * edge::get_edge_params(){
	return params;
}

node * edge::get_src(){

	return this->src;
}

node * edge::get_dst(){

	return this->dst;
}

void edge::set_id(int id){
	this->id = id;
}

graph::graph(){

	n_nodes = 0;
	n_edges = 0;

	nodes = (hashmap *) malloc(sizeof(hashmap));
	edges = (hashmap *) malloc(sizeof(hashmap));

	active_nodes = (llist *)malloc(sizeof(llist));
	active_edges = (llist *)malloc(sizeof(llist));

	llist_init(active_nodes);
	llist_init(active_edges);
	
	llist_set_equality_checker(active_nodes,int_equality_checker);
	llist_set_equality_checker(active_edges,int_equality_checker);

	hmap_init(nodes,"int",0);
	hmap_init(edges,"int",0);

}

graph::~graph(){

	

	hmap_destroy(nodes);
	hmap_destroy(edges);


	free(nodes);
	free(edges);

	llist_destroy(active_nodes);
	llist_destroy(active_edges);

	free(active_nodes);
	free(active_edges);

}


void graph::add_node(node * new_node){

	if(new_node == NULL)
		return;
	n_nodes ++;	
	
	node * curr_node;

	llist_remove(active_nodes,&new_node->id);
	llist_append(active_nodes,&new_node->id);

	hmap_put(this->nodes,&new_node->id,(void *)new_node);

	

}


void graph::add_edge(edge * new_edge){

	node * src_node;
	node * dst_node;

	if(new_edge == NULL)
		return;

	n_edges ++;
	

	edge * curr_edge;
	hmap_put(edges,&new_edge->id,new_edge);

	llist_remove(active_edges,&new_edge->id);
	llist_append(active_edges,&new_edge->id);
	
	
	src_node = new_edge->get_src();
	dst_node = new_edge->get_dst();	
	
	if(src_node != NULL && dst_node != NULL){
	src_node->add_out_neighbour(dst_node);
	dst_node->add_in_neighbour(src_node);

	

	if(hmap_get(nodes,&src_node->id) == NULL){
		n_nodes ++;
		llist_append(active_nodes,&src_node->id);
		hmap_put(nodes,&src_node->id,src_node);
	}	

	if(hmap_get(nodes,&dst_node->id) == NULL){
		n_nodes ++;

		llist_append(active_nodes,&dst_node->id);
		hmap_put(nodes,&dst_node->id,dst_node);
	}	

	}
}

void graph::set_node_params(int node_id, void * new_params){

	node * curr_node;
	curr_node = hmap_get(nodes,&node_id);
	if(curr_node != NULL){
		curr_node->set_node_params(new_params);
	}
}


void* graph::get_node_params(int node_id){

	node * curr_node;
	curr_node = hmap_get(nodes,&node_id);
	if(curr_node != NULL){
		return curr_node->get_node_params();
	}
	return NULL;
}

void graph::set_edge_params(int edge_id, void * new_params){

	edge * curr_edge;
	curr_edge = hmap_get(edges,&edge_id);
	if(curr_edge != NULL){
		curr_edge->set_edge_params(new_params);
	}
}


void* graph::get_edge_params(int edge_id){

	edge * curr_edge;
	curr_edge = hmap_get(edges,&edge_id);
	if(curr_edge != NULL){
		return curr_edge->get_edge_params();
	}
	return NULL;
}

node * graph::get_node(int node_id){
	return hmap_get(nodes,&node_id);
}

edge * graph::get_edge(int edge_id){
	return hmap_get(edges,&edge_id);
}

edge * graph::get_edge(node * src_node, node * dst_node){

	int i;
	if(src_node == NULL || dst_node == NULL)
		return NULL;

	edge * curr_edge;
	llist_elem * head = active_edges->head;
	
	while(head != NULL){

		curr_edge = hmap_get(edges,head->item);
		
		if(curr_edge != NULL){

			if(curr_edge->src->id == src_node->id && curr_edge->dst->id == dst_node->id)
				return curr_edge;
		}
		head = head->next;
	}

	return NULL;

}

void graph::remove_edge(node * src_node, node * dst_node){

	edge * curr_edge;
	curr_edge = get_edge(src_node,dst_node);
	
	llist * out_neighbours;
	llist * in_neighbours;

	if(curr_edge != NULL){

		
		hmap_remove(edges,&curr_edge->id);
		n_edges --;
		llist_remove(active_edges,&curr_edge->id);

		out_neighbours = src_node->get_out_neighbours();
		in_neighbours = dst_node->get_in_neighbours();
	
		llist_remove(out_neighbours,dst_node);
		llist_remove(in_neighbours,src_node);
		
	}
	else{
		out_neighbours = src_node->get_out_neighbours();
		in_neighbours = dst_node->get_in_neighbours();
	
		llist_remove(out_neighbours,dst_node);
		llist_remove(in_neighbours,src_node);
	}
}

void graph::remove_edge(edge * edge_to_rem){

	if(edge_to_rem != NULL)
	 	remove_edge(edge_to_rem->src,edge_to_rem->dst);
}

void graph::remove_edge(int edge_id){

	edge * curr_edge = hmap_get(edges,&edge_id);
	node * src_node;
	node * dst_node;
	llist * out_neighbours;
	llist * in_neighbours;

	if(curr_edge != NULL){
		
		
		src_node = curr_edge->src;
		dst_node = curr_edge->dst;

		out_neighbours = src_node->get_out_neighbours();
		in_neighbours = dst_node->get_in_neighbours();
	
		llist_remove(out_neighbours,dst_node);
		llist_remove(in_neighbours,src_node);

		hmap_remove(edges,&curr_edge->id);
		n_edges --;
		llist_remove(active_edges,&curr_edge->id);

	}
	else{
		out_neighbours = src_node->get_out_neighbours();
		in_neighbours = dst_node->get_in_neighbours();
	
		llist_remove(out_neighbours,dst_node);
		llist_remove(in_neighbours,src_node);
	}
	
}

void graph::remove_node(int node_id){

	node * curr_node = hmap_get(nodes,&node_id);
	llist * out_neighbours;
	llist * in_neighbours;
	node * curr_neighbour;
	int i;
	if(curr_node != NULL){
		out_neighbours = curr_node->get_out_neighbours();
		in_neighbours = curr_node->get_in_neighbours();
		while(out_neighbours->size > 0){
			curr_neighbour = llist_get(out_neighbours,0);
			if(curr_neighbour == NULL)
				printf("current neighbour is NULL\n");
			remove_edge(curr_node,curr_neighbour);
			
		}
	
		
		while(in_neighbours->size > 0){
			curr_neighbour = llist_get(in_neighbours,0);
			remove_edge(curr_neighbour,curr_node);
		}
		
	}
	n_nodes --;
	hmap_remove(nodes,&node_id);
	llist_remove(active_nodes,&node_id);
	

}

void graph::remove_node(node * node_to_rem){

	if(node_to_rem != NULL)
		remove_node(node_to_rem->id);
}


hashmap * graph::get_nodes(){
	return nodes;
}

hashmap * graph::get_edges(){
	return edges;
}

int graph::get_n_nodes(){
	return n_nodes;
}

int graph::get_n_edges(){
	return n_edges;
}

llist * graph::get_active_nodes(){
	return active_nodes;
}

llist * graph::get_active_edges(){
	return active_edges;
}

void graph::reset(){
	n_nodes = 0;
	n_edges = 0;
	llist_destroy(active_nodes);
	llist_destroy(active_edges);
	hmap_destroy(nodes);
	hmap_destroy(edges);

	hmap_init(nodes,"int",0);
	hmap_init(edges,"int",0);
}
