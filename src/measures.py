from gremlin_python.process.anonymous_traversal import GraphTraversalSource
from gremlin_python.process.traversal import within
from gremlin_python.process.graph_traversal import __

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
    # methods = g.V().has("name", "FunctionDef").values("value").toList()
    methods = g.V().has("name", "FunctionDef").toList()
    # descendants = g.V(methods[0]).emit().repeat(__.out_e().in_v().has("id", "self")).values("name").toList()
    descendants = g.V(methods[0]).repeat(__.out()).has("id", "self").toList()
    print(methods)
    print(descendants)

    # print(classes)