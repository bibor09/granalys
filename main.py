import sys
import os
from python_ast.parse_python_ast import get_ast
from database.connection import get_driver, close_connection
from database.data_acces import clean
from src.measures import comment_ratio, cyclomatic_complexity, lcom4
import time

def create(edges, session):
    start = time.time()
    names = [{"name":node.name, "value":node.value, "lineno":node.lineno, "nodeId":node.nodeId} for node in edges.keys()]
    session.run("""
            WITH $names AS batch
            UNWIND batch AS node
            CREATE (n:Node)
            SET n = {name:node.name, value:node.value, lineno:node.lineno, nodeId:node.nodeId}
            """, names=names)
    end = time.time()
    print(f"Added nodes: {end-start} s.")

def add_edges(edges, session):
    start = time.time()
    for key in edges.keys():
        children = [{"id":node.nodeId} for node in edges[key]]
        session.run("""
                WITH $children AS batch
                UNWIND batch AS child
                MATCH (p {nodeId: $parentId})
                MATCH (c {nodeId: child.id})
                CREATE (p)-[r:Child]->(c)
                """, children=children, parentId=key.nodeId)
    end = time.time()
    print(f"Added edges: {end-start} s.")

def delete(session):
    summary = session.execute_write(clean)
    print(f"Query done in {summary.result_available_after} ms: {summary.counters}")

def main():
    s = time.time()
    if len(sys.argv) < 2 or not os.path.isfile(sys.argv[1]):
        print(f"Correct format: {sys.argv[0]} file")
        sys.exit()

    # Parse code
    edges = get_ast(sys.argv[1])
    
    print(f"Parsed code.")
    
    # Connect to db
    print("Connecting...")
    driver = get_driver()
    with driver.session(database="neo4j") as session:
        # CREATE DB
        create(edges, session)
        add_edges(edges, session)
        # CLEAN DB
        delete(session)
    close_connection(driver)

    e = time.time()
    print(f"Total elapsed time: {e-s} s")

if __name__ == "__main__":
    main()