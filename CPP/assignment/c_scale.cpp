//c_scale.cpp by Group 10

#include <GL/gl.h>     // The GL Header File
#include <GL/glut.h>   // The GL Utility Toolkit (Glut) Header
#include <GL/glu.h>

#include "c_scale.h"
#include "c_graph.h"
#include "c_exceptions.h"

// Overloaded >> operator
// Read in a scale object. Checks header and footer of the object
// Provides error checking, passes back the shape name
// to the InvalidNodeException class in case of an error
std::istream & operator >> (std::istream &file, C_scale &Scale)
{
	Scale.checkheader(file);
	file>>Scale.scale[0]>>Scale.scale[1]>>Scale.scale[2];
	if(file.fail())
	{
		InvalidNodeException e;
		e.str = "scale";
		e.node_seq = g_graph.node_counter;
		throw InvalidNodeException(e);
	}
	Scale.checkfooter(file);
	return file;
}
// Scale constructor
C_scale::C_scale(void)
{
	scale[0]=1;
	scale[1]=1;
	scale[2]=1;
}
// Scale draw function
void C_scale::draw(void)
{
	glScalef(scale[0], scale[1],scale[2]);
}
