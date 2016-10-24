#include "bst.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int default_bst_key_comparer(void * key1, void * key2){

	if(key1 == key2)
		return 0;
	if(key1 < key2)
		return -1;

	return 1;
}


int integer_key_comparer(int * key1, int * key2){

	if(*key1 == *key2)
		return 0;
	if(*key1 < *key2)
		return -1;

	return 1;
}


int string_key_comparer(char * key1, char * key2){

	return strcmp(key1,key2);
}


bst::bst(char * type = "default"){

	if(strcmp(type,"int") == 0)
		compare = integer_key_comparer;
	else
		if(strcmp(type,"string") == 0)
			compare = string_key_comparer;
		else
			compare = default_bst_key_comparer;

	
	bst_tree = new tree();

}



	
void destroy_node(int * id, hashmap * nodes){

	node * curr_node = NULL;
	if(nodes != NULL)
		curr_node = hmap_get(nodes,id);

	if(curr_node != NULL){
				
		bst_elem * temp = curr_node->get_node_params();
		if(temp != NULL)		
			free(temp);		
		hmap_remove(nodes,id);
		delete curr_node;
	}

	

}

bst::~bst(){

	node * root;
	hashmap * nodes = bst_tree->get_nodes();
	llist * active_nodes = bst_tree->get_active_nodes();
	llist_iterate(active_nodes,destroy_node,nodes);	
	delete bst_tree;

}

void bst::set_key_comparer(int (*key_comparer)(void * key1, void * key2)){
	compare = key_comparer;
}

void bst::insert_recurse(node * curr_node, void * key, void * value){
	node * new_node ;
	bst_elem * new_elem;
	bst_elem * curr_elem = curr_node->get_node_params();
	if(curr_elem != NULL){

		if(compare(key,curr_elem->key) == 0){ // update key
			curr_elem->value = value;
			return;	
		}
		
		if(compare(key,curr_elem->key) > 0){ // key > curr_elem->key
			if(curr_elem->right == NULL){
				new_node = new node(bst_tree->get_n_nodes() + 1);
				new_elem = (bst_elem *) malloc(sizeof(bst_elem));
				new_elem->left = NULL;
				new_elem->right = NULL;
				new_elem->key = key;
				new_elem->value = value;
				
				new_node->set_node_params(new_elem);
				curr_elem->right = new_node;
				bst_tree->add_child(curr_node, new_node);
				return;
				
			}

			bst::insert_recurse(curr_elem->right, key,value);
			return;
		}
		else{

			if(curr_elem->left == NULL){
				new_node = new node(bst_tree->get_n_nodes() + 1);
				new_elem = (bst_elem *) malloc(sizeof(bst_elem));
				new_elem->left = NULL;
				new_elem->right = NULL;
				new_elem->key = key;
				new_elem->value = value;				
				new_node->set_node_params(new_elem);
				curr_elem->left = new_node;
				bst_tree->add_child(curr_node, new_node);
				return;
				
			}

			bst::insert_recurse(curr_elem->left, key,value);
			return;

		}	
		

	}
	else{ // should never happen
		curr_elem->key = key;
		curr_elem->value = value;

	}

}

void bst::insert(void * key, void * value){

	int n_nodes = bst_tree->get_n_nodes();
	bst_elem * new_elem;
	node * new_node;
	if(bst_tree->get_root() == NULL){
		new_elem = (bst_elem *) malloc(sizeof(bst_elem));
		new_elem->left = NULL;
		new_elem->right = NULL;
		new_elem->key = key;
		new_elem->value = value;
		new_node = new node(n_nodes + 1);
		new_node->set_node_params(new_elem);
		bst_tree->set_root(new_node);
		return;
	}

	insert_recurse(bst_tree->get_root(), key, value);
	

	
}

void* bst::search_recurse(node * curr_node, void * key){

	if(curr_node == NULL)
		return NULL;

	bst_elem * curr_params;
	curr_params = curr_node->get_node_params();

	if(curr_params == NULL)
		return NULL;

	if(compare(curr_params->key,key) == 0){
		return curr_node;
	}

	if(compare(key,curr_params->key) > 0)
		return search_recurse(curr_params->right,key);

	return search_recurse(curr_params->left,key);
}

void * bst::get(void * key){
	
	node * dst_node = search_recurse(bst_tree->get_root(),key);

	if(dst_node == NULL)
		return NULL;
	else{
		bst_elem * req_elem = dst_node->get_node_params();
		return req_elem->value;
	}	
}

int bst::search(void * key){

	if(search_recurse(bst_tree->get_root(), key) == NULL)
		return 0;
	else
		return 1;
}

node * bst::get_root(){

	return bst_tree->get_root();
}

tree * bst::get_tree(){
	return bst_tree;
}
node * bst::tree_min(node * curr_node){

	if(curr_node == NULL)
		return NULL;

	bst_elem * temp;
	temp = curr_node->get_node_params();
	if(temp->left == NULL )
		return curr_node;

	return tree_min(temp->left);
}

node * bst::tree_max(node * curr_node){
	
	if(curr_node == NULL)
		return NULL;

	bst_elem * temp;
	temp = curr_node->get_node_params();
	if(temp->right == NULL )
		return curr_node;

	return tree_min(temp->right);
}

