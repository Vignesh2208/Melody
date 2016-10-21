#include "avl.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int default_avl_key_comparer(void * key1, void * key2){

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


avl::avl(char * type = "default"){

	if(strcmp(type,"int") == 0)
		compare = integer_key_comparer;
	else
		if(strcmp(type,"string") == 0)
			compare = string_key_comparer;
		else
			compare = default_avl_key_comparer;

	
	avl_tree = new tree();

}



	
void destroy_node(int * id, hashmap * nodes){

	node * curr_node = NULL;
	if(nodes != NULL)
		curr_node = hmap_get(nodes,id);

	if(curr_node != NULL){
				
		avl_elem * temp = curr_node->get_node_params();
		if(temp != NULL)		
			free(temp);		
		hmap_remove(nodes,id);
		delete curr_node;
	}

	

}

avl::~avl(){

	node * root;
	hashmap * nodes = avl_tree->get_nodes();
	llist * active_nodes = avl_tree->get_active_nodes();
	llist_iterate(active_nodes,destroy_node,nodes);	
	delete avl_tree;

}

void avl::rotate_right(node * curr_node){

	
	avl_elem * curr_node_elem;
	avl_elem * parent_node_elem;
	avl_elem * pparent_node_elem;



	if(curr_node != NULL && ((avl_elem *) curr_node->get_node_params())->parent != NULL && ((avl_elem *) ((avl_elem *)curr_node->get_node_params())->parent->get_node_params())->left == curr_node){
		
		node * parent_node = ((avl_elem *)curr_node->get_node_params())->parent;
		node * pparent = ((avl_elem *) parent_node->get_node_params())->parent;
		parent_node_elem = parent_node->get_node_params();
		curr_node_elem = curr_node->get_node_params();
		

		if(pparent != NULL){

			
			
			pparent_node_elem = pparent->get_node_params();
			pparent_node_elem->left = ((pparent_node_elem->left == parent_node) ? curr_node : pparent_node_elem->left) ;
			pparent_node_elem->right = ((pparent_node_elem->right == parent_node) ? curr_node : pparent_node_elem->right) ;
			//printf("Pparent key = %d\n", *(int *) pparent_node_elem->key);

		
		}
		
		curr_node_elem->parent = pparent;

		if(curr_node_elem->right != NULL){
		((avl_elem *) curr_node_elem->right->get_node_params())->parent = parent_node;
		//printf("Not NULL\n");
		}
		parent_node_elem->left = curr_node_elem->right;

		curr_node_elem->right = parent_node;
		parent_node_elem->parent = curr_node;

		parent_node_elem->left_size = curr_node_elem->right_size;
		parent_node_elem->bf = parent_node_elem->left_size - parent_node_elem->right_size;
		curr_node_elem->right_size = (parent_node_elem->left_size > parent_node_elem->right_size ? parent_node_elem->left_size : parent_node_elem->right_size ) + 1;
		curr_node_elem->bf = curr_node_elem->left_size - curr_node_elem->right_size;

		if(curr_node_elem->parent == NULL)
			avl_tree->set_root(curr_node);
		


	}

}


void avl::rotate_left(node * curr_node){
	

	avl_elem * curr_node_elem;
	avl_elem * parent_node_elem;
	avl_elem * pparent_node_elem;



	if(curr_node != NULL && ((avl_elem *) curr_node->get_node_params())->parent != NULL && ((avl_elem *) ((avl_elem *)curr_node->get_node_params())->parent->get_node_params())->right == curr_node){
		
		node * parent_node = ((avl_elem *) curr_node->get_node_params())->parent;
		node * pparent = ((avl_elem *) parent_node->get_node_params())->parent;
		parent_node_elem = parent_node->get_node_params();
		curr_node_elem = curr_node->get_node_params();
		

		if(pparent != NULL){
			

			pparent_node_elem = pparent->get_node_params();
			pparent_node_elem->left = ((pparent_node_elem->left == parent_node) ? curr_node : pparent_node_elem->left) ;
			pparent_node_elem->right = ((pparent_node_elem->right == parent_node) ? curr_node : pparent_node_elem->right) ;

			//printf("Pparent key = %d\n", *(int *) pparent_node_elem->key);			

		
		}
		
		curr_node_elem->parent = pparent;

		if(curr_node_elem->left != NULL)
		((avl_elem *) curr_node_elem->left->get_node_params())->parent = parent_node;
		parent_node_elem->right = curr_node_elem->left;

		curr_node_elem->left = parent_node;
		parent_node_elem->parent = curr_node;

		parent_node_elem->right_size = curr_node_elem->left_size;
		parent_node_elem->bf = parent_node_elem->left_size - parent_node_elem->right_size;
		curr_node_elem->left_size = (parent_node_elem->left_size > parent_node_elem->right_size ? parent_node_elem->left_size : parent_node_elem->right_size ) + 1;
		curr_node_elem->bf = curr_node_elem->left_size - curr_node_elem->right_size;

		if(curr_node_elem->parent == NULL)
			avl_tree->set_root(curr_node);
		


	}

}

