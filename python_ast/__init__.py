import ast
import re

# Initialize list with node names that have attributes
nodes_with_attr = [ast.stmt, ast.expr, ast.excepthandler, ast.arg, ast.keyword, ast.alias]
nodes_with_attr_names = []

def get_node_name(node):
    matching = re.search(r'[A-Z][\w\d]*', node)
    if matching:
        return matching.group()

for node in nodes_with_attr:
    names = list(map(get_node_name, node.__doc__.split("\n")))
    for name in names:
        nodes_with_attr_names.append(name)

# # Manually add pattern node names USELESS in python v 3.9.x
# for pattern in ['MatchValue', 'MatchSingleton', 'MatchSequence', 'MatchMapping', 'MatchClass', 'MatchStar', 'MatchAs', 'MatchOr']:
#     nodes_with_attr_names.append(pattern)
