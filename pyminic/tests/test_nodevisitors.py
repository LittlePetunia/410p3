import unittest
from pycparser import parse_file
import minic.c_ast_to_minic as ctoc
import minic.minic_ast as mast


class TestVisitor(mast.NodeVisitor):

    def __init__(self):
        self.assignment_counter = 0
        self.forl_counter = 0

    def visit_Assignment(self, assignment):
        self.assignment_counter += 1

    def visit_For(self, forl):
        self.forl_counter += 1
        self.generic_visit(forl)


class TestNodeVisit(unittest.TestCase):
    def test_visit(self):
        ast = ctoc.transform(parse_file('./c_files/minic.c'))
        vs = TestVisitor()
        vs.visit(ast)
        self.assertEqual(vs.assignment_counter, 5)
        self.assertEqual(vs.forl_counter, 1)
