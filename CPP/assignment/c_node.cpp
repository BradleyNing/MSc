//c_node.cpp by Group 10

#include "c_node.h"
#include "c_graph.h"
#include "c_exceptions.h"
// Check that first character is open bracket (BadHeaderException)
void C_node::checkheader(std::istream &file)
{
	char next_char;
	file>>next_char>>std::ws;
	if(next_char!='[')
	{
		BadHeaderException	e;
		e.str = next_char;
		e.node_seq = g_graph.node_counter;
		throw BadHeaderException(e);
	}
}

//check that last character is close bracket (BadFooterException)
void C_node::checkfooter(std::istream &file)
{
	char next_char;
	file>>next_char>>std::ws;
	if(next_char!=']')
	{
		BadFooterException e;
		e.str = next_char;
		e.node_seq = g_graph.node_counter;
		throw BadFooterException(e);
	}
}
