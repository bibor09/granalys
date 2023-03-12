from queue import Queue
import parse_python_ast
from node import Node
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.anonymous_traversal import traversal

from measures import comment_ratio

# Adds a node as a vertex to the graph
def add_node_as_vertex(node: Node, g):
    return g.add_v()\
    .property("name", node.name)\
    .property("nodeId", node.nodeId)\
    .property("lineno", node.lineno)\
    .property("depth", node.depth)\
    .property("id", node.id)\
    .property("value", node.value)\
    .next()

# Create graph from nodes
def create_graph(g, edges: dict[Node, list[Node]]):
    nodes: Queue[Node] = Queue()
    visited: list[Node] = []

    # create Root node and add to queue
    root = Node(nodeId=0, name="ROOT", lineno=0, depth=-1, id=None, value=None)
    nodes.put(root)
    visited.append(root)

    # add root vertex to graph
    add_node_as_vertex(root, g)

    # Get nodes from queue
    while not nodes.empty():
        node:Node = nodes.get()
        parentVertex = g.V().has("nodeId", node.nodeId).next()

        if node in edges.keys():
            for child in edges[node]:
                if child not in visited:
                    nodes.put(child)
                    visited.append(child)
                    print(child.nodeId, child.name, child.value)
                    childVertex = add_node_as_vertex(child, g)
                    g.addE('child').from_(parentVertex).to(childVertex).iterate()
    
    g.io("D:\Egyetem\Licensz\granalys\data\graph.xml").write().iterate()
    return g

# Remove vertices
def clean_graph(g):
    g.V().drop().iterate()


def main():
    # Parse code
    edges = parse_python_ast.get_ast("D:\Egyetem\Licensz\granalys\data\example.py")

    # Connect to server
    gremlin_url = "ws://localhost:8182/gremlin"
    connection = DriverRemoteConnection(gremlin_url, "g")
    g = traversal().withRemote(connection)

    # Create graph from edges
    create_graph(g, edges)
    comment_ratio(g)
    clean_graph(g)

    connection.close()


if __name__ == "__main__":
    main()