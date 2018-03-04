//c_graph.cpp by Group 10

#include <string>
#include <list>
#include "c_node.h"
#include "c_polygon.h"
#include "c_scale.h"
#include "c_translate.h"
#include "c_circle.h"
#include "c_exceptions.h"
#include "c_graph.h"

C_sceneGraph g_graph; //g_graph, globe variable to save all the graph nodes

C_sceneGraph::C_sceneGraph(void)
{
	node_counter = 0;
	nodelist.clear();
}

C_sceneGraph::~C_sceneGraph(void)
{
	std::list <C_node *>::iterator it;
	for(it=nodelist.begin(); it!=nodelist.end(); it++)
	{
		if((*it) != NULL) delete (*it);
	}
	nodelist.clear();
}

void C_sceneGraph::draw(void)
{
	C_node *pNode;
	std::list <C_node *>::iterator it;
	for(it=nodelist.begin(); it!=nodelist.end(); it++)
	{
		pNode = *it;
		pNode->draw();
	}
}

std::istream & operator >>(std::istream &file, C_sceneGraph &Graph)
{
	std::string	shapetype;

	while(!file.eof())
	{
		g_graph.node_counter++;
		file>>shapetype;
		if(shapetype == "scale")
		{
			C_scale *pNode;
			pNode = new C_scale;
			file>>(*pNode);
			g_graph.nodelist.push_back(pNode);
		}
		else if(shapetype == "translate")
		{
			C_translate *pNode;
			pNode = new C_translate;
			file>>(*pNode);
			g_graph.nodelist.push_back(pNode);
		}
		else if(shapetype == "polygon")
		{
			C_polygon *pNode;
			pNode = new C_polygon;
			file>>(*pNode);
			g_graph.nodelist.push_back(pNode);
		}
		else if(shapetype == "circle")
		{
			C_circle *pNode;
			pNode = new C_circle;
			file>>(*pNode);
			g_graph.nodelist.push_back(pNode);
		}
		else
		{
			InvalidNodeTypeException e;
			e.str = shapetype;
			e.node_seq = g_graph.node_counter;
			throw InvalidNodeTypeException(e);
		}
	}
	return file;
}



