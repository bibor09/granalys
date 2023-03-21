import sys
import os
from neo4j import GraphDatabase
from python_ast.parse_python_ast import get_ast

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "334yBQUaX2JdrCZ")

class Granalys:
    def __init__(self, uri, auth):
        print("Connecting to database...")
        self.driver = GraphDatabase.driver(uri, auth=auth)
        self.driver.verify_connectivity()
        print("Connected")

    def close(self):
        self.driver.close()
        print("Closed connection")

    def create_graph(self, nodes, edges):
        with self.driver.session(database="neo4j") as session:
            session.execute_write(self._create_graph, nodes, edges)

    def delete_graph(self):
        with self.driver.session(database="neo4j") as session:
            session.execute_write(self._delete_graph)

    def loop(self, nodes, edges):
        self.create_graph(nodes, edges)
        alive = True

        while alive:
            command = input("Enter command: ")
            if command == "comment":
                # comment measure
                print("Not yet")
            elif command == "exit":
                alive = False
                print("Exiting...") 

        self.delete_graph()

    @staticmethod
    def _create_graph(tx,  nodes, edges):
        # Add nodes
        names = [{"name":node.name, "value":node.value, "lineno":node.lineno, "nodeId":node.nodeId} for node in nodes]
        result = tx.run("""
                WITH $names AS batch
                UNWIND batch AS node
                CREATE (n:Node)
                SET n = {name:node.name, value:node.value, lineno:node.lineno, nodeId:node.nodeId}
                """, names=names)
        summary = result.consume()
        print(f"Added nodes in {summary.result_available_after} ms: {summary.counters}")

        # Add edges
        result = tx.run("""
            UNWIND $batch AS edge
            MATCH
                (p:Node {nodeId: edge.from}),
                (c:Node {nodeId: edge.to})
            CREATE (p)-[r:Child]->(c)
            """, batch=edges)
        summary = result.consume()
        print(f"Added edges in {summary.result_available_after} ms: {summary.counters}")

    @staticmethod
    def _delete_graph(tx):
        # Delete
        result = tx.run("""
            MATCH (n)
            DETACH DELETE n
            """)
        summary = result.consume()
        print(f"Query done in {summary.result_available_after} ms: {summary.counters}")


if __name__ == "__main__":
    if len(sys.argv) < 2 or not os.path.isfile(sys.argv[1]):
        print(f"Correct format: {sys.argv[0]} file")
        sys.exit()

    nodes, edges = get_ast(sys.argv[1])
    print(f"Parsed code.")

    instance = Granalys(URI, AUTH)
    instance.loop(nodes, edges)
    instance.close()