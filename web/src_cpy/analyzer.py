import sys
import os
import time
from neo4j import GraphDatabase
from .ast_parser import get_ast
from .measure import _comment_ratio, _cyclomatic_complexity, _lcom4, _duplicates, _get_all_class_methods, _get_empty_methods

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

            self.delete_graph(session)

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

    @staticmethod
    def lcom4(session):
        s = time.time()
        all_class_methods = session.execute_read(_get_all_class_methods)
        empty_class_methods = session.execute_read(_get_empty_methods)
        session.execute_read(_lcom4, all_class_methods, empty_class_methods)
        e = time.time()
        ms = int((e-s) * 1000)
        print(f"\t[{ms} ms]")

    def analyze_files(self, base, files):
        # dict: filename: dict(stats)
        stats = dict()

        with self.driver.session(database="neo4j") as session:
            # TODO error handling
            for f in files:
                nodes, edges, ast_str = get_ast(f"{base}/{f}")
                self.create_graph(session, nodes, edges)

                comment_rat = session.execute_read(_comment_ratio)
                cc = session.execute_read(_cyclomatic_complexity)
                print("Got stats.")

                stats[f] = {"comment":comment_rat, "complexity": cc}
                
                self.delete_graph(session)
                print(f"File '{f}' done.")

        return stats

def analyze_files(base, files):
    instance = Granalys(URI, AUTH)
    print("Analyzing files:", files)
    stats = instance.analyze_files(base, files)
    instance.close()
    return stats