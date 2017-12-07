
from pycparser import parse_file

import sys
import numbers
import copy
sys.path.append('./pyminic/minic/')
from c_ast_to_minic import *
# from minic_ast import *
from ast import *

sys.path.extend(['.','..'])
import os

written_visit=[]
vas=[]


"""

visit the node of the AST body with left hand side, 
first check if LHS is array ref object, then get the 
array name. otherwise the name of the ID.  

"""
class LHSPrinter(NodeVisitor):

    def __init__(self):
        self.written=[]

    def visit_Assignment(self, assignment):
        if (assignment.lvalue.__class__.__name__ == "ArrayRef"):
            if (assignment.lvalue.name.name not in self.written):
                self.written.append(assignment.lvalue.name.name)

        elif (assignment.lvalue.name not in self.written):
            self.written.append(assignment.lvalue.name)
        
       

"""

visit the node of the AST body with left hand side, 
first check if LHS is array ref object, then get the 
array name. otherwise the name of the ID. instead using global
list for print the written variables  
"""
class LHSPrinter2(NodeVisitor):

    def visit_Assignment(self, assignment):
        if (assignment.lvalue.__class__.__name__ == "ArrayRef"):
            if (assignment.lvalue.name.name not in written_visit):
                written_visit.append(assignment.lvalue.name.name)

        elif (assignment.lvalue.name not in written_visit):
            written_visit.append(assignment.lvalue.name)
       
    

    def visit_Decl(self, decl):
        # If the declaration has an init field
        if decl.init is not None:
            # Show the name of the value initialized
            if (decl.name not in written_visit):
                written_visit.append(decl.name)

"""
visit the node of the AST body with all ID name,but remove 
with ID name of Func Call. print all variables used in the 
body

"""
    
class AllVariables(NodeVisitor):
    
    def visit_ID(self, Id):
        if not Id.name in vas:
            vas.append(Id.name)
            
    def visit_FuncCall(self,funcCall):
        if funcCall.args is not None:
            for exprs, child in funcCall.args.children():
                self.visit(child)


"""
call the visitor function body and only visit the method 
that is not main in C file.(we dont care main method)
all buildin input will be wrapped with void test method`
"""

class FunctionDefVisitor2(NodeVisitor):

    def visit_FuncDef(self, funcdef):
        if funcdef.decl.name != 'main':
            AllVariables().visit(funcdef.body)
            LHSPrinter2().visit(funcdef.body)
            
"""
str print of function prototype
"""

class FunctionPrototype(NodeVisitor):
    def __init__(self):
        self.vars =vas
        self.written_visit =written_visit

    def __str__(self):
        return ("fun block_function("+ ",".join(list(map(str,self.vars))) + ") returns (" + ", ".join(list(map(str, self.written_visit)))) +")"

