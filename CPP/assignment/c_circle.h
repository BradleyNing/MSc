//c_circle.h by Group 10

#ifndef C_CIRCLE_H_
#define C_CIRCLE_H_

#include <fstream>
#include "c_node.h"
#include "c_polygon.h"
#define PI 3.14159265

//circle class inherits from polygon class
class C_circle:public C_polygon{
private:
	float radius;

public:
	void draw();
	C_circle();
	~C_circle(){};
	friend std::istream & operator>>(std::istream &, C_circle &);
};

#endif /* C_CIRCLE_H_ */
