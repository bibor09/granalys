import ast_comments as astc
import builtins
from node import Node

builtin_types = [getattr(builtins, d) for d in dir(builtins) if isinstance(getattr(builtins, d), type)]

class NodeVisitor(astc.NodeVisitor):
    def __init__(self):
        self.edges: dict[Node] = dict()
        self.depth = -1
        self.nodeId = 0
        self.parent = Node(nodeId=self.nodeId, name="ROOT", lineno=0, depth=self.depth, id=None, value=None)
        self.bodies = dict()

    def set_node(self, ast_node):
        self.nodeId += 1
        name = ast_node.__class__.__name__
        id = None if 'id' not in ast_node._fields else ast_node.id

        # needs better solution instead of checking just for it in a list
        if name not in ["Module", "Store", "arguments", "Load", "Add", "alias", "Div", "Lt", "And"]:
            lineno = ast_node.lineno
        else:
            lineno = 0

        if 'value' in ast_node._fields and ast_node.value.__class__.__name__ not in ["Constant", "Lambda", "Call", "Name"]:
            value = ast_node.value
        else:
            value = None

        return Node(self.nodeId, name, lineno, self.depth, id, value)

    def generic_visit(self, node):
        if "body" in node._fields:
            self.depth += 1

        if self.parent not in self.edges.keys():
            self.edges[self.parent] = []

        # Keep body in count

        childNode = self.set_node(node)
        self.edges[self.parent].append(childNode)
        saved_parent = self.parent

        self.parent = childNode
        astc.NodeVisitor.generic_visit(self, node)

        if "body" in node._fields:
            self.depth -= 1
        self.parent = saved_parent


def get_ast(filename):
    visitor = NodeVisitor()

    with open(filename, "r") as f:
        source = f.read()
        tree = astc.parse(source)
        # print(astc.dump(tree, indent=2, include_attributes=True))
        visitor.visit(tree)

        # for node in visitor.edges.keys():
        #     print(node.name, node.nodeId, node.id, node.depth, node.value)
        return visitor.edges
