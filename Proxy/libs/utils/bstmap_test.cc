#include "bstmap.h"
#include <stdio.h>
#include <stdlib.h>

void print_val(int * key, bstmap * map){


	int * val = map->get(key);
	if(val != NULL)
		printf("Key = %d, Value = %d\n", *key, * val);

}


void display(bstmap * map){

	llist * active_keys = map->keys();
	llist_iterate(active_keys, print_val, map);	

}

int main(){
	bstmap * t;
	printf("Initializing\n");
	t = new bstmap("int");
	printf("Initialization complete\n");

	int keys[10] = {8,4,2,3,6,7,12,9,10,-1};
	int values[10] = {10,20,30,40,50,60,70,80,90,100};
	int i =0 ;

	for(i = 0; i < 10; i++)
		t->put(&keys[i],&values[i]);

	display(t);

	
	printf("\n\nFirst remove. key = %d\n\n", keys[4]);
	t->remove(&keys[4]);
	display(t);
	

	printf("\n\nSecond remove. key = %d\n\n", keys[0]);
	t->remove(&keys[0]);
	display(t);
	


	printf("\n\nThird remove. key = %d\n\n", keys[5]);
	t->remove(&keys[5]);
	display(t);
	


	printf("\n\nFourth remove. key = %d\n\n", keys[2]);
	t->remove(&keys[2]);
	display(t);
	


	printf("\n\nFifth remove. key = %d\n\n", keys[1]);
	t->remove(&keys[1]);
	display(t);
	

	printf("\n\nSixth remove. key = %d\n\n", keys[6]);
	t->remove(&keys[6]);
	display(t);
	

	printf("\n\nSeventh remove. key = %d\n\n", keys[7]);
	t->remove(&keys[7]);
	display(t);
	

	printf("\n\nEigth remove. key = %d\n\n", keys[8]);
	t->remove(&keys[8]);
	display(t);
	


	printf("\n\nNineth remove. key = %d\n\n", keys[9]);
	t->remove(&keys[9]);
	display(t);
	


	printf("\n\nTenth remove. key = %d\n\n", keys[3]);
	t->remove(&keys[3]);
	display(t);
	

	

	printf("Inserting again...\n");
	for(i = 0; i < 10; i++)
		t->put(&keys[i],&values[i]);
	printf("Insertion complete\n");
	display(t);
	
	

	printf("\n\ncleaning up...\n\n");
	delete t;

	return 0;
}