"""
Transform miniC ast into our own AST with Let and Let rec binding
"""     
def transformx(block,nextblock,written,loopnum):
    #check whether it is block list or other class"
    if block.__class__.__name__ == "Block":
        for i in range(len(block.block_items)):
            #linked in next block statemnet
            if (len(block.block_items) >0):
                return transformx(block.block_items[i],block.block_items[i+1:],written,loopnum)
    if block.__class__.__name__ =="Assignment":
        
        if nextblock ==[]:
            #add written variable as the output in let format
            if (block.lvalue.__class__.__name__ == "ArrayRef"):
                if (block.lvalue.name.name not in written):
                    written.append(block.lvalue.name.name)
            elif block.lvalue.name not in written:
                written.append(block.lvalue.name)
            next=written
        else:
             #check if there is not only 1 assignment left
            if (block.lvalue.__class__.__name__ == "ArrayRef"):
                if (block.lvalue.name.name not in written):
                    written.append(block.lvalue.name.name)
            elif block.lvalue.name not in written:
                written.append(block.lvalue.name)
            next =transformx(nextblock[0],nextblock[1:],written,loopnum)
        return Let(transformx(block.lvalue,[],written,loopnum), transformx(block.rvalue,[],written,loopnum),next)

    if block.__class__.__name__ == "BinaryOp":
        #check binaryop
        return BinaryOp(block.op,transformx(block.left,[],written,loopnum),transformx(block.right,[],written,loopnum))        
    if block.__class__.__name__ =="Constant":
        #check constant
        return Constant(block.type,block.value)

    if block.__class__.__name__ =="If":
        #check if return ternaryop
        ifwritten=[]
        #add if true assignment written vairables
        for i in block.iftrue.block_items:
            if i.__class__.__name__=="Assignment":
                if (i.lvalue.__class__.__name__ == "ArrayRef"):
                    if (i.lvalue.name.name not in ifwritten):
                        ifwritten.append(i.lvalue.name.name)

                elif i.lvalue.name not in ifwritten:
                    ifwritten.append(i.lvalue.name)

        #check whether the iffalse is none,add written variables
        if block.iffalse is not None:
            for i in block.iffalse.block_items:
                if i.__class__.__name__=="Assignment":
                    if (i.lvalue.__class__.__name__ == "ArrayRef"):
                        if (i.lvalue.name.name not in ifwritten):
                            ifwritten.append(i.lvalue.name.name)

                    elif i.lvalue.name not in ifwritten:
                        ifwritten.append(i.lvalue.name)
            ifstatemnet = TernaryOp(transformx(block.cond,[],[],loopnum),transformx(block.iftrue,[],ifwritten,loopnum),transformx(block.iffalse,[],ifwritten,loopnum),loopnum)
        else:
            #if no else provided ,just use the written variables
            ifstatemnet = TernaryOp(transformx(block.cond,[],[],loopnum),transformx(block.iftrue,[],ifwritten,loopnum),ifwritten,loopnum)
       
        if nextblock ==[]:
            for i in ifwritten:
                if i not in written:
                    written.append(i)
            next=written
        else:
            for i in ifwritten:
                if i not in written:
                    written.append(i)
            next=transformx(nextblock[0],nextblock[1:],written,loopnum)
        return Let(ifwritten,ifstatemnet,next)
        
    if block.__class__.__name__ =="ID":
        #checkk id
        return ID(block.name)

    if block.__class__.__name__ =="ArrayRef":
        #check arrayref
        return ArrayRef(transformx(block.name,[],written,loopnum),transformx(block.subscript,[],written,loopnum))
    if block.__class__.__name__ =="FuncCall":
        #check functioncall return function call str
        args=[]
        for i in block.args.exprs:
            args.append(transformx(i,[],written,loopnum))
        return FuncCall(transformx(block.name,[],written,loopnum),args)
    if block.__class__.__name__ =="For":
        
        #always add init assignment into written variables
        a= LHSPrinter()
        a.visit(block)
        forwritten = a.written
        stmt = transformx(Block(block.stmt.block_items+[block.next]),[],["loop"+str(loopnum)],loopnum+1)

        cond = transformx(block.cond,[],[],loopnum)
        makeif = TernaryOp(cond,stmt,forwritten)
        

        if nextblock ==[]:
            for i in forwritten:
                if i not in written:
                    written.append(i)
            next=written
            next.append("loop"+str(loopnum))
        else:
            for i in forwritten:
                if i not in written:
                    written.append(i)
            next=transformx(nextblock[0],nextblock[1:],written,loopnum+1)
        #add init to the very first
        
        letre =Letrec('loop'+str(loopnum), forwritten, makeif, next)
        letinit = Let(forwritten,letre,forwritten)

        return transformx(Block([block.init]+[letinit]),[],[],loopnum)

        
    if block.__class__.__name__ =="While":
        a= LHSPrinter()
        a.visit(block)
        whilewritten = a.written

        stmt = transformx(block.stmt,[],[],loopnum+1)
        cond = transformx(block.cond,[],[],loopnum)
        makeif = TernaryOp(cond,stmt,whilewritten)
        
        if nextblock ==[]:
            for i in whilewritten:
                if i not in written:
                    written.append(i)
            next=written
            next.append("loop"+str(loopnum))
        else:
            for i in whilewritten:
                if i not in written:
                    written.append(i)

            next=transformx(nextblock[0],nextblock[1:],written,loopnum+1)

        letre = Letrec('loop'+str(loopnum), whilewritten, makeif, next)
        letinit = Let(whilewritten,letre,whilewritten)

        return letinit

    if block.__class__.__name__ =="Let" or block.__class__.__name__ =="Letrec":
        return block

"""

make and create simple C file with sample input.
Add void test method into file as the main method.
"""  

def makec(file):

    f=open('./input/'+file,'r')
    input = f.read()
    f.close()
    
    filename =file +".c"

    f=open('./input/'+filename,'w+')
    f.write("void test(){\n" +input +"\n}")
    f.close()

    return filename

"""

simplify the output after transform. remove useless let binding and replace  constant var that only use once.

"""    
def simplify(a):
    #rule A variable that is only bound once to a constant can be replaced by this constant in its scope
    #get each line in function body
    lines =str(a).splitlines()

    #search from beginning
    output = ""
    last = written_visit
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
        if not i in writtenlines:
            output += lines[i] + "\n"
    for i in range(len(usedvar)):
        if usedvar[i] not in usedvalue[i]:
            last[last.index(usedvar[i])] = usedvalue[i]
    output += str(tuple(last))
    return output

if __name__ == '__main__':
    #change input file here by rename the inputfile 
    inputFile = raw_input("type the input file in input folder (e.g. p3_input6) :")

    File = makec(inputFile)
    print(File)
    ast = parse_file('./input/' +File)
    with open('./input/'+File, 'r') as f:
        lineArr=f.read().split('\n')
        print "=======input======="
        for line in lineArr:
            print line
  
    ast2 = transform(ast)
    FunctionDefVisitor2().visit(ast2)
    print("=============variables========")
    print("written:")
    print(written_visit)
    print("variables:") 
    print(vas)
    print("=============function==========")
    print FunctionPrototype()

    # all above is print function prototype
    #--------------------------------------------
    #print function body after transfrom by our own ast
    print("=========transform ===========")
    a=transformx(ast2.ext[0].body,[],[],0)
    print a

    print("=========simplify===========")

    print simplify(a)