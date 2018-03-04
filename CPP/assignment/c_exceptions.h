//c_exceptions.h by Group 10

#ifndef C_EXCEPTIONS_H_
#define C_EXCEPTIONS_H_
// exception classes
class BadFileException{};

class InvalidNodeTypeException{
public:
	std::string	 str;
	unsigned node_seq;
	InvalidNodeTypeException():node_seq(0) {};
};

class BadHeaderException{
public:
	std::string	str;
	unsigned node_seq;
	BadHeaderException():node_seq(0) {};
};

class BadFooterException{
public:
	std::string	str;
	unsigned node_seq;
	BadFooterException():node_seq(0) {};
};

class InvalidNodeException{
public:
	std::string	str;
	unsigned node_seq;
	InvalidNodeException():node_seq(0) {};
};

#endif /* C_EXCEPTIONS_H_ */