/*
void avl::balance_down(node * curr_node){

	if(curr_node != NULL){
		avl_elem * curr_elem = curr_node->get_node_params();
		avl_elem * right_elem = ((curr_elem->right != NULL) ? curr_elem->right->get_node_params() : NULL);
		avl_elem * left_elem = ((curr_elem->left != NULL) ? curr_elem->left->get_node_params() : NULL);
		
		if(right_elem != NULL && abs(right_elem->bf) >= 2)
			balance_down(curr_elem->right)

		if(left_elem != NULL && abs(left_elem->bf) >= 2)
			balance_down(curr_elem->left);

		right_elem = ((curr_elem->right != NULL) ? curr_elem->right->get_node_params() : NULL);
		left_elem = ((curr_elem->left != NULL) ? curr_elem->left->get_node_params() : NULL);

		if(curr_elem != NULL && abs(curr_elem->bf) >= 2){
			

			if(curr_elem->bf <= -2 && right_elem != NULL){
				// right-left
				if(right_elem->bf == 1){
					rotate_right(curr_node->right->left);
					rotate_left(curr_node->right);
				}
				else{
				// right-right
					rotate_left(curr_node->right);
				}

			}			
			
			if(curr_elem->bf >= 2 && left_elem != NULL){
				if(left_elem->bf == -1){
					// left-right
					rotate_left(curr_node->left->right);
					rotate_right(curr_node->left);
			
				}
				else{
					// left-left
					rotate_left(curr_node->left);
				}
			}
		}

		
	}
	

}
*/

