

all : bstmap_test

llist_test : llist_test.c linkedlist.c linkedlist.h
		gcc llist_test.c linkedlist.c -o llist_test

hmap_test : hmap_test.c hashmap.c linkedlist.c hashmap.h
		gcc hmap_test.c hashmap.c linkedlist.c -o hmap_test

graph_test : graph_test.cc graph.cc hashmap.c linkedlist.c graph.h hashmap.h linkedlist.h
		g++ -fpermissive graph_test.cc graph.cc hashmap.c linkedlist.c -o graph_test

tree_test : tree_test.cc tree.cc graph.cc hashmap.c linkedlist.c graph.h hashmap.h linkedlist.h tree.h
		g++ -fpermissive tree_test.cc tree.cc graph.cc hashmap.c linkedlist.c -o tree_test

bst_test : bst_test.cc bst.cc tree.cc graph.cc hashmap.c linkedlist.c graph.h linkedlist.h tree.h bst.h
		g++ -fpermissive bst_test.cc bst.cc tree.cc graph.cc hashmap.c linkedlist.c -o bst_test

avl_test : avl_test.cc avl.cc tree.cc graph.cc hashmap.c linkedlist.c graph.h linkedlist.h tree.h avl.h
		g++ -fpermissive avl_test.cc avl.cc tree.cc graph.cc hashmap.c linkedlist.c -o avl_test

bstmap_test : bstmap_test.cc bstmap.cc bstmap.h bst.cc tree.cc graph.cc hashmap.c linkedlist.c graph.h linkedlist.h tree.h bst.h
		g++ -fpermissive bstmap_test.cc bstmap.cc bst.cc tree.cc graph.cc hashmap.c linkedlist.c -o bstmap_test
