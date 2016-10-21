#include "linkedlist.h"
#include <stdio.h>
#include <stdlib.h>

typedef struct elem_struct{

	int val;
} elem;

void display(llist * l){
	int i;
	elem  * p;
	for(i = 0; i < l->size; i++){
		p = llist_get(l,i);
		printf("%d ",p->val);
	}
	printf("\n");
}

void acton(elem * p, void * args){
	p->val = p->val + 2;
}

int equality(elem * elem1, elem * elem2){
	if(elem1->val == elem2->val)
		return 0;
	else
		return 1;
}

void main(){

	llist l;
	llist_init(&l);
	llist_set_equality_checker(&l,equality);
	elem elements[5];
	int i;
	for(i = 0; i < 5; i++){
		elements[i].val = i;
		llist_append(&l,&elements[i]);
	}

	display(&l);

	llist_pop(&l);
	
	display(&l);

	llist_remove_at(&l,2);

	display(&l);

	llist_remove(&l,&elements[1]);

	display(&l);

	llist_iterate(&l,acton, NULL);

	display(&l);
	
	llist_destroy(&l);

}
