from neo4j import GraphDatabase

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "334yBQUaX2JdrCZ")

def create_person(tx, name):  
    result = tx.run(
        "MERGE (:Person {name: $name})",  
        name=name  
    )
    summary = result.consume()
    return summary

driver = GraphDatabase.driver(URI, auth=AUTH)
driver.verify_connectivity()

with driver.session(database="neo4j") as session:
    summary = session.execute_write(create_person, name="Alice")  

    print("Created {nodes_created} nodes in {time} ms.".format(
        nodes_created=summary.counters.nodes_created,
        time=summary.result_available_after
    ))

driver.close()