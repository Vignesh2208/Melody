#include "bstmap.h"
#include <stdio.h>
#include <stdlib.h>
#include <cstring>

#define DEFAULT_SIZE 10000

int hash(void * elem){
	int * ptr = (int *) elem;
	return *ptr;
}

int string_hash(char * s)
{

    //http://stackoverflow.com/questions/114085/fast-string-hashing-algorithm-with-low-collision-rates-with-32-bit-integer
    int hash = 0;
    char * ptr = s;
    int i = 0;
    while(*ptr != NULL)
    {
    	hash += *ptr;
    	hash += (hash << 10);
    	hash ^= (hash >> 6);

        ++ptr;
    }

    hash += (hash << 3);
    hash ^= (hash >> 11);
    hash += (hash << 15);


    return hash;
}

int integer_hash(int * val){

	char buffer[33];
	int hash;
	sprintf(buffer,"%d", *val);
	hash = str_hash(buffer);
	return hash;

}


bstmap::bstmap(char * key_type = "default", int map_size = 0){

	if(strcmp(key_type,"default") == 0)
		key_hash = hash;
	if(strcmp(key_type,"int") == 0)
		key_hash = integer_hash;
	if(strcmp(key_type,"string") == 0)
		key_hash = string_hash;

	if(map_size <= 0)
		size = DEFAULT_SIZE;
	else
		size = map_size;

	bstarray = new bst * [size];
	active_keys = (llist * ) malloc(sizeof(llist));
	initialized = (int *) calloc(size, sizeof(int));
	type = (char *)malloc(sizeof(char)* strlen(key_type) + 1);
	strcpy(type,key_type);
	is_compare_fn_set = 0;

	n_removed = 0;
}

bstmap::~bstmap(){

	int i = 0;
	for(i = 0; i < size; i++){
		if(initialized[i] == 1)
			delete bstarray[i];
	}
	delete bstarray;
	free(active_keys);
	free(initialized);
	free(type);

}

void bstmap::set_key_comparer(int (*comparefn)(void * elem1, void * elem2)){
	int i = 0;
	compare = comparefn;
	is_compare_fn_set = 1;
	for(i = 0; i < size; i++){
		if(initialized[i] == 1)
		bstarray[i]->set_key_comparer(comparefn);

	}

}

void * bstmap::get(void * key){

	int index;

	if(key == NULL)
		return NULL;
	index = abs(key_hash(key)) % size;
	bst * t;

	t = bstarray[index];
	return t->get(key);
	

}

void bstmap::put(void * key, void * value){
	
	int index;

	

	if(key == NULL)
		return;
	index = abs(key_hash(key)) % size;
	bst * t;

	if(initialized[index] == 0){
		bstarray[index] = new bst(type);
		if(is_compare_fn_set)
			bstarray[index]->set_key_comparer(compare);
		initialized[index] = 1;
	}

	t = bstarray[index];
	if(t->search(key) == 0){
		llist_append(active_keys, key);
	}
	t->insert(key,value);


	
	

}

void bstmap::remove(void * key){

	int index;

	if(key == NULL)
		return NULL;
	index = abs(key_hash(key)) % size;
	bst * t;

	t = bstarray[index];
	if(t->search(key)){
		n_removed ++;
		t->remove(key);
	}
	
}

int bstmap::exists(void * key){

	int index;

	if(key == NULL)
		return NULL;
	index = abs(key_hash(key)) % size;
	bst * t;

	t = bstarray[index];
	return t->search(key);
}

llist * bstmap::keys(){

	int i = 0;
	llist_elem * head = active_keys->head;
	llist_elem * tmp;
	llist * l = active_keys;

	int numremoved = 0;		

	while(head != NULL && numremoved < n_removed){

		if(bstmap::get(head->item) == NULL){
			
			l->size --;
			numremoved ++;
			if(head == l->head){
				
				if(l->head == l->tail){
					l->head = NULL;
					l->tail = NULL;
					free(head);
					break;

				}
				
				head->next->prev = NULL;
				l->head = head->next;
				free(head);
				head = l->head;
				

			}
			else{
				if(head == l->tail){
					
					l->tail = l->tail->prev;
					if(l->tail != NULL)
					l->tail->next = NULL;
					free(head);
					break;

				}	
				else{
					head->prev->next = head->next;
					head->next->prev = head->prev;
					tmp = head->next;
					free(head);
					head = tmp;
				}

			}
		



		}
		else
			head = head->next;
	}
	
	n_removed = 0;

	return active_keys;

}
