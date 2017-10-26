from pycparser import parse_file
from pycparser.c_ast import *
sys.path.extend(['.','..'])

ast = parse_file('./input/p3_input2.c')



class LHSPrinter2(NodeVisitor):

    def visit_Assignment(self, assignment):

        assignment.lvalue.show()
        print("written varaibles")



class RHSPrinter2(NodeVisitor):

    def visit_Assignment(self, assignment):
        if assignment.rvalue.__class__.__name__ == "ID":
            assignment.rvalue.show()
            print ("varaibles")
    

class BinaryOpPrinter(NodeVisitor):
    #

    def visit_BinaryOp(self, binaryOp):

        if binaryOp.left.__class__.__name__ == "ID":
            binaryOp.left.show()
            print ("varaibles")
        
        if binaryOp.right.__class__.__name__ =="ID":
            binaryOp.right.show()
            print ("varaibles")


class ArrayRefPrinter(NodeVisitor):
    

    def visit_ArrayRef(self, ArrayRef):

        if ArrayRef.name.__class__.__name__ == "ID":
            ArrayRef.name.show()
            print ("varaibles")
        
        if ArrayRef.subscript.__class__.__name__ =="ID":
            ArrayRef.subscript.show()
            print ("varaibles")

class WhilePrinter(NodeVisitor):
 
    def visit_While(self, While):

        if While.cond.__class__.__name__ == "ID":
            While.cond.show()
            print ("varaibles")

class IfPrinter(NodeVisitor):
 
    def visit_If(self, If):

        if If.cond.__class__.__name__ == "ID":
            If.cond.show()
            print ("varaibles")

class ForPrinter(NodeVisitor):
 
    def visit_While(self, For):

        if For.cond.__class__.__name__ == "ID":
            For.cond.show()
            print ("varaibles")

class UnaryPrinter(NodeVisitor):
 
    def visit_While(self, Unary):
            Unary.expr.show()
            print ("written varaibles")
            print ("varaibles")

class DeclPrinter(NodeVisitor):
 
    def visit_While(self, Decl):
            Decl.name.show()
            print ("varaibles")






LHSPrinter2().visit(ast)
RHSPrinter2().visit(ast)
BinaryOpPrinter().visit(ast)
ArrayRefPrinter().visit(ast)
WhilePrinter().visit(ast)
ForPrinter().visit(ast)
IfPrinter().visit(ast)
DeclPrinter().visit(ast)
UnaryPrinter().visit(ast)
#any varaible ID after Assignment symbol is a written variables 
