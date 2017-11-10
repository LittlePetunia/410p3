from pycparser import parse_file

import sys

sys.path.append('./pyminic/minic/')
from c_ast_to_minic import *
# from minic_ast import *
from ast import *
sys.path.extend(['.','..'])



if __name__ == '__main__':
    ast = parse_file('./input/p3_input4.c')
    ast2 = t(ast)