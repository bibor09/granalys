from gremlin_python.process.anonymous_traversal import GraphTraversalSource
from gremlin_python.process.traversal import within
from gremlin_python.process.graph_traversal import __
from src.util import put_in_dict, find_clusters, find

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


# LCOM4 class cohesion
def lcom4(g: GraphTraversalSource):
    # Count connected components in class
    class_level = dict()

    methods = g.V().has("name", "FunctionDef").toList()
    method_names = g.V().has("name", "FunctionDef").values("value").toList()
    for i in range(len(methods)):
        # Looks for every descendant of method which has "self" in name
        descendants = g.V(methods[i]).emit().repeat(__.out()).has("id","self").to_list()

        for d in descendants: 
            # Looks for every parent of those specific descendants
            parent = g.V(d).in_e().out_v().values("value").next()
            put_in_dict(method_names[i], parent, class_level)

    print(class_level)
    find_clusters(class_level, method_names)
    find(set(method_names), class_level)

def is_empty(m, g: GraphTraversalSource):
    descendants = g.V(m).emit().repeat(__.out()).values("name").to_list()
    # print(descendants)
    return descendants.sort() == ["Pass", "arguments"].sort()