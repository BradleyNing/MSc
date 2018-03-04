//c_polygon.h by Group 10

#ifndef POLYGON_H_
#define POLYGON_H_

#include <vector>
#include <fstream>
#include "c_node.h"

//polygon class inherits from abstract node class
class C_polygon:public C_node {
protected:
	int		vertNum;
	float	color[3];
	std::vector <float *>	points;

public:
	void draw();
	C_polygon();
	~C_polygon();
	friend std::istream & operator>>(std::istream &, C_polygon &);
};

#endif /* POLYGON_H_ */
