import networkx as nx
import zlib
from suffix_tree import Tree


'''
Comemnt line ratio
'''
def _comment_ratio(tx, verbose = False):
    result = tx.run("""
        MATCH (n:Node {name: $comment})
        WITH count(n) as comment_nr
        MATCH (nn:Node)
        RETURN comment_nr, max(nn.lineno) as lines_nr
        """, comment="Comment")
    [r] = result.data()
    summary = result.consume()
    comment_nr = r["comment_nr"]
    lines_nr = r["lines_nr"]

    if lines_nr != 0:
        ratio = comment_nr/lines_nr
        if verbose:
            print(f"Comment ratio: {comment_nr}/{lines_nr} = {ratio}\t[{summary.result_available_after} ms]")
    else:
        ratio = 0
        if verbose:
            print(f"Comment ratio: {ratio}\t[{summary.result_available_after} ms]")
    return ratio


'''
Number of variables declared in a method
'''
def _loc(tx, verbose = False):
    result = tx.run("""
        MATCH(n:Node)
        RETURN max(n.lineno) as line    
        """) 
    [r] = result.data()
    summary = result.consume()
    loc = r["line"]
    if verbose:
        print(f"LOC: {loc}\t[{summary.result_available_after} ms]")
    return loc


'''
Number of variables declared in a method
'''
def _method_var_number(tx, verbose = False):
    result = tx.run("""
        MATCH (f:Node {name:"FunctionDef"}) -[:Child*1..]->(:Node {name:"Assign"})-[:Child]->(var:Node {name:"Name"})
        WITH f, collect(distinct var.id) as vars
        RETURN f.value as function, vars 
        """)
    method_variables = result.data()
    summary = result.consume()
    
    variables = dict()
    if verbose:
        print("Number of declared variables:")
    for row in method_variables:
        function = row['function']
        vars = row['vars']

        if verbose:
            print(f'\t{function}:\t{len(vars)} {vars}')

        variables[function] = vars
    
    if verbose:
        print(f"\t[{summary.result_available_after} ms]")
    return variables


'''
Efferent coupling
'''
def _efferent_coupling(tx, verbose = False):
    # Get all classes, then look for every class calling inside of a class
    result = tx.run("""
        MATCH (c:Node {name:"ClassDef"})
        WITH collect(c.value) as classes
        UNWIND classes as called
        MATCH (cl1:Node {name:"ClassDef"})-[:Child*1..]->({name:"Call"})-[]->(cl2:Node {name:"Name", id:called})
        RETURN cl1.value as calling, collect(distinct cl2.id) as called
        """)
    r = result.data()
    summary = result.consume()

    ec = dict()
    if verbose:
        print("Efferent Coupling:")

    for row in r:
        calling = row["calling"]
        called = row["called"]
        ec[calling] = len(called)
        if verbose:
            print(f'\t{calling}:\t{ec[calling]}')
    
    if verbose:
        print(f"\t[{summary.result_available_after} ms]")
    return ec


'''
Afferent coupling
'''
def _afferent_coupling(tx, verbose = False):
    result = tx.run("""
        MATCH (c:Node {name:"ClassDef"})
        WITH collect(c.value) as classes
        UNWIND classes as called
        MATCH (cl1:Node {name:"ClassDef"})-[:Child*1..]->({name:"Call"})-[]->(cl2:Node {name:"Name", id:called})
        RETURN collect(cl1.value) as calling, cl2.id as called
        """)
    r = result.data()
    summary = result.consume()

    ac = dict()
    if verbose:
        print("Afferent Coupling:")

    for row in r:
        calling = row["calling"]
        called = row["called"]
        ac[called] = len(calling)
        if verbose:
            print(f'\t{called}:\t{ac[called]}')
    
    if verbose:
        print(f"\t[{summary.result_available_after} ms]")
    return ac


'''
Cycloamtic Complexity
'''
# calculate cyclomatic code complexity from ast, counting the predicate nodes: G(v) = d + 1
decision_nodes = ["For", "AsyncFor", "While", "If", "And", "Or", "Try", "TryStar"]

def _cyclomatic_complexity(tx, verbose = False):
    nodes = [{"name": name} for name in decision_nodes]
    result = tx.run("""
        MATCH (func:Node {name:"FunctionDef"})
        WITH collect(func.value) as functions
        UNWIND $nodes as node
        MATCH (f:Node {name:"FunctionDef"})-[:Child*1..]->(n:Node {name: node.name})
        WITH functions, count(n) as cc
        RETURN functions, cc
        """, nodes=nodes)
    r = result.data()
    summary = result.consume()

    avg_cc = 0
    compl_gt_1 = 0
    func_nr = 0
    for row in r:
        func_nr = len(row["functions"])
        cc = int(row['cc']) + 1
        avg_cc += cc
        compl_gt_1 += 1

    if func_nr != 0:
        avg_cc = (avg_cc + func_nr - compl_gt_1) / func_nr
    else:
        avg_cc = 1

    if verbose:
        print(f"Cyclomatic complexity (avg): {avg_cc}\t[{summary.result_available_after} ms]")
    return avg_cc


