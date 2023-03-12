from gremlin_python.process.anonymous_traversal import GraphTraversalSource
from gremlin_python.process.traversal import within

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

# another measure