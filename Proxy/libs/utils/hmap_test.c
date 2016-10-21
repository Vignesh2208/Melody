#include "hashmap.h"
#include <stdio.h>
#include <stdlib.h>

typedef struct elem_struct{
	int val;
} elem;

int key_comparer(elem * key1, elem * key2){
	
	if(key1->val == key2->val)
		return 0;
	else
		return 1;

}

int key_hash(elem * key){
	return int_hash(key->val);
}

void display(hashmap * h, elem * keys, int size){
	int i;
	elem  * p;
	for(i = 0; i < size; i++){
		p = hmap_get(h,&keys[i]);
		if(p != NULL)
			printf("(%d, %d) ",keys[i].val, p->val);
	}
	printf("\n");
}


void main(){

	hashmap h;
	char * key = "Hello";
	char * key2 = "Hello";
	char * value = "value";
	char * ret;
	/*hmap_init(&h,"custom",0);
	hmap_set_hash(&h,key_hash);
	hmap_set_comparer(&h,key_comparer);
	int i;
	elem keys[5];
	int invalid_key = 1001;
	elem elements[5];
	elem * p;
	printf("Finished Initialization\n");
	for(i = 0; i < 5; i++){
		keys[i].val = 1000*i;
		elements[i].val = i;
		hmap_put(&h,&keys[i],&elements[i]);
	}
	printf("Finished inserting\n");
	//display(&h,keys,5);



	p = hmap_get(&h,&keys[2]);

	if(p != NULL)
	printf("val = %d\n",p->val);

	//p = hmap_get(&h,&invalid_key);

	//if(p != NULL)
	//printf("val = %d\n",p->val);

	hmap_remove(&h,&keys[0]);
	//display(&h,&keys,5);

	for(i = 0; i < 5; i++){
		keys[i].val = 1000*i;
		elements[i].val = i + 1;
		hmap_put(&h,&keys[i],&elements[i]);
	}

	display(&h,keys,5);

	hmap_destroy(&h);*/

	hmap_init(&h,"string",0);
	hmap_put(&h,key,value);
	ret = hmap_get(&h,key2);
	printf("Ret = %s\n",ret);
	hmap_destroy(&h);

}
