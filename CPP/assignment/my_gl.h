//my_gl.h by Group 10

#ifndef MY_GL_H_
#define MY_GL_H_

class window {
public:
	window(int argc, char** argv);
	~window(){};

	static void reshape(int w,int h);
	static void keyboard ( unsigned char key, int x, int y );
	static void display();
};


#endif /* MY_GL_H_ */
