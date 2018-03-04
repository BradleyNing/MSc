//main.cpp by Group 10

#include <fstream>
#include <iostream>
#include "c_graph.h"
#include "my_gl.h"
#include "c_exceptions.h"
using namespace std;

// main, reads in from file, errors out if no arguments are passed, catches exceptions
int main(int argc, char *argv[])
{
	try
	{
		if(argc!=2)
		{
			cerr<<"Incorrect usage. Should pass one argument to locate the graph file"<<std::endl;
		}
		else
		{
			ifstream in(argv[1]);
			if(!in.good())
				throw BadFileException();
			in >> g_graph;  //g_graph, globe variable to save all the graph nodes
			window w(argc,argv);
			in.close();
		}
	}
	catch(BadFileException& e)
	{
		cerr<<"BadFileException occurred"<<endl;
	}
	catch(InvalidNodeTypeException& e)
	{
		cerr<<"No."<<e.node_seq<<" Node has invalidShapeType of: "<<e.str<<endl;
	}
	catch(InvalidNodeException& e)
	{
		cerr<<"No."<<e.node_seq<<" Node, "<<e.str<<" has invalid format!"<<endl;
	}
	catch(BadHeaderException& e)
	{
		cerr<<"No."<<e.node_seq<<" Unexpected Header encountered: "<<e.str<<endl;
	}
	catch(BadFooterException& e)
	{
		cerr<<"No."<<e.node_seq<<" Unexpected Footer encountered: "<<e.str<<endl;
	}
	catch(std::bad_alloc& e)
	{
		cerr<<"Memory allocating error"<<e.what()<<endl;
	}
	return 0;   //double check
}
