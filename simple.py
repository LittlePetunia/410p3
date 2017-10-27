from pycparser import parse_file
from pycparser.c_ast import *
sys.path.extend(['.','..'])

ast = parse_file('./input/p3_input2.c')



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

##class UnaryPrinter(NodeVisitor):
## 
##    def visit_While(self, Unary):
##            Unary.name.show()
##            print ("written varaibles")
##            print ("varaibles")
##
##class DeclPrinter(NodeVisitor):
## 
##    def visit_While(self, Decl):
##            Decl.show()
##            print ("varaibles")


class FunctionDefVisitor2(NodeVisitor):

    def visit_FuncDef(self, funcdef):
        if funcdef.decl.name != 'main':
            LHSPrinter2().visit(funcdef.body)
            RHSPrinter2().visit(funcdef.body)
            BinaryOpPrinter().visit(funcdef.body)
            ArrayRefPrinter().visit(funcdef.body)
            WhilePrinter().visit(funcdef.body)
            ForPrinter().visit(funcdef.body)
            IfPrinter().visit(funcdef.body)
        else:
            print ("\nWe don't care about main.")





FunctionDefVisitor2().visit(ast)

##DeclPrinter().visit(ast)
##UnaryPrinter().visit(ast)
#any varaible ID after Assignment symbol is a written variables 
