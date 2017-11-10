
from pycparser import parse_file

import sys

sys.path.append('./pyminic/minic/')
from c_ast_to_minic import *
# from minic_ast import *
from ast import *
sys.path.extend(['.','..'])

written=[]
vas=[]

class LHSPrinter2(NodeVisitor):

    def visit_Assignment(self, assignment):
        if (assignment.lvalue.name not in written):
            written.append(assignment.lvalue.name)
        if (assignment.lvalue.name not in vas):
            vas.append(assignment.lvalue.name)

    def visit_Decl(self, decl):
        # If the declaration has an init field
        if decl.init is not None:
            # Show the name of the value initialized
            if (decl.name not in written):
                written.append(decl.name)
            if (decl.name not in vas):
                vas.append(decl.name)
            



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
            if (binaryOp.right.name not in vas):
                vas.append(binaryOp.right.name)


class ArrayRefPrinter(NodeVisitor):
    

    def visit_ArrayRef(self, ArrayRef):

        if ArrayRef.name.__class__.__name__ == "ID":
           if (ArrayRef.name.name not in vas):
                vas.append(ArrayRef.name.name)
        
        if ArrayRef.subscript.__class__.__name__ =="ID":
            if (ArrayRef.subscript.name not in vas):
                vas.append(ArrayRef.subscript.name)

class WhilePrinter(NodeVisitor):
 
    def visit_While(self, While):
        if While.cond.__class__.__name__ == "ID":
            if (While.cond.name not in vas):
                vas.append(While.cond.name)

class IfPrinter(NodeVisitor):
 
    def visit_If(self, If):

        if If.cond.__class__.__name__ == "ID":
            if (If.cond.name not in vas):
                vas.append(If.cond.name)

class ForPrinter(NodeVisitor):
 
    def visit_While(self, For):

        if For.cond.__class__.__name__ == "ID":
            if (For.cond.name not in vas):
                vas.append(For.cond.name)




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

class FunctionPrototype(NodeVisitor):
    def __init__(self):
        self.vars =vas
        self.written =written

    def __str__(self):
        print("fun block_function("+ ",".join(list(map(str,self.vars))) + ") returns " + ", ".join(list(map(str, self.written))))
        


def transform(block,nextblock):

    if block.__class__.__name__ == "Block":
        for i in range(len(block.block_items)):
            if i == len(block.block_items) -1:
                return transform(block.block_items[i],[])
            else:
                return transform(block.block_items[i],block.block_items[i+1])
    if block.__class__.__name__ =="Assignment":
        
        return Let(transform(block.lvalue,[]), transform(block.rvalue,[]),transform(nextblock,[]))

    if block.__class__.__name__ == "BinaryOp":

        return BinaryOp(block.op,transform(block.left,[]),transform(block.right,[]))        
    if block.__class__.__name__ =="Constant":

        return Constant(block.type,block.value)

    if block.__class__.__name__ =="If":

        return TernaryOp(transform(block.cond,[]),transform(block.iftrue,[]),transform(block.iffalse,[])) 
    if block.__class__.__name__ =="ID":

        return ID(block.name)

    if block.__class__.__name__ =="ArrayRef":

        return ArrayRef(transform(block.name,[]),transform(block.subscript,[]))
    if block.__class__.__name__ =="FuncCall":
        return FuncCall(trannsform(block.name,[]), transform(block.args),[])


if __name__ == '__main__':
    ast = parse_file('./input/p3_input4.c')
    ast2 = t(ast)
    FunctionDefVisitor2().visit(ast2)
    print("written:")
    print(written)
    print("varaibles:") 
    print(vas)
    FunctionPrototype().__str__()
    print(transform(ast2.ext[0].body,[]))
