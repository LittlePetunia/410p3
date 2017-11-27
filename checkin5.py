
from pycparser import parse_file

import sys
import numbers

sys.path.append('./pyminic/minic/')
from c_ast_to_minic import *
# from minic_ast import *
from ast import *
sys.path.extend(['.','..'])
import os

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


    
class AllVariables(NodeVisitor):
    
    def visit_ID(self, Id):
        if not Id.name in vas:
            vas.append(Id.name)
            
    def visit_FuncCall(self,funcCall):
        if funcCall.args is not None:
            for exprs, child in funcCall.args.children():
                self.visit(child)


    



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
            if block.lvalue.name not in written:
                written.append(block.lvalue.name)
            next=written
        else:
             #check if there is not only 1 assignment left
            if block.lvalue.name not in written:
                written.append(block.lvalue.name)
            next =transformx(nextblock[0],nextblock[1:],written)
        return Let(transformx(block.lvalue,[],written), transformx(block.rvalue,[],written),next)

    if block.__class__.__name__ == "BinaryOp":
        #check binaryop
        return BinaryOp(block.op,transformx(block.left,[],written),transformx(block.right,[],written))        
    if block.__class__.__name__ =="Constant":
        #check constant
        return Constant(block.type,block.value)

    if block.__class__.__name__ =="If":
        #check if return ternaryop
        ifwritten=[]
        #add if true assignment written vairables
        for i in block.iftrue.block_items:
            if i.__class__.__name__=="Assignment":
                if i.lvalue.name not in ifwritten:
                    ifwritten.append(i.lvalue.name)

        #check whether the iffalse is none,add written variables
        if block.iffalse is not None:
            for i in block.iffalse.block_items:
                if i.__class__.__name__=="Assignment":
                    if i.lvalue.name not in ifwritten:
                        ifwritten.append(i.lvalue.name)
            ifstatemnet = TernaryOp(transformx(block.cond,[],[]),transformx(block.iftrue,[],ifwritten),transformx(block.iffalse,[],ifwritten))
        else:
            #if no else provided ,just use the written variables
            ifstatemnet = TernaryOp(transformx(block.cond,[],[]),transformx(block.iftrue,[],ifwritten),ifwritten)
       
        if nextblock ==[]:
            for i in ifwritten:
                if i not in written:
                    written.append(i)
            next=written
        else:
            for i in ifwritten:
                if i not in written:
                    written.append(i)
            next=transformx(nextblock[0],nextblock[1:],written)
        return Let(ifwritten,ifstatemnet,next)
        
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
   

def simplify(a):
    #rule A variable that is only bound once to a constant can be replaced by this constant in its scope
    #get each line in function body
    lines =str(a).splitlines()

    #search from beginning
    output = ""
    last = written
    used1 = []
    usedvar = []
    usedvalue = []
    writtenlines = []
    for i in range(len(lines) - 1):
        if "Let" in lines[i]:
            used1.append(lines[i].split()[1])
    for i in range(len(lines) - 1):
        if "Let" in lines[i]:
            (var, value) = (lines[i].split()[1], lines[i ].split()[3])
            if used1.count(var) == 1:
                try:
                    float(value)
                    writtenlines.append(i)
                    usedvar.append(var)
                    usedvalue.append(value)
                except ValueError:
                    last = last
    for i in range(len(lines) - 1):
        if "Let" in lines[i]:
            single =0
            a= lines[i]
            for j in range(len(usedvar)):
                if usedvar[j] in lines[i].split("=")[1]:
                    single +=1
                    writtenlines.append(i)
                    a = a.replace(usedvar[j], usedvalue[j]) 
                    
            if single > 0:
                output+=a + "\n"
        if "if" in lines[i]:
            writtenlines.append(i)
            output += "if " +lines[i].split("if")[1] +"\n"
        if not i in writtenlines:
            output += lines[i] + "\n"
    for i in range(len(usedvar)):
        if usedvar[i] not in usedvalue[i]:
            last[last.index(usedvar[i])] = usedvalue[i]
    output += str(last)
    return output



    

    #return lines
if __name__ == '__main__':
    #change input file here by rename the inputfile 
    inputFile = raw_input("type the input c file in input folder (e.g. p3_input3.c) :")
    print(inputFile)
    ast = parse_file('./input/' +inputFile)
    with open('./input/'+inputFile, 'r') as f:
        lineArr=f.read().split('\n')
        print "=======input======="
        for line in lineArr:
            print line
  
    ast2 = transform(ast)
    FunctionDefVisitor2().visit(ast2)
    print("written:")
    print(written)
    print("varaibles:") 
    print(vas)
    FunctionPrototype().__str__()

    # all above is print function prototype
    #--------------------------------------------
    #print function body after transfrom by our own ast
    a=transformx(ast2.ext[0].body,[],[])
    print(a)

    #print simplify str output
    print("=========simplify==============")
    a= simplify(a)
    print(a)
    print("===============================")

