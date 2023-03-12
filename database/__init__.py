from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.anonymous_traversal import GraphTraversalSource
from gremlin_python.process.anonymous_traversal import traversal

gremlin_url = "ws://localhost:8182/gremlin"
connection = DriverRemoteConnection(url=gremlin_url, traversal_source="g")

def get_traversal_source():
    return traversal().withRemote(connection)

def clean_graph(g: GraphTraversalSource):
    g.V().drop().iterate()

def close_connection():
    connection.close()