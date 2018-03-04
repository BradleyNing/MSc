//c_translate.cpp by Group 10

#include <GL/gl.h>     // The GL Header File
#include <GL/glut.h>   // The GL Utility Toolkit (Glut) Header
#include <GL/glu.h>

#include "c_translate.h"
#include "c_graph.h"
#include "c_exceptions.h"

// Overloaded >> operator
// Read in a translate object. Checks header and footer of the object
// Provides error checking, passes back the shape name
// to the InvalidNodeException class in case of an error
std::istream & operator >> (std::istream &file, C_translate &Translate)
{
	Translate.checkheader(file);
	file>>Translate.trans[0]>>Translate.trans[1]>>Translate.trans[2];
	if(file.fail())
	{
		InvalidNodeException e;
		e.str = "translate";
		e.node_seq = g_graph.node_counter;
		throw InvalidNodeException(e);
	}
	Translate.checkfooter(file);
	return file;
}
// Translate constructor
C_translate::C_translate(void)
{
	trans[0]=0;
	trans[1]=0;
	trans[2]=0;
}
// Translate Draw function
void C_translate::draw(void)
{
	glTranslatef(trans[0], trans[1], trans[2]);

}
