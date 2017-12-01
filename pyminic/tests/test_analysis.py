from __future__ import print_function
import sys
sys.path.append("../minic")
import minic.analysis as mana
import unittest
import minic.c_ast_to_minic as ctoc


class TestLoopAnalysis(unittest.TestCase):
    def test_reachingdefs(self):
        ast = ctoc.minic_parse_file('./c_files/loop_analysis.c')
        # Reaching Definitions analysis
        rdefs_analyzer = mana.FuncBodiesAnalysis('ReachingDefinitions')
        rdefs_analyzer.visit(ast)

        # Reaching Definitions analysis
        liveness_analyzer = mana.FuncBodiesAnalysis('LiveVariables')
        liveness_analyzer.visit(ast)


class TestNestedLoops(unittest.TestCase):
    def test_analyze(self):
        ast = ctoc.minic_parse_file('./c_files/nested_loops.c')
        # Reaching Definitions analysis
        rdefs_analyzer = mana.FuncBodiesAnalysis('ReachingDefinitions')
        rdefs_analyzer.visit(ast)
        rdefs_analyzer.print_results()

        # Reaching Definitions analysis
        liveness_analyzer = mana.FuncBodiesAnalysis('LiveVariables')
        liveness_analyzer.visit(ast)
        liveness_analyzer.print_results()

