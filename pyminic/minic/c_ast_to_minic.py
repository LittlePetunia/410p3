from __future__ import print_function
from pycparser import c_ast, parse_file
import minic_ast as mc
from mutils import lmap


# In the transformation process, all the nodes will receive an id for
# hashing purposes. This will be used in the analysis.
sid = 0


def get_new_id():
    global sid
    sid += 1
    return sid


def set_sid(i):
    global sid
    sid = i


# Assignments are all converted into assignments using the '=' operator.
# All assignments using other operators are converted into assignments
# using the '=' and the expression on the right hand side is a binary
# expression such that the assignment has the same semantics.
def of_assignment(orig):
    lvalue = transform(orig.lvalue)
    if orig.rvalue is not None:
        rvalue = transform(orig.rvalue)
    else:
        rvalue = None

    final_rvalue = {
        '=': rvalue,
        '+=': mc.BinaryOp('+', lvalue, rvalue, nid=get_new_id()),
        '-=': mc.BinaryOp('-', lvalue, rvalue, nid=get_new_id()),
        '*=': mc.BinaryOp('*', lvalue, rvalue, nid=get_new_id()),
        '/=': mc.BinaryOp('/', lvalue, rvalue, nid=get_new_id()),
        '%=': mc.BinaryOp('%', lvalue, rvalue, nid=get_new_id()),
        '^=': mc.BinaryOp('^', lvalue, rvalue, nid=get_new_id()),
        '|=': mc.BinaryOp('|', lvalue, rvalue, nid=get_new_id()),
        '>>=': mc.BinaryOp('>>', lvalue, rvalue, nid=get_new_id()),
        '<<=': mc.BinaryOp('<<', lvalue, rvalue, nid=get_new_id()),
        '&=': mc.BinaryOp('&', lvalue, rvalue, nid=get_new_id()),
        '++': mc.BinaryOp('+', lvalue, mc.Constant('int', '1'), nid=get_new_id()),
        '--': mc.BinaryOp('-', lvalue, mc.Constant('int', '1'), nid=get_new_id()),
    }.get(orig.op, mc.EmptyStatement())

    return mc.Assignment(lvalue, final_rvalue, coord=orig.coord, nid=get_new_id())


# PyCParser represents increment and decrement as unary operations, we convert them
# to assignments. Other unary operators are kept as is.
def maybe_special_unary(orig):
    return {
        'p--': (lambda x: mc.Assignment(x, mc.BinaryOp('-', x, mc.Constant('int', '1')), nid=get_new_id())),
        'p++': (lambda x: mc.Assignment(x, mc.BinaryOp('+', x, mc.Constant('int', '1')), nid=get_new_id())),
        '--': (lambda x: mc.Assignment(x, mc.BinaryOp('-', x, mc.Constant('int', '1')), nid=get_new_id())),
        '++': (lambda x: mc.Assignment(x, mc.BinaryOp('+', x, mc.Constant('int', '1')), nid=get_new_id()))
    }.get(orig.op, lambda x: mc.UnaryOp(orig.op, x, coord=orig.coord, nid=get_new_id()))(transform(orig.expr))


# Checks that the original construct is a value, a not any another construct. It helps
# in checking that we have terminal symbols at the right places.
def v(orig):
    if isinstance(orig, str) or isinstance(orig, int) or isinstance(orig, float) \
            or isinstance(orig, bool) or orig is None:
        return orig
    else:
        print("Unexpected type for value %r" % orig)
        raise TypeError


def tmap(x):
    if isinstance(x, list):
        return lmap(transform, x)
    else:
        return transform(x)


class ErrorUnsupportedConstruct(TypeError):
    def __init__(self, construct):
        self.messsage = "Unsupported construct %s" % construct


# If there is no match case in the dictionary style switch, then it means it is a construct
# that is not supported in minic.
def unsupported(y):
    if y is None:
        return None
    else:
        raise ErrorUnsupportedConstruct(y)


