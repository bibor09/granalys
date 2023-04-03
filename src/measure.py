import networkx as nx

def _comment_ratio(tx):
    result = tx.run("""
        MATCH (n:Node {name: $comment})
        WITH count(n) as comment_nr
        MATCH (nn:Node)
        RETURN comment_nr, max(nn.lineno) as lines_nr
        """, comment="Comment")
    [r] = result.data()
    comment_nr = r["comment_nr"]
    lines_nr = r["lines_nr"]
    ratio = comment_nr/lines_nr
    summary = result.consume()
    print(f"Comment ratio: {comment_nr}/{lines_nr} = {ratio}\t[{summary.result_available_after} ms]")

# calculate cyclomatic code complexity from ast, counting the predicate nodes: G(v) = d + 1
decision_nodes = ["For", "AsyncFor", "While", "If", "And", "Or", "Try", "TryStar"]

def _cyclomatic_complexity(tx):
    nodes = [{"name": name} for name in decision_nodes]
    result = tx.run("""
        UNWIND $nodes as node
        MATCH (n:Node {name: node.name})
        RETURN count(n) as cc
        """, nodes=nodes)
    [r] = result.data()
    cc = r["cc"] + 1
    summary = result.consume()
    print(f"Cyclomatic complexity: {cc}\t[{summary.result_available_after} ms]")



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

    # for comp in nx.connected_components(G):
    #     print("CONNECTED COMP", comp)
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

def _lcom4(tx, all_class_methods, empty_class_methods):
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

    print("LCOM4:")
    for clss in classes.items():
        name = clss[0]
        functions = clss[1]
        con_comp = count_connected_components(functions, all_class_methods[name])
        non_rel = len(all_class_methods[name]) - len(functions)
        empty = empty_class_methods[name]
        print(f'\t{clss[0]}: {con_comp + non_rel - empty}')
        
    # print(classes)
    # print(r)
    # print(f'{r["class.value"]} -> {r["func.value"]} -> {r["attr.value"]}')
    
   
# Code duplication

def _duplicates(tx):
    clones = []
    # for each subtree, if mass then hash i to bucket
    # for each subtree i and j in the same bucket
    pass

# Coverage



