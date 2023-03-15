from gremlin_python.process.anonymous_traversal import GraphTraversalSource
from gremlin_python.process.traversal import within
from gremlin_python.process.graph_traversal import __
from src.util import put_in_dict, count_connected_components, find_non_related_methods

# get comment and all lines of code ratio
def comment_ratio(g: GraphTraversalSource):
    # count comments
    # and all lines and return ratio
    comment_nr = g.V().has("name", "Comment").count().next()
    print("Comments:", comment_nr)

    lines_nr = g.V().values('lineno').max_().next()
    print("Lines:", lines_nr)

    print("Ratio:", comment_nr/lines_nr)


# calculate cyclomatic code complexity from ast, countning the predicate nodes: G(v) = d + 1
decision_nodes = ["For", "AsyncFor", "While", "If", "And", "Or", "Try", "TryStar"]

def cyclomatic_complexity(g: GraphTraversalSource):
    complexity = g.V().has("name", within(decision_nodes)).count().next() + 1
    print("Cyclomatic complexity:", complexity)


# LCOM4 class cohesion: lack of cohesion in methods
def lcom4(g: GraphTraversalSource):
    # For each method store used class-level variables and methods
    # If the method doesn't access any class-level variable or method, it isn't included in the dictionary
    pot_rel_methods = dict()

    # Get every method from class
    methods = g.V().has("name", "FunctionDef").toList()
    method_names = g.V().has("name", "FunctionDef").values("value").toList()

    for i in range(len(methods)):
        # Looks for every descendant of method which has "self" in name
        descendants = g.V(methods[i]).emit().repeat(__.out()).has("id","self").to_list()

        for d in descendants: 
            # Looks for every parent of those specific descendants
            parent = g.V(d).in_e().out_v().values("value").next()
            put_in_dict(method_names[i], parent, pot_rel_methods)

    # From the methods not included in the dictionary, remove the empty ones, which shouldn't count towards the final lcom4 value
    non_related_methods = find_non_related_methods(method_names, pot_rel_methods)
    empty_methods = 0
    for method in non_related_methods:
        v = g.V().has("value", method).next()
        if is_empty(v, g):
            empty_methods += 1

    print("LCOM4 =", count_connected_components(pot_rel_methods, method_names) + len(non_related_methods) - empty_methods)

def is_empty(m, g: GraphTraversalSource):
    descendants = g.V(m).emit().repeat(__.out()).values("name").to_list()
    descendants.remove("FunctionDef")
    descendants.sort()
    return descendants == ["Pass", "arguments"]