import time
from neo4j import GraphDatabase
from .ast_parser import get_ast
from .measure import _comment_ratio, _cyclomatic_complexity, _lcom4, _duplicates, _get_all_class_methods, _get_empty_methods

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "334yBQUaX2JdrCZ")

class Granalys:
    def __init__(self, uri, auth):
        self.driver = GraphDatabase.driver(uri, auth=auth)
        self.driver.verify_connectivity()

    def close(self):
        self.driver.close()

    def create_graph(self, session, nodes, edges):
        session.execute_write(self._create_graph, nodes, edges)

    def delete_graph(self, session):
        session.execute_write(self._delete_graph)

    @staticmethod
    def _create_graph(tx,  nodes, edges):
        # Add nodes
        names = [{"name":node.name, "value":node.value, "lineno":node.lineno, "id":node.id, "nodeId":node.nodeId} for node in nodes]
        result = tx.run("""
                WITH $names AS batch
                UNWIND batch AS node
                CREATE (n:Node)
                SET n = {name:node.name, value:node.value, lineno:node.lineno, id:node.id, nodeId:node.nodeId}
                """, names=names)
        summary = result.consume()

        # Add edges
        result = tx.run("""
            UNWIND $batch AS edge
            MATCH
                (p:Node {nodeId: edge.from}),
                (c:Node {nodeId: edge.to})
            CREATE (p)-[r:Child]->(c)
            """, batch=edges)
        summary = result.consume()

    @staticmethod
    def _delete_graph(tx):
        result = tx.run("""
            MATCH (n)
            DETACH DELETE n
            """)
        summary = result.consume()

    @staticmethod
    def lcom4(session):
        s = time.time()
        all_class_methods = session.execute_read(_get_all_class_methods)
        empty_class_methods = session.execute_read(_get_empty_methods)
        session.execute_read(_lcom4, all_class_methods, empty_class_methods)
        e = time.time()
        ms = int((e-s) * 1000)

    def analyze_files(self, base, files):
        # dict: {filename: dict(stats)}
        stats = dict()

        try:
            with self.driver.session(database="neo4j") as session:
                # TODO error handling
                for f in files:
                    nodes, edges, ast_str = get_ast(f"{base}/{f}")
                    self.create_graph(session, nodes, edges)

                    comment_rat = session.execute_read(_comment_ratio)
                    cc = session.execute_read(_cyclomatic_complexity)

                    with open(f"{base}/{f}", "r") as file:
                        stats[f] = {"comment":comment_rat, "complexity": cc, "content": file.read()}
                    
                    self.delete_graph(session)
                    print(f"File '{f}' done.")
        except:
            return None

        return stats

def analyze_files(base, files):
    instance = Granalys(URI, AUTH)
    print("Analyzing files:", files)
    stats = instance.analyze_files(base, files)
    instance.close()
    return stats