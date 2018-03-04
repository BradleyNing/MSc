//c_scale.h by Group 10

#ifndef C_SCALE_H_
#define C_SCALE_H_

#include <fstream>
#include "c_node.h"
//scale class inherits from abstract node class
class C_scale:public C_node {
private:
	float scale[3];

public:
	void draw();
	C_scale();
	~C_scale(){};
	friend std::istream & operator>>(std::istream &, C_scale &);
};

#endif /* C_SCALE_H_ */
