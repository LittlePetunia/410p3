
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


    
class AllVariables(NodeVisitor):
    
    def visit_ID(self, Id):
        if not Id.name in vas:
            vas.append(Id.name) 



class FunctionDefVisitor2(NodeVisitor):

    def visit_FuncDef(self, funcdef):
        if funcdef.decl.name != 'main':
            AllVariables().visit(funcdef.body)
            LHSPrinter2().visit(funcdef.body)
            

class FunctionPrototype(NodeVisitor):
    def __init__(self):
        self.vars =vas
        self.written =written

    def __str__(self):
        print("fun block_function("+ ",".join(list(map(str,self.vars))) + ") returns (" + ", ".join(list(map(str, self.written)))) +")"
        


def transformx(block,nextblock,written):
    #check whether it is block list or other class"
    if block.__class__.__name__ == "Block":
        for i in range(len(block.block_items)):
            #linked in next block statemnet
            if (len(block.block_items) >0):
                return transformx(block.block_items[i],block.block_items[i+1:],written)
    if block.__class__.__name__ =="Assignment":
        
        if nextblock ==[]:
            #add written variable as the output in let format
            next=written+[block.lvalue]
            next=[node.name for node in next]
       
        else:
             #check if there is not only 1 assignment left
            next =transformx(nextblock[0],nextblock[1:],written+[block.lvalue])
        return Let(transformx(block.lvalue,[],written), transformx(block.rvalue,[],written),next)

    if block.__class__.__name__ == "BinaryOp":
        #check binaryop
        return BinaryOp(block.op,transformx(block.left,[],written),transformx(block.right,[],written))        
    if block.__class__.__name__ =="Constant":
        #check constant
        return Constant(block.type,block.value)

    if block.__class__.__name__ =="If":
        #check if return ternaryop
        return TernaryOp(transformx(block.cond,[],written),transformx(block.iftrue,[],written),transformx(block.iffalse,[],written)) 
    if block.__class__.__name__ =="ID":
        #checkk id
        return ID(block.name)

    if block.__class__.__name__ =="ArrayRef":
        #check arrayref
        return ArrayRef(transformx(block.name,[],written),transformx(block.subscript,[],written))
    if block.__class__.__name__ =="FuncCall":
        #check functioncall return function call str
        args=[]
        for i in block.args.exprs:
            args.append(transformx(i,[],written))
        return FuncCall(transformx(block.name,[],written),args)
   


if __name__ == '__main__':
    #change input file here by rename the inputfile 
    ast = parse_file('./input/p3_input7.c')
    ast2 = transform(ast)
    FunctionDefVisitor2().visit(ast2)
    print("written:")
    print(written)
    print("varaibles:") 
    print(vas)
    FunctionPrototype().__str__()

    # all above is print function prototype
    #--------------------------------------------
    #print function body
    print(transformx(ast2.ext[0].body,[],[]))