'''
LCOM4
'''
# LCOM4 class cohesion: lack of cohesion in methods
def count_connected_components(pot_rel_methods, all_methods):
   # Create a graph where each set(aka key) is represented by a vertex, and two vertices are connected by an edge if their corresponding sets have at least one common element.
    G = nx.Graph()
    keys = list(pot_rel_methods.keys())
    G.add_nodes_from(keys)

    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            # If they have at least one common element or the element is a class-level method
            if len(pot_rel_methods[keys[i]] & pot_rel_methods[keys[j]]) > 0 or keys[i] in all_methods:
                G.add_edge(keys[i], keys[j])
    return nx.number_connected_components(G)

# Returns a dictionary of class names with their number of empty methods
# Methods with only 'pass' or 'return' statement in them are considered empty
def _get_empty_methods(tx):
    result = tx.run("""
        MATCH (c:Node {name:"ClassDef"}) 
            -[:Child]-> (f:Node {name:"FunctionDef"})
            -[r:Child]-> (p:Node)
        WITH c.value AS class, f.value AS func, collect(p.name) AS body
        RETURN class, func, body
        """)
    r = result.data()

    nr_of_empty_methods = dict()

    for row in r:
        class_name = row["class"]
        body = row["body"]
        body.sort()
        if class_name not in nr_of_empty_methods.keys():
            nr_of_empty_methods[class_name] = 0
        if body == ["Return", "arguments"] or body == ["Pass", "arguments"]:
            nr_of_empty_methods[class_name] += 1
    return nr_of_empty_methods    

# Returns a dictionary of class names with their set of methods
def _get_all_class_methods(tx):
    result = tx.run("""
        MATCH (class:Node {name:"ClassDef"}) -[:Child]-> (func:Node {name:"FunctionDef"})
        WITH class, collect(distinct func.value) as funcs
        RETURN class.value as class, funcs
        """)
    r = result.data()

    all_class_methods = dict()
    for row in r:
        class_name = row["class"]
        funcs = row["funcs"]
        all_class_methods[class_name] = set(funcs)
    
    return all_class_methods

# Returns a dictionary of class names with their lcom4 value
def _lcom4(tx, all_class_methods, empty_class_methods, verbose = False):
    result = tx.run("""
        MATCH (class:Node {name:"ClassDef"}) -[:Child]-> 
                (func:Node {name:"FunctionDef"}) -[:Child*0..]-> 
                (attr:Node {name:"Attribute"}) -[:Child]-> (:Node {id:"self"})
        WITH class, func, collect(distinct attr.value) as attrs
        RETURN class.value as class, func.value as func, attrs
        """)
    r = result.data()

    # Place in dict methods that are referencing class variable or class method
    classes = dict()
    for row in r:
        class_name = row["class"]
        function_name = row["func"]
        attrs = row["attrs"]
        
        if class_name not in classes.keys():
            classes[class_name] = dict()

        classes[class_name][function_name] = set(attrs)

    lcom4 = dict()
    if verbose:
        print("LCOM4:")
    for class_name, functions in classes.items():
        # LCOM4 for a class = number of connected components + discrete methods - empty methods - 
        con_comp = count_connected_components(functions, all_class_methods[class_name])
        non_related = len(all_class_methods[class_name]) - len(functions)
        empty = empty_class_methods[class_name]

        lcom4[class_name] = con_comp + non_related - empty

    for cl in all_class_methods.keys():
        if cl not in lcom4.keys():
            lcom4[cl] = 0               # Meaning that the particular class's methods are not using class attributes
        if verbose:
            print(f'\t{cl}:\t{lcom4[cl]}')
   
    return lcom4


'''Depth in Inheritance Tree'''
def find_depth(relations, child, depth):
    if child not in relations.keys():
        return depth
    else:
        parent = relations[child]
        return find_depth(relations, parent, depth+1)


def _dit(tx, verbose = False):
    result = tx.run('''
        MATCH (def:Node {name:"ClassDef"})-[:Child]->(ref:Node {name:"Name"})
        RETURN def.value as def, ref.id as ref
        ''')
    r = result.data()
    summary = result.consume()
    
    relations = dict()
    for row in r:
        defs = row['def']
        refs = row['ref']
        relations[defs] = refs

    if verbose:
        print("Depth in Inheritance Tree:")

    dit = dict()
    for defs in relations.keys():
        dit[defs] = find_depth(relations, defs, 0)
        if verbose:
            print(f"\t{defs}: {dit[defs]}")

    if verbose:
        print(f"\t[{summary.result_available_after} ms]")

    return dit

