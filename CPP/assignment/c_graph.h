//c_graph.h by Group 10

#ifndef GRAPH_H_
#define GRAPH_H_

#include <fstream>
#include <list>
#include "c_node.h"

class C_sceneGraph{
public:
	std::list <C_node *> nodelist;
	int		node_counter;
	void	draw();
	friend 	std::istream & operator>>(std::istream &, C_sceneGraph &);
	C_sceneGraph();
	~C_sceneGraph();
};

extern  C_sceneGraph g_graph;

#endif /* GRAPH_H_ */
