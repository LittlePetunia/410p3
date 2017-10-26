#-----------------------------------------------------------------
# pycparser: tutorial.py
#
# Examples on how to use NodeVisitor to perform some simple analysis.
#
# Victor Nicolet [victorn at cs dot toronto.edu]
# License: BSD
#-----------------------------------------------------------------

from pycparser import parse_file
from pycparser.c_ast import *
sys.path.extend(['.', '..'])

# - 1 Basics: parsing and visiting the AST

# Read and parse the file
ast = parse_file('./input/p3_input3.c')
# Now the 'ast' variables contains the ast we want to work on
# To look at how the ast is built, have a look at the c_ast.py file
# in the pycparser package (../pycparser/c_ast.py)

# For example an Assignment is a superclass of the Node class with the
# following fields:
# - op , the assignment operator, can be '+', '+=', '-=", ...
# - lvalue, the left hand side of the assignment
# - rvalue, the right hand side of the assignment

# Any analysis of the program in our case will be based on visitors.
# Visitors are object that visit the nodes of the abstract syntax tree
# recursively, peforming operation depdending on the node type they
# traverse.

# For example, let us write a visitor that shows the left-hand side values

ast2 = ast


class ReplaceZero(NodeVisitor):
    def visit_Decl(self, decl):
        # We use 'and' and not '&' here because we can check the second part
        # of the condition only when the first is true.
        if decl.init is not None and decl.init.value == '0':
            decl.init.value = '-1'

ReplaceZero().visit(ast2)
ast2.ext[0].body.show()
