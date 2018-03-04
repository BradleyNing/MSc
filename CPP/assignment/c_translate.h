//c_translate.h by Group 10

#ifndef C_TRANSLATE_H_
#define C_TRANSLATE_H_

#include <fstream>
#include "c_node.h"

//translate class inherits from abstract node class
class C_translate:public C_node {
private:
	float trans[3];

public:
	void  draw();
	C_translate();
	~C_translate(){};
	friend std::istream & operator>>(std::istream &, C_translate &);
};

#endif /* C_TRANSLATE_H_ */
