from pycparser import parse_file

import sys

sys.path.append('./pyminic/minic/')
from c_ast_to_minic import *
from minic_ast import *
sys.path.extend(['.','..'])

ast = parse_file('./input/p3_input2.c')
ast2 = t(ast)
written=[]
vas=[]

class LHSPrinter2(NodeVisitor):

    def visit_Assignment(self, assignment):
        if (assignment.lvalue.name not in written):
            written.append(assignment.lvalue.name)

    def visit_Decl(self, decl):
        # If the declaration has an init field
        if decl.init is not None:
            # Show the name of the value initialized
            if (decl.name not in written):
                written.append(decl.name)
            



class RHSPrinter2(NodeVisitor):

    def visit_Assignment(self, assignment):
        if assignment.rvalue.__class__.__name__ == "ID":
            if (assignment.rvalue.name not in vas):
                vas.append(assignment.rvalue.name)
    

class BinaryOpPrinter(NodeVisitor):


    def visit_BinaryOp(self, binaryOp):

        if binaryOp.left.__class__.__name__ == "ID":
            if (binaryOp.left.name not in vas):
                vas.append(binaryOp.left.name)
        
        if binaryOp.right.__class__.__name__ =="ID":
            if (binaryOp.left.name not in vas):
                vas.append(binaryOp.left.name)


class ArrayRefPrinter(NodeVisitor):
    

    def visit_ArrayRef(self, ArrayRef):

        if ArrayRef.name.__class__.__name__ == "ID":
           if (ArrayRef.name not in vas):
                vas.append(ArrayRef.name)
        
        if ArrayRef.subscript.__class__.__name__ =="ID":
            if (ArrayRef.subscript not in vas):
                vas.append(ArrayRef.subscript)

class WhilePrinter(NodeVisitor):
 
    def visit_While(self, While):
        if While.cond.__class__.__name__ == "ID":
            if (While.cond not in vas):
                vas.append(While.cond)

class IfPrinter(NodeVisitor):
 
    def visit_If(self, If):

        if If.cond.__class__.__name__ == "ID":
            if (If.cond not in vas):
                vas.append(If.cond)

class ForPrinter(NodeVisitor):
 
    def visit_While(self, For):

        if For.cond.__class__.__name__ == "ID":
            if (For.cond not in vas):
                vas.append(For.cond)







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


if __name__ == '__main__':
    FunctionDefVisitor2().visit(ast2)
    print("written:")
    print(written)
    print("varaibles:") 
    print(vas)
#any varaible ID after Assignment symbol is a written variables 
