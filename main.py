import sys
import os
from neo4j import GraphDatabase
from python_ast.parse_python_ast import get_ast
from src.measure import _comment_ratio, _cyclomatic_complexity

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

    def create_graph(self, session, nodes, edges):
        session.execute_write(self._create_graph, nodes, edges)

    def delete_graph(self, session):
        session.execute_write(self._delete_graph)

    def loop(self, nodes, edges):
        with self.driver.session(database="neo4j") as session:
            self.create_graph(session, nodes, edges)
            alive = True

            while alive:
                command = input(">> ")
                if command == "comment":
                    try:
                        session.execute_read(_comment_ratio)
                    except Exception as e:
                        print("Error:",e)
                        alive = False
                if command == "complexity":
                    try:
                        session.execute_read(_cyclomatic_complexity)
                    except Exception as e:
                        print("Error:",e)
                        alive = False
                elif command == "exit":
                    alive = False
                    print("Exiting...") 

            self.delete_graph(session)

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
        print(f"Added nodes\t[{summary.result_available_after} ms -- {summary.counters}]")

        # Add edges
        result = tx.run("""
            UNWIND $batch AS edge
            MATCH
                (p:Node {nodeId: edge.from}),
                (c:Node {nodeId: edge.to})
            CREATE (p)-[r:Child]->(c)
            """, batch=edges)
        summary = result.consume()
        print(f"Added edges\t[{summary.result_available_after} ms -- {summary.counters}]")

    @staticmethod
    def _delete_graph(tx):
        # Delete
        result = tx.run("""
            MATCH (n)
            DETACH DELETE n
            """)
        summary = result.consume()
        print(f"Delete graph\t[{summary.result_available_after} ms -- {summary.counters}]")


if __name__ == "__main__":
    if len(sys.argv) < 2 or not os.path.isfile(sys.argv[1]):
        print(f"Correct format: {sys.argv[0]} file")
        sys.exit()

    nodes, edges = get_ast(sys.argv[1])
    print(f"Parsed code.")

    instance = Granalys(URI, AUTH)
    instance.loop(nodes, edges)
    instance.close()