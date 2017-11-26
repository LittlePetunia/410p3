from __future__ import print_function

from mutils import *
import minic_ast as mast
import copy

# Dataflow analyses on ASTs




# Function to get variable name from lvalue in Assignment
def get_lvalue_vname(lvalue):
    if isinstance(lvalue, mast.ID):
        return str(lvalue)
    elif isinstance(lvalue, mast.ArrayRef):
        return str(lvalue.name)
    else:
        print("Unexpected lvalue: %r\n" % lvalue)
        raise TypeError


class DFAnalysis(object):
    def print_results(self):
        pass


# Reaching definitions
class ReachingDefsSet(object):
    # Reaching definitions are a map from variable name to statement id
    def __init__(self, rdefs):
        if rdefs is not None:
            self.rdefs = rdefs
        else:
            self.rdefs = {}

    def update_del(self, vname, sid):
        self.rdefs[vname] = [sid]

    def update_add(self, vname, sid):
        if self.rdefs.has_key(vname):
            self.rdefs[vname].append(sid)
        else:
            self.rdefs[vname] = [sid]

    def update_addall(self, ordefs):
        for k in ordefs.rdefs.keys():
            if self.rdefs.has_key(k):
                ordefs.rdefs[k].extend(self.rdefs[k])

        self.rdefs.update(ordefs.rdefs)
        # Remove duplicates
        for k, l in self.rdefs.items():
            self.rdefs[k] = list(set(l))

    def aslist(self):
        return list(self.rdefs.items())




def update_rdefs(sid, assignment_or_decl, incoming_rdefs, nondestructive=False):
    vname = "??_update_rdefs"
    if isinstance(assignment_or_decl, mast.Assignment):
        vname = get_lvalue_vname(assignment_or_decl.lvalue)

    elif isinstance(assignment_or_decl, mast.Decl):
        vname = assignment_or_decl.name

    if nondestructive:
        incoming_rdefs.update_add(vname, sid)
    else:
        incoming_rdefs.update_del(vname, sid)

    return incoming_rdefs


