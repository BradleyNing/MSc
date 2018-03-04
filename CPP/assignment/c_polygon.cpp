//c_polygon.c by Group 10
#include <GL/gl.h>     // The GL Header File
#include <GL/glut.h>   // The GL Utility Toolkit (Glut) Header
#include <GL/glu.h>

#include "c_polygon.h"
#include "c_graph.h"
#include "c_exceptions.h"

std::istream & operator >> (std::istream &file, C_polygon &polygon)
{
	polygon.checkheader(file);
	std::string	c_name, v_name;
	int		v_num;
	file>>c_name>>polygon.color[0]>>polygon.color[1]>>polygon.color[2]>>v_name>>v_num;
	if(c_name!="colour" || v_name!="num_vert" || file.fail())
	{
		InvalidNodeException e;
		e.str = "polygon";
		e.node_seq = g_graph.node_counter;
		throw InvalidNodeException(e);
	}
	polygon.vertNum = v_num;
	float *point;
	for(int i=0; i<v_num; i++)
	{
		point = new float[3];
		file>>point[0]>>point[1]>>point[2];
		polygon.points.push_back(point);
	}
	if(file.fail())
	{
		InvalidNodeException e;
		e.str = "polygon";
		e.node_seq = g_graph.node_counter;
		throw InvalidNodeException(e);
	}
	polygon.checkfooter(file);
	return file;
}

C_polygon::C_polygon()
{
	points.clear();
	vertNum  = 0;
	color[0] = 1;  //red
	color[1] = 0;
	color[2] = 0;
}

C_polygon::~C_polygon()
{
	for(unsigned i=0; i<points.size(); i++)
	{
		if (points[i] != NULL) 	delete points[i];
	}
	points.clear();
}
void C_polygon::draw(void)
{
	glBegin(GL_LINE_LOOP);
	glColor3f(color[0], color[1], color[2]);
	for(unsigned i=0; i<points.size(); i++)
		glVertex3f(points[i][0], points[i][1], points[i][2]);
	glEnd();
}
