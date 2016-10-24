/** @file libpriqueue.c
 */

#include <stdlib.h>
#include <stdio.h>

#include "libpriqueue.h"


/**
  Initializes the priqueue_t data structure.
  
  Assumtions
    - You may assume this function will only be called once per instance of priqueue_t
    - You may assume this function will be the first function called using an instance of priqueue_t.
  @param q a pointer to an instance of the priqueue_t data structure
  @param comparer a function pointer that compares two elements.
  See also @ref comparer-page
 */
void priqueue_init(priqueue_t *q, int(*comparer)(void *, void *))
{
	/*if(q == NULL){
		printf("Dyn allocation\n");
		q = (priqueue_t *)malloc(sizeof(priqueue_t));
		q->is_dyn_allocated = 1;
	}
	else{
		
		q->is_dyn_allocated = 0;
	}*/
	q->head = NULL;
	q->tail = NULL;
	q->compare = comparer;
	q->size = 0;
}


/**
  Inserts the specified element into this priority queue.

  @param q a pointer to an instance of the priqueue_t data structure
  @param ptr a pointer to the data to be inserted into the priority queue
  @return The zero-based index where ptr is stored in the priority queue, where 0 indicates that ptr was stored at the front of the priority queue.
 */
int priqueue_offer(priqueue_t *q, void *ptr)
{
	priqueue_elem * new_elem;
	priqueue_elem * head;
	priqueue_elem * tail;
	int index = 0;
	void * new_job = ptr;
	new_elem = (priqueue_elem *) malloc(sizeof(priqueue_elem));
	new_elem->job_ptr = new_job;
	new_elem->next = NULL;
	new_elem->prev = NULL;

	if(q->head == NULL){
		q->head = new_elem;
		q->tail = new_elem;
		q->size = 1;
		index = 0;

		return index;
	}
	else{
		head = q->head;
		while(head != NULL){
			if(q->compare(new_elem->job_ptr,head->job_ptr) < 0 ){
				if(head == q->head){
					new_elem->next = q->head;
					(q->head)->prev = new_elem;
					new_elem->prev = NULL;
					q->head = new_elem;
					q->size = q->size + 1;
					index = 0;

					return index;

				}
				else{
					new_elem->next = head;
					new_elem->prev = head->prev;
					head->prev->next = new_elem;
					head->prev = new_elem;
					q->size = q->size + 1;

					return index;

				}
			}
			index++;
			head = head->next;
		}
		if(head == NULL) // Add to tail
		{
			q->tail->next = new_elem;
			new_elem->prev = q->tail;
			new_elem->next = NULL;
			q->tail = new_elem;
			q->size = q->size + 1;

			return index;
		}

		
	}

}


/**
  Retrieves, but does not remove, the head of this queue, returning NULL if
  this queue is empty.
 
  @param q a pointer to an instance of the priqueue_t data structure
  @return pointer to element at the head of the queue
  @return NULL if the queue is empty
 */
void *priqueue_peek(priqueue_t *q)
{

	if(q->head == NULL)
		return NULL;
	else
		return q->head->job_ptr;

	
}


/**
  Retrieves and removes the head of this queue, or NULL if this queue
  is empty.
 
  @param q a pointer to an instance of the priqueue_t data structure
  @return the head of this queue
  @return NULL if this queue is empty
 */
void *priqueue_poll(priqueue_t *q)
{
	priqueue_elem * head;
	void * ptr;
	if(q->head == NULL)
		return NULL;
	else{
		head = q->head;
		if(q->head == q->tail){
			q->tail = NULL;
			q->head = NULL;
		}
		else{
			q->head = head->next;
			q->head->prev = NULL;
		}
		
		q->size = q->size - 1;
		ptr = head->job_ptr;
		free(head);
		return ptr;
	}
		
}


/**
  Returns the element at the specified position in this list, or NULL if
  the queue does not contain an index'th element.
 
  @param q a pointer to an instance of the priqueue_t data structure
  @param index position of retrieved element
  @return the index'th element in the queue
  @return NULL if the queue does not contain the index'th element
 */