void avl::balance_up(node * curr_node){

	if(curr_node != NULL){
		avl_elem * curr_elem = curr_node->get_node_params();
		avl_elem * right_elem = ((curr_elem->right != NULL) ? curr_elem->right->get_node_params() : NULL);
		avl_elem * left_elem = ((curr_elem->left != NULL) ? curr_elem->left->get_node_params() : NULL);
		node * parent;
		avl_elem * new_right_elem ;
		avl_elem * new_left_elem;
		

		if(left_elem != NULL){

			curr_elem->left_size = (left_elem->left_size > left_elem->right_size ? left_elem->left_size : left_elem->right_size) + 1;
		}
		else
			curr_elem->left_size = 0;

		if(right_elem != NULL){

			curr_elem->right_size = (right_elem->left_size > right_elem->right_size ? right_elem->left_size : right_elem->right_size) + 1;
		}
		else
			curr_elem->right_size = 0;

		curr_elem->bf = curr_elem->left_size - curr_elem->right_size;
		/*printf("Balancing Key = %d, bf = %d\n",*(int *)curr_elem->key, curr_elem->bf);
		if(right_elem == NULL && left_elem == NULL)
		printf("Finished key = %d, bf = %d, old_left = NULL, old_right = NULL\n", *(int *) curr_elem->key,curr_elem->bf);
		else
			if(right_elem == NULL)
			printf("Finished key = %d, bf = %d, old_left = %d, old_right = NULL\n", *(int *) curr_elem->key,curr_elem->bf,*(int *) left_elem->key);
			else
				if(left_elem == NULL)
				printf("Finished key = %d, bf = %d, old_left = NULL, old_right = %d\n", *(int *) curr_elem->key,curr_elem->bf,*(int *)right_elem->key);
				else
				printf("Finished key = %d, bf = %d, old_left = %d, old_right = %d\n", *(int *) curr_elem->key,curr_elem->bf,*(int *) left_elem->key, *(int *)right_elem->key);
		*/
		parent = curr_elem->parent;
		
		if(curr_elem != NULL && abs(curr_elem->bf) >= 2){
			

			if(curr_elem->bf <= -2 && right_elem != NULL){
				// right-left
				if(right_elem->bf == 1){
					//printf("Balancing Key = %d right-left\n",*(int *)curr_elem->key);
					rotate_right(right_elem->left);
					rotate_left(curr_elem->right);
				}
				else{
				// right-right
					//printf("Balancing Key = %d right-right\n",*(int *)curr_elem->key);
					rotate_left(curr_elem->right);
				}

			}			
			
			if(curr_elem->bf >= 2 && left_elem != NULL){
				if(left_elem->bf == -1){
					// left-right
					//printf("Balancing Key = %d left-right\n",*(int *)curr_elem->key);
					rotate_left(left_elem->right);
					rotate_right(curr_elem->left);
			
				}
				else{
					// left-left
					//printf("Balancing Key = %d left-left\n",*(int *)curr_elem->key);
					rotate_right(curr_elem->left);
				}
			}
		}

		/*new_right_elem = ((curr_elem->right != NULL) ? curr_elem->right->get_node_params() : NULL);
		new_left_elem = ((curr_elem->left != NULL) ? curr_elem->left->get_node_params() : NULL);

		if(new_right_elem == NULL && new_left_elem == NULL)
		printf("Finished key = %d, bf = %d, new_left = NULL, new_right = NULL\n", *(int *) curr_elem->key,curr_elem->bf);
		else
			if(new_right_elem == NULL)
			printf("Finished key = %d, bf = %d, new_left = %d, new_right = NULL\n", *(int *) curr_elem->key,curr_elem->bf,*(int *) new_left_elem->key);
			else
				if(new_left_elem == NULL)
				printf("Finished key = %d, bf = %d, new_left = NULL, new_right = %d\n", *(int *) curr_elem->key,curr_elem->bf,*(int *)new_right_elem->key);
				else
				printf("Finished key = %d, bf = %d, new_left = %d, new_right = %d\n", *(int *) curr_elem->key,curr_elem->bf,*(int *) new_left_elem->key, *(int *)new_right_elem->key);
		*/
		if(curr_elem != NULL){
			//printf("Moving to parent\n");
			balance_up(parent);

		}

		
	}
	

}


void avl::set_key_comparer(int (*key_comparer)(void * key1, void * key2)){
	compare = key_comparer;
}

