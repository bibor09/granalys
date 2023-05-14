import networkx as nx
import zlib

def _comment_ratio(tx, verbose = False):
    result = tx.run("""
        MATCH (n:Node {name: $comment})
        WITH count(n) as comment_nr
        MATCH (nn:Node)
        RETURN comment_nr, max(nn.lineno) as lines_nr
        """, comment="Comment")
    [r] = result.data()
    comment_nr = r["comment_nr"]
    lines_nr = r["lines_nr"]
    if lines_nr != 0:
        ratio = comment_nr/lines_nr
    else:
        ratio = "empty file"
    summary = result.consume()

    if verbose:
        print(f"Comment ratio: {comment_nr}/{lines_nr} = {ratio}\t[{summary.result_available_after} ms]")
    
    return ratio
    

# calculate cyclomatic code complexity from ast, counting the predicate nodes: G(v) = d + 1
decision_nodes = ["For", "AsyncFor", "While", "If", "And", "Or", "Try", "TryStar"]

def _cyclomatic_complexity(tx, verbose = False):
    nodes = [{"name": name} for name in decision_nodes]
    result = tx.run("""
        UNWIND $nodes as node
        MATCH (n:Node {name: node.name})
        RETURN count(n) as cc
        """, nodes=nodes)
    [r] = result.data()
    cc = r["cc"] + 1
    summary = result.consume()

    if verbose:
        print(f"Cyclomatic complexity: {cc}\t[{summary.result_available_after} ms]")
    return cc


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

def _get_empty_methods(tx):
    result = tx.run("""
        MATCH (c:Node {name:"ClassDef"}) 
            -[:Child]-> (f:Node {name:"FunctionDef"})
            -[r:Child]->(p:Node)
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

def _get_all_class_methods(tx):
    result = tx.run("""
        MATCH (class:Node {name:"ClassDef"}) -[:Child]-> (func:Node {name:"FunctionDef"})
        RETURN class.value, func.value 
        """)
    r = result.data()

    all_class_methods = dict()
    for row in r:
        class_name = row["class.value"]
        function_name = row["func.value"]
        if class_name not in all_class_methods.keys():
            all_class_methods[class_name] = set()
        all_class_methods[class_name].add(function_name)
    
    return all_class_methods

def _lcom4(tx, all_class_methods, empty_class_methods, verbose = False):
    result = tx.run("""
        MATCH (class:Node {name:"ClassDef"}) -[:Child]-> 
            (func:Node {name:"FunctionDef"}) -[:Child*0..]-> 
            (attr:Node {name:"Attribute"}) -[:Child]-> 
            (:Node {id:"self"})
        RETURN class.value, func.value, attr.value 
        """)
    r = result.data()

    # Place in dict methods that are referencing class variable or class method
    classes = dict()
    for row in r:
        class_name = row["class.value"]
        function_name = row["func.value"]
        attr_name = row["attr.value"]
        
        if class_name not in classes.keys():
            classes[class_name] = dict()

        if function_name not in classes[class_name].keys():
            classes[class_name][function_name] = set()
        
        classes[class_name][function_name].add(attr_name)

    if verbose:
        print("LCOM4:")
    for clss in classes.items():
        name = clss[0]
        functions = clss[1]
        con_comp = count_connected_components(functions, all_class_methods[name])
        non_rel = len(all_class_methods[name]) - len(functions)
        empty = empty_class_methods[name]

        if verbose:
            print(f'\t{clss[0]}: {con_comp + non_rel - empty}')
        
    # print(classes)
    # print(r)
    # print(f'{r["class.value"]} -> {r["func.value"]} -> {r["attr.value"]}')
    
   

# Code duplication
def path_union(path1, path2):
    path1_nodeIds = set([n["nodeId"] for n in path1])
    path2_nodeIds = set([n["nodeId"] for n in path2])
    path1_nodeIds.union(path2_nodeIds)

    path_union = []
    for n in path1:
        if n["nodeId"] in path1_nodeIds:
            path_union.append(n)
    for n in path2:
        if n["nodeId"] in path2_nodeIds:
            if n not in path_union:
                path_union.append(n)

    return path_union

def concat_node_attributes(node):
    str = node["name"]
    if "value" in node.keys():
        str += node["value"]
    if "id" in node.keys():
        str += node["id"]
    return str

def hash_subtree(subtree):
    str = ''
    for n in subtree:
        str += concat_node_attributes(n)
    return zlib.crc32(bytearray(str, 'utf-8'))

def _duplicates(tx, verbose = False):
    # 1 to not consider leaves
    result = tx.run("""
        MATCH path=(a:Node)-[r:Child*1..]->(b:Node)
        WHERE not (b:Node)-[]->()
        RETURN a, nodes(path) AS path
        """)
    r = result.data()

    subtrees = dict()
    # merge paths to get subtrees
    for row in r:
        a = row["a"]
        id = a["nodeId"]
        path = row["path"]
        
        if id not in subtrees.keys():
            subtrees[id] = set()

        subtrees[id] = path_union(subtrees[id], path)

    # after subtrees are done
    clones = dict()
    for i in subtrees.values():
        if len(i) >= 1:
            hash = hash_subtree(i)
        if hash not in clones.keys():
            clones[hash] = []
        clones[hash].append(i)

    if verbose:
        print("Duplicates:")
    for trees in clones.values():
        if len(trees) > 1:
            lines = ''
            for t in range(len(trees)):
                lines += str(trees[t][0]["lineno"]) + " "
            if verbose:
                print(f"\tOn lines: {lines}")
# Coverage