void *priqueue_at(priqueue_t *q, int index)
{
	priqueue_elem * indexed_elem;
	int start_index;
	if(q->head == NULL)
		return NULL;
	else{
		indexed_elem = q->head;
		start_index = 0;
		while(indexed_elem != NULL && start_index <= index){
			if(start_index == index){
				return indexed_elem->job_ptr;
			}
			else{
				start_index++;
				indexed_elem = indexed_elem->next;
			}
		}
		return NULL;
	}
}


/**
  Removes all instances of ptr from the queue. 
  
  This function should not use the comparer function, but check if the data contained in each element of the queue is equal (==) to ptr.
 
  @param q a pointer to an instance of the priqueue_t data structure
  @param ptr address of element to be removed
  @return the number of entries removed
 */
int priqueue_remove(priqueue_t *q, void *ptr)
{
	int nentries = 0;
	priqueue_elem * head;
	void * removed_elem = ptr;
	
	if(q->head == NULL)
		return 0;

	head = q->head;
	while(head != NULL){
		if(q->compare(head->job_ptr,removed_elem) == 0){

			if(head == q->head && q->size != 1 ){
				q->head = q->head->next;
				q->head->prev = NULL;
				q->size = q->size - 1;
				//free(head->job_ptr);
				free(head);
				head = q->head;
				
				nentries ++;
				continue;
			}
			else {
				if(head == q->head && q->size == 1){
					q->head = NULL;
					q->size = 0;
					q->tail = NULL;
					nentries++;
					//free(head->job_ptr);
					free(head);
					
					break;
				}
				else{
					if(head == q->tail){
						q->tail = q->tail->prev;
						q->tail->next = NULL;
						//free(head->job_ptr);
						free(head);
						q->size = q->size - 1;
						nentries ++;
						
						break;
					}
					else{
						head->next->prev = head->prev;
						head->prev->next = head->next;
						//free(head->job_ptr);
						free(head);
						q->size = q->size - 1;
						nentries++;

					}	

				}

			}

		}
		head = head->next;
	}
	return nentries;
}

/**
  Removes the specified index from the queue, moving later elements up
  a spot in the queue to fill the gap.
 
  @param q a pointer to an instance of the priqueue_t data structure
  @param index position of element to be removed
  @return the element removed from the queue
  @return NULL if the specified index does not exist
 */
void *priqueue_remove_at(priqueue_t *q, int index)
{
	int curr_index;
	priqueue_elem * head;

	if(q->head == NULL)
		return NULL;
	else{
		curr_index = 0;
		head = q->head;
		while(head != NULL && curr_index <= index){
			if(curr_index == index){
				if(head == q->head && q->size != 1){
					q->head = q->head->next;
					q->head->prev = NULL;
					q->size = q->size - 1;
					head->next = NULL;
					head->prev = NULL;
					return head;

				}
				else{
					if(head == q->head && q->size == 1){
						q->head = NULL;
						q->size = 0;
						q->tail = NULL;
						head->next = NULL;
						head->prev = NULL;
						return head;
					}
					else{
						if(head == q->tail){
							q->tail = q->tail->prev;
							q->tail->next = NULL;
							q->size = q->size - 1;
							head->next = NULL;
							head->prev = NULL;
							return head;
						}
						else{
							head->next->prev = head->prev;
							head->prev->next = head->next;
							q->size = q->size - 1;
							head->next = NULL;
							head->prev = NULL;
							return head;
						}	

					}

				}
			}
			curr_index ++;
			head = head->next;
		}
	}
	return NULL;
}

/**
  Returns the number of elements in the queue.
 
  @param q a pointer to an instance of the priqueue_t data structure
  @return the number of elements in the queue
 */
int priqueue_size(priqueue_t *q)
{
	return q->size;
}

/**
  Destroys and frees all the memory associated with q.
  
  @param q a pointer to an instance of the priqueue_t data structure
 */
void priqueue_destroy(priqueue_t *q)
{
	priqueue_elem * head;
	priqueue_elem * tmp;
	head = q->head;

	printf("Freeing up ...\n");
	while(head != NULL){
		tmp = head;
		head = head->next;
		//free(tmp->job_ptr);
		free(tmp);
	
	}
	if(q->is_dyn_allocated == 1){
		printf("Freeing priority queue\n");	
		free(q);

	}
}
