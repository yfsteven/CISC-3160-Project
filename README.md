# CISC-3160-Project
Interpreter written in Python by Yan Chao Feng

**Usage: python interpreter.py <file>


The following defines a simple language in which a program consists of assignment statements, and each variable is assumed to be of integer type. For simplicity, only operators that produce integer values are included. An assignment that starts with the keyword 'let' defines a single-assignment variable, where the expression on the right-hand side may contain constants or previously defined single-assignment variables only.

Write an interpreter for this language in a programming language of your choice. Given a program, your interpreter should be able to do the following:

detect syntax errors;
report the use of uninitialized variables;
report an error if a let expression contains normal (non-single-assignment) variables; and
if no error is detected, execute the assignments and print the values of all variables after all assignments have been completed.


Program:
	Assignment*

Assignment:
	Identifier = Exp;
    let Identifier = Exp;

Exp: 
	Exp + Term | Exp - Term | Term

Term:
	Term * Fact  | Fact

Fact:
	( Exp ) | - Fact | + Fact | Literal | Identifier

Identifier:
     	Letter [Letter | Digit]*

Letter:
	a|...|z|A|...|Z|_

Literal:
	0 | NonZeroDigit Digit*
		
NonZeroDigit:
	1|...|9

Digit:
	0|1|...|9

Sample inputs and outputs


Input 1


x = 001;


Output 1


error


Input 2


x_2 = 0;


Output 2


x_2 = 0


Input 3


x = 0


y = x;


z = ---(x+y);


Output 3


error


Input 4


let x = 1;


y = 2;


z = ---(x+y)*(x+-y);


Output 4


x = 1


y = 2


z = 3


Input 5


let x = 1;


y = 2;


let z = x+ y;


Output 4


error, normal variables in let expression
