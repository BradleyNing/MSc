//c_node.h by Group 10

#ifndef C_NODE_H_
#define C_NODE_H_
#include <fstream>

// abstract node class
class C_node{
public:
	virtual void draw()=0;
	virtual ~C_node(){};
	void checkheader(std::istream &);
	void checkfooter(std::istream &);
};
#endif /* C_NODE_H_ */