void avl::insert_recurse(node * curr_node, void * key, void * value){
	node * new_node ;
	avl_elem * new_elem;
	avl_elem * curr_elem = curr_node->get_node_params();
	if(curr_elem != NULL){

		if(compare(key,curr_elem->key) == 0){ // update key
			curr_elem->value = value;
			return ((curr_elem->left_size > curr_elem->right_size ) ? curr_elem->left_size : curr_elem->right_size) + 1;	
		}
		
		if(compare(key,curr_elem->key) > 0){ // key > curr_elem->key



			if(curr_elem->right == NULL){
				new_node = new node(avl_tree->get_n_nodes() + 1);
				new_elem = (avl_elem *) malloc(sizeof(avl_elem));
				new_elem->left = NULL;
				new_elem->right = NULL;
				new_elem->parent = curr_node;
				new_elem->left_size = 0;
				new_elem->right_size = 0;
				new_elem->bf = 0;
				new_elem->key = key;
				new_elem->value = value;
				
				new_node->set_node_params(new_elem);
				curr_elem->right = new_node;
				avl_tree->add_child(curr_node, new_node);
				//printf("END : *key = %d, *value = %d, curr_key = %d\n",*(int *) key, *(int *) value, *(int *)curr_elem->key);
				balance_up(curr_node);
				//printf("Finished balancing\n");
				
				return;
				
			}
			//printf("Right tree : curr_key = %d\n\n",*(int *) curr_elem->key);
			avl::insert_recurse(curr_elem->right, key,value);
			//curr_elem->bf = curr_elem->left_size - curr_elem->right_size;
			//balance_down(curr_node);
			//return ((curr_elem->left_size > curr_elem->right_size ) ? curr_elem->left_size : curr_elem->right_size) + 1;
			return;
		}
		else{



			if(curr_elem->left == NULL){
				new_node = new node(avl_tree->get_n_nodes() + 1);
				new_elem = (avl_elem *) malloc(sizeof(avl_elem));
				new_elem->left = NULL;
				new_elem->right = NULL;
				new_elem->parent = curr_node;
				new_elem->left_size = 0;
				new_elem->right_size = 0;
				new_elem->bf = 0;
				new_elem->key = key;
				new_elem->value = value;				
				new_node->set_node_params(new_elem);
				curr_elem->left = new_node;
				avl_tree->add_child(curr_node, new_node);
				//printf("END : *key = %d, *value = %d, curr_key = %d\n",*(int *) key, *(int *) value, *(int *) curr_elem->key);
				
				balance_up(curr_node);
				
				return;
				
			}
			//printf("Left tree : curr_key = %d\n\n",*(int *) curr_elem->key);
			avl::insert_recurse(curr_elem->left, key,value);
			//curr_elem->bf = curr_elem->left_size - curr_elem->right_size;
			//balance_down(curr_node);

			//return ((curr_elem->left_size > curr_elem->right_size ) ? curr_elem->left_size : curr_elem->right_size) + 1;
			return;


		}	
		

	}
	else{ // should never happen
		curr_elem->key = key;
		curr_elem->value = value;
		//return ((curr_elem->left_size > curr_elem->right_size ) ? curr_elem->left_size : curr_elem->right_size) + 1;
		return;
	}

}

void avl::insert(void * key, void * value){

	int n_nodes = avl_tree->get_n_nodes();
	avl_elem * new_elem;
	node * new_node;
	if(avl_tree->get_root() == NULL){
		new_elem = (avl_elem *) malloc(sizeof(avl_elem));
		new_elem->left = NULL;
		new_elem->right = NULL;
		new_elem->parent = NULL;
		new_elem->left_size = 0;
		new_elem->right_size = 0;
		new_elem->key = key;
		new_elem->value = value;
		new_elem->bf = 0;
		new_node = new node(n_nodes + 1);
		new_node->set_node_params(new_elem);
		avl_tree->set_root(new_node);
		return;
	}

	//printf("Inserting %d\n",*(int *) key);

	insert_recurse(avl_tree->get_root(), key, value);
	

	
}