void bst::remove(void * key){
	
	node * dst_node = search_recurse(bst_tree->get_root(),key);
	node * parent;
	bst_elem * temp;
	bst_elem * node_elem;
	int j;
	if(dst_node == NULL)
		return;
	else{
		node_elem = dst_node->get_node_params();
		parent = bst_tree->get_parent(dst_node);
		if(node_elem->left == NULL && node_elem->right == NULL){ // leaf. remove it.
		
			free(node_elem);
			if(parent != NULL){
				temp = parent->get_node_params();
				if(temp->right == dst_node)
					temp->right = NULL;
				else
					temp->left = NULL;

				bst_tree->remove_node(dst_node);
				delete dst_node;
				return;
			}

			bst_tree->remove_node(dst_node);
			bst_tree->set_root(NULL);
			bst_tree->reset();
			delete dst_node;
			return;


		}
		else{

			if(node_elem->left == NULL && node_elem->right != NULL){
				
				bst_tree->remove_node(dst_node);
				if(parent == NULL){
					
					bst_tree->set_root(node_elem->right);
					free(node_elem);
					delete dst_node;
					return;
				}

				temp = parent->get_node_params();
				if(temp->right == dst_node){
					temp->right = node_elem->right;
					if(temp->right != NULL){
						bst_tree->add_child(parent,temp->right);
					}			
					free(node_elem);
					delete dst_node;
					return;
				}

				temp->left = node_elem->right;				
				if(node_elem->right != NULL)
					bst_tree->add_child(parent,node_elem->right);
				free(node_elem);
				delete dst_node;
				return;

			}

			if(node_elem->left != NULL && node_elem->right == NULL){
				bst_tree->remove_node(dst_node);
				if(parent == NULL){
					
					bst_tree->set_root(node_elem->left);
				
					free(node_elem);
					delete dst_node;
					return;
				}

				temp = parent->get_node_params();
				if(temp->right == dst_node){
					temp->right = node_elem->left;				
					if(node_elem->left != NULL)
						bst_tree->add_child(parent,node_elem->left);	
					free(node_elem);
					delete dst_node;
					return;
				}

				temp->left = node_elem->left;

				
				if(node_elem->left != NULL)
					bst_tree->add_child(parent,node_elem->left);
				free(node_elem);
				delete dst_node;
				return;

			}

			// both != NULL

			// find successor

			node * successor = tree_min(node_elem->right);
			bst_elem * succ_elem;
			succ_elem = successor->get_node_params();
			if(successor != NULL){
				node * successor_parent;
				successor_parent = bst_tree->get_parent(successor);
				if(successor_parent != NULL){
					
					bst_tree->remove_node(successor);
					bst_tree->remove_node(dst_node);
					bst_elem * succ_parent_elem = successor_parent->get_node_params();
					
					if(successor_parent != dst_node){
	
						if(succ_parent_elem->left == successor){							
							succ_parent_elem->left = succ_elem->right;							
						}
						else
							succ_parent_elem->right = succ_elem->right; // should never happen
						if(succ_elem->right != NULL && successor_parent != NULL)
							bst_tree->add_child(successor_parent,succ_elem->right);	

					}
					
					
					
				
					
				}
				else{

					printf("ERROR during remove. successor parent is NULL\n");
					return;
				}

				
				if(successor == node_elem->right){ // successor == dst_node->right
					
					if(parent == NULL){
						// root = successor
						succ_elem->left = node_elem->left;
						bst_tree->set_root(successor);
						bst_tree->add_child(successor, node_elem->left);
						if(succ_elem->right != NULL)
							bst_tree->add_child(successor, succ_elem->right);

						free(node_elem);
						delete dst_node;
						return;
					}
					temp = parent->get_node_params();
					succ_elem->left = node_elem->left;
					if(temp->left == dst_node)
						temp->left = successor;
					else
						temp->right = successor;					
					bst_tree->add_child(successor,node_elem->left);
					bst_tree->add_child(parent,successor);
					if(succ_elem->right != NULL){
						bst_tree->add_child(successor, succ_elem->right);
					}

					free(node_elem);
					delete dst_node;
					return;

					
				}

				// successor != dst_node->right;
						
				       if(parent == NULL){
						// root = successor
						succ_elem->left = node_elem->left;
						succ_elem->right = node_elem->right;
						
						bst_tree->set_root(successor);
						
						bst_tree->add_child(successor, node_elem->left);
						bst_tree->add_child(successor,node_elem->right);

						free(node_elem);
						delete dst_node;
						return;
					}

					succ_elem->left = node_elem->left;					
					succ_elem->right = node_elem->right;
					temp = parent->get_node_params();
					if(temp->left == dst_node)
						temp->left = successor;
					else
						temp->right = successor;

					bst_tree->add_child(parent,successor);
					bst_tree->add_child(successor,node_elem->left);
					bst_tree->add_child(successor,node_elem->right);

					free(node_elem);
					delete dst_node;
					return;
				

			}
			// else should never happen
			printf("ERROR during remove. successor is NULL\n");
			return;


		}


	}	



	
}
