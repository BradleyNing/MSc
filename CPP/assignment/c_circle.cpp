//c_circle.c by Group 10

#include <GL/gl.h>     // The GL Header File
#include <GL/glut.h>   // The GL Utility Toolkit (Glut) Header
#include <GL/glu.h>
#include <math.h>

#include "c_circle.h"
#include "c_graph.h"
#include "c_exceptions.h"

// Overloaded >> operator
// Read in a circle object. Checks header and footer of the object
// Provides error checking, passes back the shape name
// to the InvalidNodeException class in case of an error
std::istream & operator >> (std::istream &file, C_circle &circle)
{
	circle.checkheader(file);
	std::string	c_name;
	file>>c_name>>circle.color[0]>>circle.color[1]>>circle.color[2];
	if(c_name!="colour" || file.fail())
	{
		InvalidNodeException e;
		e.str = "circle";
		e.node_seq = g_graph.node_counter;
		throw InvalidNodeException(e);
	}

	std::string r_name, seg_name;
	float  r;
	int    s_num;
	file>>r_name>>std::ws>>r>>seg_name>>std::ws>>s_num;
	if(file.fail() || r_name!="radius"|| r<=0 || seg_name!="num_segments" || s_num<3)
	{
		InvalidNodeException e;
		e.str = "circle";
		e.node_seq = g_graph.node_counter;
		throw InvalidNodeException(e);
	}
	circle.radius  = r;
	circle.vertNum = s_num;

	circle.checkfooter(file);
	return file;
}
// Circle constructor
C_circle::C_circle(void)
{
	radius = 0;
}
// Circle draw function, uses math library to perform parametric operation
void C_circle::draw(void)
{
	glBegin(GL_LINE_LOOP);
	glColor3f(color[0], color[1], color[2]);
	float x,y,z;
	for(int i=0; i<vertNum; i++)
	{
		x = radius*cos(i*2.0*PI/vertNum+PI/2.0);
		y = radius*sin(i*2.0*PI/vertNum+PI/2.0);
		z = 0;
		glVertex3f(x, y, z);
	}
	glEnd();
}