void* avl::search_recurse(node * curr_node, void * key){

	if(curr_node == NULL)
		return NULL;

	avl_elem * curr_params;
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

void * avl::get(void * key){
	
	node * dst_node = search_recurse(avl_tree->get_root(),key);

	if(dst_node == NULL)
		return NULL;
	else{
		avl_elem * req_elem = dst_node->get_node_params();
		return req_elem->value;
	}	
}

int avl::search(void * key){

	if(search_recurse(avl_tree->get_root(), key) == NULL)
		return 0;
	else
		return 1;
}

node * avl::get_root(){

	return avl_tree->get_root();
}

tree * avl::get_tree(){
	return avl_tree;
}
node * avl::tree_min(node * curr_node){

	if(curr_node == NULL)
		return NULL;

	avl_elem * temp;
	temp = curr_node->get_node_params();
	if(temp->left == NULL )
		return curr_node;

	return tree_min(temp->left);
}

node * avl::tree_max(node * curr_node){
	
	if(curr_node == NULL)
		return NULL;

	avl_elem * temp;
	temp = curr_node->get_node_params();
	if(temp->right == NULL )
		return curr_node;

	return tree_min(temp->right);
}

void avl::remove(void * key){
	
	node * dst_node = search_recurse(avl_tree->get_root(),key);
	node * parent;
	avl_elem * temp;
	avl_elem * node_elem;
	avl_elem * child_elem;
	int j;
	if(dst_node == NULL)
		return;
	else{
		node_elem = dst_node->get_node_params();
		parent = avl_tree->get_parent(dst_node);
		if(node_elem->left == NULL && node_elem->right == NULL){ // leaf. remove it.
		
		
			free(node_elem);
			if(parent != NULL){
				temp = parent->get_node_params();
				if(temp->right == dst_node)
					temp->right = NULL;
				else
					temp->left = NULL;

				avl_tree->remove_node(dst_node);
				delete dst_node;


				//temp->bf = ((temp->right == NULL) ? temp->left_size : -temp->right_size);
				//temp->left_size = ((temp->left == NULL ) ? 0 : temp->left_size);
				//temp->right_size = ((temp->right == NULL ) ? 0 : temp->right_size);
				balance_up(parent);
				return;
			}

			avl_tree->remove_node(dst_node);
			avl_tree->set_root(NULL);
			avl_tree->reset();
			delete dst_node;
			return;


		}
		else{

			if(node_elem->left == NULL && node_elem->right != NULL){
				
				avl_tree->remove_node(dst_node);
				if(parent == NULL){
					
					avl_tree->set_root(node_elem->right);
					free(node_elem);
					delete dst_node;
					return;
				}

				temp = parent->get_node_params();
				if(temp->right == dst_node){
					temp->right = node_elem->right;
					if(temp->right != NULL){
						avl_tree->add_child(parent,temp->right);
						child_elem = node_elem->right->get_node_params();
						child_elem->parent = parent;
					}
					//temp->right_size = (((avl_elem *) node_elem->right->get_node_params())->left_size > ((avl_elem *) node_elem->right->get_node_params())->right_size ? ((avl_elem *) node_elem->right->get_node_params())->left_size : ((avl_elem *) node_elem->right->get_node_params())->right_size) + 1;


					free(node_elem);
					balance_up(parent);
					delete dst_node;
					return;
				}

				temp->left = node_elem->right;				
				if(node_elem->right != NULL){
					avl_tree->add_child(parent,node_elem->right);
					child_elem = node_elem->right->get_node_params();
					child_elem->parent = parent;
				}
				//temp->right_size = (((avl_elem *) node_elem->right->get_node_params())->left_size > ((avl_elem *) node_elem->right->get_node_params())->right_size ? ((avl_elem *) node_elem->right->get_node_params())->left_size : ((avl_elem *) node_elem->right->get_node_params())->right_size) + 1;
				free(node_elem);
				balance_up(parent);
				delete dst_node;
				return;

			}

			if(node_elem->left != NULL && node_elem->right == NULL){
				avl_tree->remove_node(dst_node);
				if(parent == NULL){
					
					avl_tree->set_root(node_elem->left);
				
					free(node_elem);
					delete dst_node;
					return;
				}

				temp = parent->get_node_params();
				if(temp->right == dst_node){
					temp->right = node_elem->left;				
					if(node_elem->left != NULL){
						avl_tree->add_child(parent,node_elem->left);
						child_elem = node_elem->left->get_node_params();
						child_elem->parent = parent;
					}
					//temp->left_size = (((avl_elem *) node_elem->left->get_node_params())->left_size > ((avl_elem *) node_elem->right->get_node_params())->right_size ? ((avl_elem *) node_elem->right->get_node_params())->left_size : ((avl_elem *) node_elem->right->get_node_params())->right_size) + 1;	
					free(node_elem);
					balance_up(parent);
					delete dst_node;
					return;
				}

				temp->left = node_elem->left;

				
				if(node_elem->left != NULL){
					avl_tree->add_child(parent,node_elem->left);
					child_elem = node_elem->left->get_node_params();
					child_elem->parent = parent;
				}
				//temp->left_size = (((avl_elem *) node_elem->left->get_node_params())->left_size > ((avl_elem *) node_elem->right->get_node_params())->right_size ? ((avl_elem *) node_elem->right->get_node_params())->left_size : ((avl_elem *) node_elem->right->get_node_params())->right_size) + 1;	
				free(node_elem);
				balance_up(parent);
				delete dst_node;
				return;

			}

			// both != NULL

			// find successor

			node * successor = tree_min(node_elem->right);
			avl_elem * succ_elem;
			succ_elem = successor->get_node_params();
			if(successor != NULL){
				node * successor_parent;
				successor_parent = avl_tree->get_parent(successor);
				if(successor_parent != NULL){
					
					avl_tree->remove_node(successor);
					avl_tree->remove_node(dst_node);
					avl_elem * succ_parent_elem = successor_parent->get_node_params();
					
					if(successor_parent != dst_node){
	
						if(succ_parent_elem->left == successor){							
							succ_parent_elem->left = succ_elem->right;							
						}
						else
							succ_parent_elem->right = succ_elem->right; // should never happen
						if(succ_elem->right != NULL && successor_parent != NULL){
							avl_tree->add_child(successor_parent,succ_elem->right);	
							avl_elem * succ_elem_right = (avl_elem *) succ_elem->right->get_node_params();
							succ_parent_elem->left_size = (succ_elem_right->left_size > succ_elem_right->right_size ? succ_elem_right->left_size : succ_elem_right->right_size ) + 1;
							succ_parent_elem->bf = succ_parent_elem->left_size - succ_parent_elem->right_size;
							succ_elem_right->parent = successor_parent;
							
						}

					}
					
					
					
				
					
				}
				else{

					printf("ERROR during remove. successor parent is NULL\n");
					return;
				}

				
				avl_elem * succ_left_elem;
				avl_elem * succ_right_elem;				
				if(successor == node_elem->right){ // successor == dst_node->right
					
					if(parent == NULL){
						// root = successor
						succ_elem->left = node_elem->left;
						succ_elem->parent = NULL;
						avl_tree->set_root(successor);
						if(succ_elem->left != NULL){
							avl_tree->add_child(successor, node_elem->left);
							/*
							succ_elem->left_size = (((avl_elem *) node_elem->left->get_node_params())->left_size > ((avl_elem *) node_elem->left->get_node_params())->right_size ? ((avl_elem *) node_elem->left->get_node_params())->left_size : ((avl_elem *) node_elem->left->get_node_params())->right_size ) + 1;
							*/

							succ_left_elem = succ_elem->left->get_node_params();
							succ_left_elem->parent = successor;
							

						}
						if(succ_elem->right != NULL){
							avl_tree->add_child(successor, succ_elem->right);
							/*
							succ_elem->right_size = (((avl_elem *) succ_elem->right->get_node_params())->left_size > ((avl_elem *) succ_elem->right->get_node_params())->right_size ? ((avl_elem *) succ_elem->right->get_node_params())->left_size : ((avl_elem *) succ_elem->right->get_node_params())->right_size ) + 1;
							*/
							succ_right_elem = succ_elem->right->get_node_params();
							succ_right_elem->parent = successor;
							

						}
						//succ_elem->bf = succ_elem->left_size - succ_elem->right_size;
						balance_up(successor);
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
					succ_elem->parent = parent;
					avl_tree->add_child(parent,successor);

					if(succ_elem->left != NULL){
						avl_tree->add_child(successor, node_elem->left);
						/*
						succ_elem->left_size = (((avl_elem *) node_elem->left->get_node_params())->left_size > ((avl_elem *) node_elem->left->get_node_params())->right_size ? ((avl_elem *) node_elem->left->get_node_params())->left_size : ((avl_elem *) node_elem->left->get_node_params())->right_size ) + 1;
						*/
						succ_left_elem = succ_elem->left->get_node_params();
						succ_left_elem->parent = successor;
						

					}
					if(succ_elem->right != NULL){
						avl_tree->add_child(successor, succ_elem->right);
						/*
						succ_elem->right_size = (((avl_elem *) succ_elem->right->get_node_params())->left_size > ((avl_elem *) succ_elem->right->get_node_params())->right_size ? ((avl_elem *) succ_elem->right->get_node_params())->left_size : ((avl_elem *) succ_elem->right->get_node_params())->right_size ) + 1;
						*/
						succ_right_elem = succ_elem->right->get_node_params();
						succ_right_elem->parent = successor;
						
					
					}
					/*
					succ_elem->bf = succ_elem->left_size - succ_elem->right_size;
					if(temp->left == successor)
						temp->left_size = (succ_elem->left_size > succ_elem->right_size ? succ_elem->left_size : succ_elem->right_size) + 1;

					if(temp->right == successor)
						temp->right_size = (succ_elem->left_size > succ_elem->right_size ? succ_elem->left_size : succ_elem->right_size) + 1;

					temp->bf = temp->left_size - temp->right_size;
					*/

					balance_up(successor);
					free(node_elem);
					delete dst_node;
					return;

					
				}

				// successor != dst_node->right;
						
				       if(parent == NULL){
						// root = successor
						succ_elem->left = node_elem->left;
						succ_elem->right = node_elem->right;
						
						avl_tree->set_root(successor);
						succ_elem->parent = NULL;
						if(succ_elem->left != NULL){
							avl_tree->add_child(successor, node_elem->left);
							/*
							succ_elem->left_size = (((avl_elem *) node_elem->left->get_node_params())->left_size > ((avl_elem *) node_elem->left->get_node_params())->right_size ? ((avl_elem *) node_elem->left->get_node_params())->left_size : ((avl_elem *) node_elem->left->get_node_params())->right_size ) + 1;
							*/
							succ_left_elem = succ_elem->left->get_node_params();
							succ_left_elem->parent = successor;
							
	
						}
						if(succ_elem->right != NULL){
							avl_tree->add_child(successor, succ_elem->right);
							/*
							succ_elem->right_size = (((avl_elem *) succ_elem->right->get_node_params())->left_size > ((avl_elem *) succ_elem->right->get_node_params())->right_size ? ((avl_elem *) succ_elem->right->get_node_params())->left_size : ((avl_elem *) succ_elem->right->get_node_params())->right_size ) + 1;
							*/
							succ_right_elem = succ_elem->right->get_node_params();
							succ_right_elem->parent = successor;
							
					
						}
						//succ_elem->bf = succ_elem->left_size - succ_elem->right_size;
						
						balance_up(successor_parent);	
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

					avl_tree->add_child(parent,successor);
					succ_elem->parent = parent;
					

					if(succ_elem->left != NULL){
						avl_tree->add_child(successor, node_elem->left);
						/*
						succ_elem->left_size = (((avl_elem *) node_elem->left->get_node_params())->left_size > ((avl_elem *) node_elem->left->get_node_params())->right_size ? ((avl_elem *) node_elem->left->get_node_params())->left_size : ((avl_elem *) node_elem->left->get_node_params())->right_size ) + 1;
						*/
						succ_left_elem = succ_elem->left->get_node_params();
						succ_left_elem->parent = successor;
						

					}
					if(succ_elem->right != NULL){
		
						avl_tree->add_child(successor, succ_elem->right);
						/*
						succ_elem->right_size = (((avl_elem *) succ_elem->right->get_node_params())->left_size > ((avl_elem *) succ_elem->right->get_node_params())->right_size ? ((avl_elem *) succ_elem->right->get_node_params())->left_size : ((avl_elem *) succ_elem->right->get_node_params())->right_size ) + 1;
						*/
						succ_right_elem = succ_elem->right->get_node_params();
						succ_right_elem->parent = successor;
						
					
					}

					/*
					succ_elem->bf = succ_elem->left_size - succ_elem->right_size;
					if(temp->left == successor)
						temp->left_size = (succ_elem->left_size > succ_elem->right_size ? succ_elem->left_size : succ_elem->right_size) + 1;

					if(temp->right == successor)
						temp->right_size = (succ_elem->left_size > succ_elem->right_size ? succ_elem->left_size : succ_elem->right_size) + 1;
					temp->bf = temp->left_size - temp->right_size;
					*/


					avl_tree->add_child(successor,node_elem->left);
					avl_tree->add_child(successor,node_elem->right);

					free(node_elem);
					balance_up(successor_parent);
					delete dst_node;
					return;
				

			}
			// else should never happen
			printf("ERROR during remove. successor is NULL\n");
			return;


		}


	}	



	
}
