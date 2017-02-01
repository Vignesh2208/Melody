#include "skiplist.h"
#include <cstring>
#include <stdio.h>
#include <ctime> 
#include <iostream>






int int_compare_fn(int * e1, int * e2){

	if(*e1 > *e2)
		return 1;
	if(*e1 == *e2)
		return 0;

	return -1;

}

int str_compare_fn(char * s1, char * s2){

	return strcmp(s1,s2);
}

skiplist::skiplist(int M , char * item_type = "int"){

	int i;
	srand((unsigned)time(0)); 
	assert(M > 0);

	strcpy(type,item_type);
	
	if(strcmp(type,"int") == 0)
		compare = int_compare_fn;

	if(strcmp(type,"string") == 0)
		compare = str_compare_fn;

	head_ptrs = (skipl_elem *) malloc(M * sizeof(skipl_elem));
	for(i = 0; i < M; i++){

		head_ptrs[i] = (skip_elem *) malloc(sizeof(skipl_elem));
		head_ptrs[i]->item = NULL;

		head_ptrs[i]->next = NULL;

		if(i == 0)
			head_ptrs[i]->down = NULL;

		if(i == M-1)
			head_ptrs[i]->up = NULL;

		if(i > 0){
			head_ptrs[i]->down = head_ptrs[i-1];
			head_ptrs[i-1]->up = head_ptrs[i];
		}
	}

}

skiplist::~skiplist(){

	int curr_level = M-1;
	skipl_elem * tmp;
	skipl_elem * head;

	while(curr_level >= 0){

		head = head_ptrs[curr_level];
		while(head != NULL){
			tmp = head;
			head = head->next;
			free(tmp);
		}
		curr_level --;

	}

	free(head_ptrs);

	


}

void skiplist::insert(void * item){

	skipl_elem * prev_ptrs[M];
	int curr_level = M-1;

	prev_ptrs[M-1] = head_ptrs[M-1];

	
	while(curr_level >= 0){
		while(prev_ptrs[curr_level]->next != NULL && compare(prev_ptrs[curr_level]->next->item,item) < 0){
		
			prev_ptrs[curr_level] = prev_ptrs[curr_level]->next;

		}
		if(curr_level > 0){
			prev_ptrs[curr_level -1] = prev_ptrs[curr_level]->down;
		}
		else{
			break;
		}
	
		curr_level --;


	}


	skipl_elem * new_elem = (skipl_elem *) malloc(sizeof(skipl_elem));
	skipl_elem * bottom_ptr;
	new_elem->down = NULL;
	new_elem->item = item;
	new_elem->up = NULL;

	if(prev_ptrs[0]->next == NULL){
		prev_ptrs[0]->next = new_elem;
		new_elem->next = NULL;
	}
	else{
		new_elem->next = prev_ptrs[0]->next;
		prev_ptrs[0]->next = new_elem;
	}
		
	bottom_ptr = new_elem;
	curr_level = 1;

	while((int)(rand() %2 ) == 1 && curr_level < M-1){

		new_elem = (skipl_elem *) malloc(sizeof(skipl_elem));
		new_elem->item = item;
		new_elem->down = bottom_ptr;
		new_elem->up = NULL;
		bottom_ptr->up = new_elem;

		

		if(prev_ptrs[curr_level]->next == NULL){
			prev_ptrs[curr_level]->next = new_elem;
			new_elem->next = NULL;
		}
		else{
			new_elem->next = prev_ptrs[curr_level]->next;
			prev_ptrs[curr_level]->next = new_elem;
		}

		bottom_ptr = new_elem;
		curr_level++;		

	}
	



}

int skiplist::exists(void * item){


	skipl_elem * prev_ptrs[M];
	int curr_level = M-1;

	prev_ptrs[M-1] = head_ptrs[M-1];

	
	while(curr_level >= 0){
		while(prev_ptrs[curr_level]->next != NULL && compare(prev_ptrs[curr_level]->next->item,item) < 0){
		
		
			prev_ptrs[curr_level] = prev_ptrs[curr_level]->next;

		}

		if(compare(prev_ptrs[curr_level]->next->item,item) == 0)
			break;

		if(curr_level > 0){
			prev_ptrs[curr_level -1] = prev_ptrs[curr_level]->down;
		}
		else{
			break;
		}
		curr_level --;


	}

	if(prev_ptrs[curr_level]->next == NULL)
		return 0;

	if(compare(prev_ptrs[curr_level]->next->item,item) == 0)
		return 1;
	else
		return 0;	


}


void skiplist::remove(void * item){

	skipl_elem * prev_ptrs[M];
	int curr_level = M-1;

	prev_ptrs[M-1] = head_ptrs[M-1];

	
	while(curr_level >= 0){
		while(prev_ptrs[curr_level]->next != NULL && compare(prev_ptrs[curr_level]->next->item,item) < 0){
		
			prev_ptrs[curr_level] = prev_ptrs[curr_level]->next;

		}
		if(curr_level > 0){
			prev_ptrs[curr_level -1] = prev_ptrs[curr_level]->down;
		}
		else{
			break;
		}
		curr_level --;


	}

	if(prev_ptrs[0]->next == NULL)
		return;

	skipl_elem * tmp;
	skipl_elem * top_ptr = NULL;

	if(compare(prev_ptrs[0]->next->item,item) == 0){

		curr_level = 0;
		do{
			tmp = prev_ptrs[curr_level]->next;
			top_ptr = tmp->up;
			pre_ptrs[0]->next = tmp->next;
			free(tmp);
			curr_level ++;
		
		}while(top_ptr != NULL);

	}

}

void set_compare_fn(int (*comparer)(void * e1, void * e2)){

	this->compare = comparer;

}

void skiplist::iterate(void (*acton_fn)(void * item, void * args)){


	skipl_elem * head = head_ptrs[0];

	while(head != NULL){
		if(head != head_ptrs[0])
			acton_fn(head->item,args);
		head = head->next;
	}

}

skipl_elem ** skiplist::get_head_ptrs(){
	return head_ptrs;
}

int skiplist::get_n_levels(){
	return M;
}
