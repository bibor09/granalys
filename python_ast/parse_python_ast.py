import ast_comments as astc
import builtins
from src.node import Node
from python_ast import nodes_with_attr_names
import re

builtin_types = [getattr(builtins, d) for d in dir(builtins) if isinstance(getattr(builtins, d), type)]

def has_attributes(name):
    return name in nodes_with_attr_names

def is_primitive(name):
    return re.match(r'^[a-z]+$', name)

class NodeVisitor(astc.NodeVisitor):
    def __init__(self):
        self.nodes: list[Node] = []
        self.edges = []
        self.depth = -1
        self.nodeId = 0
        self.parent = Node(nodeId=self.nodeId, name="ROOT", lineno=0, depth=self.depth, id=None, value=None)
        self.bodies = dict()

    def set_node(self, ast_node):
        self.nodeId += 1
        name = ast_node.__class__.__name__
        id = None if 'id' not in ast_node._fields else ast_node.id
        # print(name, ast_node._fields)

        if id and 'attr' in ast_node._fields:
            print("benne", ast_node.attr)
            id += f".{ast_node.attr}"

        if has_attributes(name):
            lineno = ast_node.lineno
        else:
            lineno = 0

        if name == "Attribute":
            value = ast_node.attr
        elif 'value' in ast_node._fields and is_primitive(ast_node.value.__class__.__name__) :
            value = ast_node.value
        elif 'name' in ast_node._fields:
            value = ast_node.name
        else:
            value = None

        return Node(self.nodeId, name, lineno, self.depth, id, value)

    def generic_visit(self, node):
        if "body" in node._fields:
            self.depth += 1

        if self.parent not in self.nodes:
            self.nodes.append(self.parent)

        # Keep body in count

        childNode = self.set_node(node)
        self.nodes.append(childNode)
        self.edges.append({"from":self.parent.nodeId, "to":childNode.nodeId})
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
        ast_str = astc.dump(tree, indent=2)
        visitor.visit(tree)

        # for node in visitor.edges.keys():
        #     print(node.name, node.nodeId, node.id, node.depth, node.value)
        return visitor.nodes, visitor.edges, ast_str
