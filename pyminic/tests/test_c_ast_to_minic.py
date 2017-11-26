from __future__ import print_function
import unittest
import minic.c_ast_to_minic as ctoc
import minic.minic_ast as mast


class TestConversion1(unittest.TestCase):
    def test_parse_and_convert1(self):
        ast = ctoc.minic_parse_file('./c_files/minic.c')
        self.failUnless(isinstance(ast, mast.FileAST))
        self.assertEqual(len(ast.ext), 2)
        self.failUnless(isinstance(ast.ext[0], mast.FuncDef))

        funcdef_mss = ast.ext[0]
        self.assertEqual(funcdef_mss.decl.name, 'mss')
        mss_body = funcdef_mss.body
        self.assertTrue(isinstance(mss_body, mast.Block))
        self.assertEqual(len(mss_body.block_items), 5)
        self.failUnless(isinstance(mss_body.block_items[0], mast.Decl))
        self.failUnless(isinstance(mss_body.block_items[1], mast.Decl))
        self.failUnless(isinstance(mss_body.block_items[2], mast.Decl))
        self.failUnless(isinstance(mss_body.block_items[3], mast.For))
        forstmt = mss_body.block_items[3]
        self.assertTrue(isinstance(forstmt.next, mast.Assignment))
        self.failUnless(isinstance(mss_body.block_items[4], mast.Return))

        funcdef_main = ast.ext[1]
        self.assertEqual(funcdef_main.decl.name, 'main')
        main_body = funcdef_main.body
        self.assertEqual(len(main_body.block_items), 4)
        self.failUnless(isinstance(main_body.block_items[0], mast.Decl))
        self.failUnless(isinstance(main_body.block_items[1], mast.Decl))
        self.failUnless(isinstance(main_body.block_items[2], mast.Assignment))
        self.failUnless(isinstance(main_body.block_items[3], mast.Return))

    def test_parse_and_convert2(self):
        converted = ctoc.minic_parse_file('./c_files/test2.c')
        self.failUnless(isinstance(converted, mast.FileAST))

    def test_parse_and_convert_constructs(self):
        ast = ctoc.minic_parse_file('./c_files/constructs.c')
        self.failUnless(isinstance(ast, mast.FileAST))