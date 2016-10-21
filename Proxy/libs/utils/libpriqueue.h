/** @file libpriqueue.h
 */

#ifndef LIBPRIQUEUE_H_
#define LIBPRIQUEUE_H_



// return value < 0 : elem1 < elem2
// return value > 0 : elem1 > elem2
// return value = 0 : elem1 = elem2

typedef int (*compare_fn)(void * elem1, void * elem2);

/**
  Priqueue Data Structure
*/

typedef struct _priqueue_elem_t
{
	void * job_ptr;
	struct _priqueue_elem_t * next;
	struct _priqueue_elem_t * prev;

}
priqueue_elem;

typedef struct _priqueue_t
{
	priqueue_elem * head;
	priqueue_elem * tail;
	compare_fn compare;
	int size;
	int is_dyn_allocated;

} priqueue_t;


void   priqueue_init     (priqueue_t *q, int(*comparer)(void *, void *));

int    priqueue_offer    (priqueue_t *q, void *ptr);
void * priqueue_peek     (priqueue_t *q);
void * priqueue_poll     (priqueue_t *q);
void * priqueue_at       (priqueue_t *q, int index);
int    priqueue_remove   (priqueue_t *q, void *ptr);
void * priqueue_remove_at(priqueue_t *q, int index);
int    priqueue_size     (priqueue_t *q);
void   priqueue_destroy  (priqueue_t *q);

#endif /* LIBPQUEUE_H_ */