# The main transformer function. This is close to a mapping for PyCparser AST nodes to Minic nodes, except
# that there are less constructs and we have to transform assignments and unary operators.
def transform(x):
    return {
        c_ast.ArrayDecl: (lambda orig: mc.ArrayDecl(transform(orig.type), orig.dim, coord=orig.coord, nid=get_new_id())),
        c_ast.ArrayRef: (lambda orig: mc.ArrayRef(transform(orig.name), transform(orig.subscript), coord=orig.coord, nid=get_new_id())),
        c_ast.Assignment: (lambda orig: of_assignment(orig)),
        c_ast.BinaryOp: (lambda orig: mc.BinaryOp(v(orig.op), transform(orig.left), transform(orig.right),
                                                  coord=orig.coord, nid=get_new_id())),
        c_ast.Compound: (lambda orig: mc.Block(lmap(transform, orig.block_items), coord=orig.coord, nid=get_new_id())),
        c_ast.Constant: (lambda orig: mc.Constant(transform(orig.type), v(orig.value), coord=orig.coord, nid=get_new_id())),
        c_ast.Decl: (lambda orig: mc.Decl(transform(orig.name), transform(orig.funcspec), transform(orig.type),
                                          transform(orig.init), coord=orig.coord, nid=get_new_id())),
        c_ast.DeclList: (lambda orig: mc.DeclList(tmap(orig.decls), coord=orig.coord, nid =get_new_id())),
        c_ast.DoWhile: (lambda orig: mc.DoWhile(transform(orig.cond), transform(orig.stmt), coord=orig.coord,
                                                nid=get_new_id())),
        c_ast.EmptyStatement: (lambda orig: mc.EmptyStatement(coord=orig.coord, nid=get_new_id())),
        c_ast.ExprList: (lambda orig: mc.ExprList(tmap(orig.exprs), coord=orig.coord, nid=get_new_id())),
        c_ast.FileAST: (lambda orig: mc.FileAST(lmap(transform, orig.ext), coord=orig.coord, nid=get_new_id())),
        c_ast.For: (lambda orig: mc.For(transform(orig.init), transform(orig.cond), transform(orig.next),
                                        transform(orig.stmt), coord=orig.coord, nid=get_new_id())),
        c_ast.FuncCall: (lambda orig: mc.FuncCall(transform(orig.name), tmap(orig.args), coord=orig.coord, nid=get_new_id())),
        c_ast.FuncDecl: (lambda orig: mc.FuncDecl(tmap(orig.args), transform(orig.type), coord=orig.coord, nid=get_new_id())),
        c_ast.FuncDef: (lambda orig: mc.FuncDef(transform(orig.decl), tmap(orig.param_decls), transform(orig.body),
                                                coord=orig.coord, nid=get_new_id())),
        c_ast.ID: (lambda orig: mc.ID(v(orig.name), coord=orig.coord, nid=get_new_id())),
        c_ast.IdentifierType: (lambda orig: mc.IdentifierType(tmap(orig.names), nid=get_new_id())),
        c_ast.If: (lambda orig: mc.If(transform(orig.cond), transform(orig.iftrue), transform(orig.iffalse),
                                      coord=orig.coord, nid=get_new_id())),
        c_ast.InitList: (lambda orig: mc.InitList(tmap(orig.exprs), coord=orig.coord, nid=get_new_id())),
        c_ast.NamedInitializer: (lambda orig: mc.NamedInitializer(v(orig.name), transform(orig.expr),
                                                                  coord=orig.coord, nid=get_new_id())),
        c_ast.ParamList: (lambda orig: mc.ParamList(tmap(orig.params), coord=orig.coord, nid=get_new_id())),
        c_ast.PtrDecl: (lambda orig: mc.PtrDecl(transform(orig.type), coord=orig.coord, nid=get_new_id())),
        c_ast.Return: (lambda orig: mc.Return(transform(orig.expr), coord=orig.coord, nid=get_new_id())),
        c_ast.TernaryOp: (lambda orig: mc.TernaryOp(transform(orig.cond), transform(orig.iftrue),
                                                    transform(orig.iffalse), coord=orig.coord, nid=get_new_id())),
        c_ast.Typename: (lambda orig: mc.Typename(v(orig.name), transform(orig.type), coord=orig.coord, nid=get_new_id())),
        c_ast.TypeDecl: (lambda orig: mc.TypeDecl(v(orig.declname), transform(orig.type), coord=orig.coord, nid=get_new_id())),
        c_ast.UnaryOp: (lambda orig: maybe_special_unary(orig)),
        c_ast.While: (lambda orig: mc.While(transform(orig.cond), transform(orig.stmt), coord=orig.coord, nid=get_new_id())),
        str: (lambda orig: orig),
        int: (lambda orig: orig),
        float: (lambda orig: orig),
        list: (lambda orig: tmap(orig)),
    }.get(x.__class__, lambda y: unsupported(y))(x)


def minic_parse_file(filename):
    return transform(parse_file(filename))


def wrap(filename):
    infile = open(filename, 'r')
    outfilename = filename+'_wrap.c'
    outfile = open(outfilename, 'w')
    outfile.write("void main(){\n")
    for line in infile:
        outfile.write("\t" + line)
    outfile.write("}\n")
    outfile.close()
    infile.close()
    return outfilename


def minic_parse_wrap_file(filename):
    return transform(parse_file(wrap(filename)))