# The visitor stores all statements in a map, assigning them an ID
# Additionally, it stores the loop statement ids in a list.
# For each statement, the set of reaching definitions is stored (sid -> reaching definitions)
class ReachingDefinitions(mast.NodeVisitor, DFAnalysis):
    def __init__(self):
        self.current_rdefs = ReachingDefsSet(None)
        # Map statement id to statement node
        self.stmts = {}
        # Map statement id to reaching definitions
        self.stmt_rdefs = {}
        # Statement ids that are loops
        self.loops = list()

    def __store_self_defs_(self, sid):
        self.stmt_rdefs[sid] = copy.deepcopy(self.current_rdefs)

    def show_rdefs(self, sid):
        for rd_sid in list(self.stmt_rdefs[sid].rdefs):
            self.stmts[rd_sid].show()

    # What you do when you visited a children with another visitor
    def update_from_children_visit(self, subvisit):
        # Update the statements
        self.stmts.update(subvisit.stmts)
        # Update the reaching defs at the exit of the loop
        self.current_rdefs.update_addall(subvisit.current_rdefs)
        # And finally there might have been loops in there
        # But don't keep duplicates
        self.loops = list(set(self.loops + subvisit.loops))
        self.stmt_rdefs.update(subvisit.stmt_rdefs)

    # When visiting an assignment, update the reaching definitions.
    def visit_Assignment(self, assignment):
        # Get a new statement id
        msid = assignment.nid
        # Store the sid -> statement information.
        self.stmts[msid] = assignment
        # Store the reaching definitions
        self.__store_self_defs_(msid)
        # Update the reaching definitions, store them in the map
        self.current_rdefs = update_rdefs(msid, assignment, self.current_rdefs)



    #Same when visiting a declaration
    def visit_Decl(self, decl):
        msid = decl.nid
        # Store the sid -> statement information.
        self.stmts[msid] = decl
        # Store the reaching definitions
        self.__store_self_defs_(msid)
        # Update the reaching definitions, store them in the map
        self.current_rdefs = update_rdefs(msid, decl, self.current_rdefs)



    #Visiting a conditional causes branching, and joining with non-destructive update
    def visit_If(self, ifstmt):
        ifsid = ifstmt.nid
        self.stmts[ifsid] = ifstmt
        self.__store_self_defs_(ifsid)
        #Visit the two branches, starting with the current state
        # Use deepcopy to avoid conflicts with current state
        # Do the then branch
        thenbvisitor = copy.deepcopy(self)
        thenbvisitor.visit(ifstmt.iftrue)
        # Do the else branch (if there is one)
        elsebvisitor = copy.deepcopy(self)
        if ifstmt.iffalse is not None:
            elsebvisitor.visit(ifstmt.iffalse)
        # Update the current state with the definitions by merging them
        # We're out of the branches now.
        elsebvisitor.stmts.update(thenbvisitor.stmts)
        self.stmts.update(elsebvisitor.stmts)
        # Join the two maps of reaching definitions
        elsebvisitor.current_rdefs.update_addall(thenbvisitor.current_rdefs)
        # And update the current state, we are after the branches of the if.
        self.current_rdefs = elsebvisitor.current_rdefs


    # Visiting a for loop ...
    def visit_For(self, forstmt):
        forsid = forstmt.nid
        # Don't forget to store the statement id, this is a loop
        self.loops.append(forsid)
        self.stmts[forsid] = forstmt
        # Store the current state of reaching definitions
        self.__store_self_defs_(forsid)
        # Store the special 'init' statemetn in the for declaration
        initsid = forstmt.init.nid
        self.stmts[initsid] = forstmt.init
        self.__store_self_defs_(initsid)
        self.current_rdefs = update_rdefs(initsid, forstmt.init, self.current_rdefs)
        # Store the special 'next' statement in the for declaration
        updatesid = forstmt.next.nid
        self.stmts[updatesid] = forstmt.next
        self.__store_self_defs_(updatesid)
        # Update the reaching defs state
        # the update must be nondestructive, either one or the other definition can reach the body
        self.current_rdefs = update_rdefs(updatesid, forstmt.next, self.current_rdefs, nondestructive=True)
        # Start a new recursive visit of the loop body
        bodyvisitor = copy.deepcopy(self)
        bodyvisitor.visit(forstmt.stmt)
        self.update_from_children_visit(bodyvisitor)

    def visit_While(self, whilestmt):
        wsid = whilestmt.nid
        self.loops.append(wsid)
        self.stmts[wsid] = whilestmt
        self.__store_self_defs_(wsid)
        # Start a new recursive visit of the loop body
        bodyvisitor = copy.deepcopy(self)
        bodyvisitor.visit(whilestmt.stmt)

        self.update_from_children_visit(bodyvisitor)

    def visit_DoWhile(self, dowhilestmt):
        dowsid = dowhilestmt.nid
        self.loops.append(dowsid)
        self.stmts[dowsid] = dowhilestmt
        self.__store_self_defs_(dowsid)
        # Start a new recursive visit of the loop body
        bodyvisitor = copy.deepcopy(self)
        bodyvisitor.visit(dowhilestmt.stmt)

        self.update_from_children_visit(bodyvisitor)

    def visit_Block(self, block):
        blockid = block.nid
        self.stmts[blockid] = block
        self.__store_self_defs_(blockid)
        for stmt in block.block_items:
            self.visit(stmt)

    def __str__(self):
        srepr = ""
        for sid in list(self.stmt_rdefs.keys()):
            srepr+= self.str_of_rdef(sid)

        return srepr

    def str_of_rdef(self, sid):
        rdefs = self.stmt_rdefs[sid]
        stmt = self.stmts.get(sid)
        srepr = "statement %i (%s)" % (sid, stmt)
        if stmt.coord is not None:
            srepr += " at line %i:\n" % stmt.coord.line
        else:
            srepr += ":\n"

        for (vname, sidl) in rdefs.aslist():
            srepr += "\t%s <-- {%s}\n" % (str(vname),
                                          ", ".join(list(map(str, list(map(lambda x: self.stmts[x], sidl))))))
        return srepr

    def print_results(self):
        for lsid in self.loops:
            print(self.str_of_rdef(lsid))



