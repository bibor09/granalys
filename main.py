import sys
import os
from python_ast.parse_python_ast import get_ast
from database.connection import get_driver, close_connection
from src.measures import comment_ratio, cyclomatic_complexity, lcom4
import time

# ---------------------------- Multiple Queries - One transaction ----------------------- 
def create_graph(tx, nodes, edges):
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

    # Delete
    result = tx.run("""
        MATCH (n)
        DETACH DELETE n
        """)
    summary = result.consume()
    print(f"Query done in {summary.result_available_after} ms: {summary.counters}")

def main():
    s = time.time()
    if len(sys.argv) < 2 or not os.path.isfile(sys.argv[1]):
        print(f"Correct format: {sys.argv[0]} file")
        sys.exit()

    # Parse code
    nodes, edges = get_ast(sys.argv[1])
    print(f"Parsed code.")
    
    # Connect to db
    print("Connecting...")
    driver = get_driver()
    with driver.session(database="neo4j") as session:
        result = session.execute_write(create_graph, nodes, edges)
    close_connection(driver)

    e = time.time()
    print(f"Total elapsed time: {e-s} s")

if __name__ == "__main__":
    main()