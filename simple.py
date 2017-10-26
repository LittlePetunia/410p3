from pycparser import parse_file
from pycparser.c_ast import *
sys.path.extend(['.','..'])

ast = parse_file('./input/p3_input1.c')



# Now we can call it on the ast TEST
# FunctionDefVisitor().visit(ast)


# Now you might have noticed when we do a declaration with and initial value,
# like this one :
# int sum = 0;
# The visitor didn't print anything. If we want if to print any value that
# is on the left hand side of a '=' sign then we have to handle Decl nodes
# that represent declaration statements.
# So now with our new LHSPrinter


class LHSPrinter2(NodeVisitor):

    def visit_Assignment(self, assignment):

        assignment.lvalue.show()
        print("written varaibles")

    def visit_Decl(self, decl):
        # If the declaration has an init field
        if decl.init is not None:
            # Show the name of the value initialized
            print ("ID: %s" , decl.name)


class RHSPrinter2(NodeVisitor):

    def visit_Assignment(self, assignment):
    	if assignment.rvalue.__class__.__name__ == "ID":
            assignment.rvalue.show()
            print ("varaibles")
        

    def visit_Decl(self, decl):
        # If the declaration has an init field
        if decl.init is not None:
            # Show the name of the value initialized
            print ("ID: %s" , decl.name)

class BinaryOpPrinter(NodeVisitor):
    # The type of node a function visits depends on its name
    # Here we want to do something special when the visitor
    # encounters an Assignment node (look at the c_ast.py to
    # see how it is defined).
    def visit_BinaryOp(self, binaryOp):
        # The assignment node has a 'lvalue' field, we just
        # want to show it here
        binaryOp.left.show()
        binaryOp.right.show()
        print(binaryOp.left.__class__.__name__)
        print(binaryOp.right.__class__.__name__)


LHSPrinter2().visit(ast)
RHSPrinter2().visit(ast)
BinaryOpPrinter().visit(ast)


#any varaible ID after Assignment symbol is a written variables 