# Live variables analysis
class LiveVariables(mast.NodeVisitor, DFAnalysis):
    def __init__(self):
        self.stmts = {}
        self.livevars_stmts = {}
        self.current_livevars = set()
        self.loops = []

    def freeze(self, sid):
        self.livevars_stmts[sid] = copy.deepcopy(self.current_livevars)

    def show_rdefs(self, sid):
        for rd_sid in list(self.current_livevars[sid]):
            self.stmts[rd_sid].show()

    # What you do when you visited a children with another visitor
    def update_from_children_visit(self, subvisit):
        # Update the statements
        self.stmts.update(subvisit.stmts)
        # Update the reaching defs at the exit of the loop
        self.livevars_stmts.update(subvisit.livevars_stmts)
        # And finally there might have been loops in there
        # But don't keep duplicates
        self.loops = list(set(self.loops + subvisit.loops))
        self.current_livevars.union(subvisit.current_livevars)

    def visit_ID(self, id):
        self.current_livevars.add(id.name)

    # We don't want funcnames
    def visit_FuncCall(self, fcall):
        if fcall.args is not None:
            self.visit(fcall.args)

    def visit_ExprList(self, exprlist):
        for e in exprlist.exprs:
            self.visit(e)

    def getset(self):
        return copy.copy(self.current_livevars)

    # When visiting an assignment, update the reaching definitions.
    def visit_Assignment(self, assignment):
        msid = assignment.nid
        # Store the sid -> statement information.
        self.stmts[msid] = assignment
        # Store the reaching definitions
        self.freeze(msid)
        # Update the reaching definitions, store them in the map
        self.visit(assignment.rvalue)
        self.visit(assignment.lvalue)

    def visit_If(self, ifstmt):
        ifsid = ifstmt.nid
        self.stmts[ifsid] = ifstmt
        # Trick here: use a copy of self to go though one branch,
        # and self to the other, so the live variables seen in the branches
        # are correct.
        iftrue_visitor = copy.deepcopy(self)
        iftrue_visitor.visit(ifstmt.iftrue)
        if ifstmt.iffalse is not None:
            self.visit(ifstmt.iffalse)
        self.update_from_children_visit(iftrue_visitor)
        # Add the variables used in the condition
        self.visit(ifstmt.cond)
        self.freeze(ifsid)

    # Visiting a for loop ...
    def visit_For(self, forstmt):
        forsid = forstmt.nid
        self.loops.append(forsid)
        self.stmts[forsid] = forstmt
        self.visit(forstmt.stmt)
        self.visit(forstmt.next)
        self.visit(forstmt.init)
        self.freeze(forsid)

    def visit_While(self, whilestmt):
        wsid = whilestmt.nid
        self.loops.append(wsid)
        self.stmts[wsid] = whilestmt
        self.visit(whilestmt.stmt)
        self.visit(whilestmt.cond)
        self.freeze(wsid)

    def visit_DoWhile(self, dowhilestmt):
        dowsid = dowhilestmt.nid
        self.loops.append(dowsid)
        self.stmts[dowsid] = dowhilestmt
        self.visit(dowhilestmt.stmt)
        self.visit(dowhilestmt.cond)
        self.freeze(dowsid)


    def visit_Block(self, block):
        blockid = block.nid
        self.stmts[blockid] = block
        for stmt in reversed(block.block_items):
            self.visit(stmt)
        self.freeze(blockid)

    def __str__(self):
        srepr = ""
        for sid in list(self.livevars_stmts.keys()):
            srepr += self.str_of_rdef(sid)

        return srepr

    def str_of_rdef(self, sid):
        lives = self.livevars_stmts[sid]
        stmt = self.stmts.get(sid)
        srepr = "statement %i (%s)" % (sid, stmt)
        if stmt.coord is not None:
            srepr += " at line %i:\n" % stmt.coord.line
        else:
            srepr += ":\n"
        srepr += "%s\n" % lives

        return srepr

    def print_results(self):
        for lsid in self.loops:
            print(self.str_of_rdef(lsid))


# Store all function bodies
class FuncBodiesAnalysis(mast.NodeVisitor):
    # Instantiate with name of an analysis that must be a superclass of DFAnalysis
    def __init__(self, analysis):
        self.analysis = analysis
        self.function_bodies = {}
        self.function_analysis_results = {}

    def visit_FuncDef(self, funcdef):
        self.function_bodies[str(funcdef.decl.name)] = funcdef.body
        # Get the class with the name stored in self.analysis.
        # It should be a class in the current module.
        analysis_class = globals().get(self.analysis)
        # Create an instance of the class
        analysis_instance = analysis_class()
        analysis_instance.visit(funcdef.body)
        self.function_analysis_results[str(funcdef.decl.name)] = analysis_instance

    def print_results(self):
        print("Results for analysis %s:\n" % self.analysis)
        for fname, fres in list(self.function_analysis_results.items()):
            print('----------In function %s ----------\n' % fname)
            fres.print_results()

    def __str__(self):
        resstr = "Results for analysis %s:\n" % self.analysis
        for fname, fres in list(self.function_analysis_results.items()):
            resstr += '----------In function %s ----------\n' % fname
            resstr += "%s: %s\n" % (fname, fres)
        return resstr

    def __repr__(self):
        srepr = "Results for analysis %s\n" % self.analysis
        for fname, fres in list(self.function_analysis_results.items()):
            srepr += "%s: %r\n" % (fname, fres)
        return srepr

