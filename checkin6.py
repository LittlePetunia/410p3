
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
            if block.lvalue.name not in written:
                written.append(block.lvalue.name)
            next=written
        else:
             #check if there is not only 1 assignment left
            if block.lvalue.name not in written:
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
                if i.lvalue.name not in ifwritten:
                    ifwritten.append(i.lvalue.name)

        #check whether the iffalse is none,add written variables
        if block.iffalse is not None:
            for i in block.iffalse.block_items:
                if i.__class__.__name__=="Assignment":
                    if i.lvalue.name not in ifwritten:
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
        forwritten =[]
        #always add init assignment into written variables
        forwritten.append(block.init.lvalue.name)

        for i in block.stmt.block_items:
            if i.__class__.__name__ =="Assignment":
                if i.lvalue.name not in forwritten:
                    forwritten.append(i.lvalue.name)

        stmt = transformx(Block(block.stmt.block_items+[block.next]),[],[],loopnum+1)
        letinit = Let(forwritten,stmt,["loop"+str(loopnum)] +forwritten)


        cond = transformx(block.cond,[],[],loopnum)
        makeif = TernaryOp(cond,letinit,forwritten)

        if nextblock ==[]:
            for i in forwritten:
                if i not in written:
                    written.append(i)
            next=written
        else:
            for i in forwritten:
                if i not in written:
                    written.append(i)
            next=transformx(nextblock[0],nextblock[1:],written,loopnum+1)
        #add init to the very first
        return transformx(Block([block.init]+[Letrec('loop'+str(loopnum), forwritten, makeif, next)]),[],[])

        
    if block.__class__.__name__ =="While":
        whilewritten =[]
        for i in block.stmt.block_items:
            if i.__class__.__name__ =="Assignment":
                if i.lvalue.name not in whilewritten:
                    whilewritten.append(i.lvalue.name)


        stmt = transformx(block.stmt,[],[],loopnum+1)
        letinit = Let(whilewritten,stmt,["loop"+str(loopnum)] +whilewritten)

        cond = transformx(block.cond,[],[],loopnum)
        makeif = TernaryOp(cond,letinit,whilewritten)

        if nextblock ==[]:
            for i in whilewritten:
                if i not in written:
                    written.append(i)
            next=written
        else:
            for i in whilewritten:
                if i not in written:
                    written.append(i)

            next=transformx(nextblock[0],nextblock[1:],written,loopnum+1)

        return transformx(Letrec('loop'+str(loopnum), whilewritten, makeif, next),[],[],loopnum)


    if block.__class__.__name__ =="Let" or block.__class__.__name__ =="Letrec":
        return block


def makec(file):

    f=open('./input/'+file,'r')
    input = f.read()
    f.close()
    
    filename =file +".c"

    f=open('./input/'+filename,'w+')
    f.write("void test(){\n" +input +"\n}")
    f.close()

    return filename
    

    #return lines
if __name__ == '__main__':
    #change input file here by rename the inputfile 
    inputFile = raw_input("type the input file in input folder (e.g. p3_input3) :")
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
    print("written:")
    print(written)
    print("varaibles:") 
    print(vas)
    FunctionPrototype().__str__()

    # all above is print function prototype
    #--------------------------------------------
    #print function body after transfrom by our own ast
    a=transformx(ast2.ext[0].body,[],[],0)
    print(a)


    
    print("===============================")

