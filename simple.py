from pycparser import parse_file
from pycparser.c_ast import *
sys.path.extend(['.','..'])

ast = parse_file('./input/p3_input1.c')

class LHSPrinter(NodeVisitor):
    # The type of node a function visits depends on its name
    # Here we want to do something special when the visitor
    # encounters an Assignment node (look at the c_ast.py to
    # see how it is defined).
    def visit_Assignment(self, assignment):
        # The assignment node has a 'lvalue' field, we just
        # want to show it here
        assignment.lvalue.show()

    # And for all the other node types, the visitor will just
    # go recursively through them without doing anything.

# Let us visit the whole ast. For that you need to call the
# visit method of an instance of LHSPrinter on the ast TEST
# lhsp = LHSPrinter()
# lhsp.visit(ast)
# Alternatively, you write directly:
# LHSPrinter().visit(ast)
# since we don't care about the results, it is just outputs.

# Now this is not nicely presented. Let us visit the different function nodes,
# and if the function is not the main function, then print the left-hand side
# values in its body.


class FunctionDefVisitor(NodeVisitor):
    # Now we are visiting function definitions, which are represented
    # by FuncDef nodes with the following (interesting) fields:
    #  'decl', 'param_decls', 'body'
    # And the 'decl' will be a Decl node with the fields (from c_ast.py);
    # class Decl(Node):
    # __slots__ = ('name', 'quals', 'storage', 'funcspec', 'type', 'init', ...
    # where 'name' will be the function name in our case.
    def visit_FuncDef(self, funcdef):
        # Check that we are not in the main function
        if funcdef.decl.name != 'main':
            print('\nIn function %s on the left hand sides:' % funcdef.decl.name)
            # Then we call the lhs-printer on the body of the function
            LHSPrinter().visit(funcdef.body)
        else:
            print("\nWe don't care about main.")

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

    def visit_Decl(self, decl):
        # If the declaration has an init field
        if decl.init is not None:
            # Show the name of the value initialized
            print ("ID: %s" , decl.name)

# Be careful about the representation of the DATA in the AST. You noticed that
# here the declaration has a name, which is a string, but the assignment's left
# hand side is not a name but another node, on which we call 'show()'


class FunctionDefVisitor2(NodeVisitor):

    def visit_FuncDef(self, funcdef):
        if funcdef.decl.name != 'main':
            print('\nIn function %s on the left hand sides:' % funcdef.decl.name)
            LHSPrinter2().visit(funcdef.body)
        else:
            print ("\nWe don't care about main.")

# Now we can call it on the ast TEST
# FunctionDefVisitor2().visit(ast)


# 2 - Analyzing programs

# Now let us do something more interesting than printing values
# with our visitor.
# We can add memory to it, and operate on it as we visit the nodes
# of the AST.
# We start with a simple first example. The visitor remembers the variables
# appearing on the left hand side of an assignment.
# This can be seen as a 'write-set' analysis, where the program doesn't have side
# effects and the only way to write in variables is to assign something to them.

# When a visitor has visited a code block, it should have the set of written variables
# in its memory

class WriteSetVisitor(NodeVisitor):
    def __init__(self):
        # The 'memory' of the node: the set of variables we are writing in.
        self.writeset = set()

    # What we do when we visit an assignment.
    def visit_Assignment(self, assignment):
        # Add the lvalue if is is an ID node
        # we don't care about other types of lvalues in this
        # very simple analysis.

        if isinstance(assignment.lvalue, ID):
            self.writeset.add(assignment.lvalue.name)

    # What happens when we visit a declaration.
    # Similar to the previous example: we add the variable name
    def visit_Decl(self, decl):
        if decl.init is not None:
            self.writeset.add(decl.name)

    # Here we have a single visitor looking in the whole tree. But you
    # might sometimes need to handle merge cases (when you have to
    # look in a specific way into different branches)
    # For example, we could have added the following function
    def visit_If(self, ifnode):
        wif = WriteSetVisitor()
        welse = WriteSetVisitor()
        wif.visit(ifnode.iftrue)
        welse.visit(ifnode.iffalse)
        self.writeset.union(wif.writeset.union(welse.writeset.union()))

    # In this case it is not really interesting, the visitor would have added
    # the variables anyway, but it could be in other cases.

# We can wrap this in a function visitor
class FuncWriteSetVisitor(NodeVisitor):
    def __init__(self):
        # The dict associates function names to write sets:
        self.writesets = {}

    def visit_FuncDef(self, funcdef):
        # Create a WriteSet visitor for the body of the function
        wsv = WriteSetVisitor()
        # Execute it on the function's body
        wsv.visit(funcdef.body)
        # Now it contains the writeset of the function
        self.writesets[funcdef.decl.name] = wsv.writeset

# TEST
# fws = FuncWriteSetVisitor()
# fws.visit(ast)
# # Now print the write sets for each function:
# for fname, writeset in fws.writesets.items():
#     # Print 'function string' writes in 'set representation'
#     print ("%s writes in %r" % (fname, writeset))


# 3 - Transforming trees

# To transform a tree, you just need to modify the nodes as you go.
# For example, let us write a NodeVisitor that replaces every
# initialization with 0 by an initialization with -1:
ast2 = ast


class ReplaceZero(NodeVisitor):
    def visit_Decl(self, decl):
        # We use 'and' and not '&' here because we can check the second part
        # of the condition only when the first is true.
        if decl.init is not None and decl.init.value == '0':
            decl.init.value = '-1'

ReplaceZero().visit(ast2)
ast2.ext[0].body.show()