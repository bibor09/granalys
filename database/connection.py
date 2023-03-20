from neo4j import GraphDatabase

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "334yBQUaX2JdrCZ")

def get_driver():
    driver = GraphDatabase.driver(URI, auth=AUTH)
    driver.verify_connectivity()
    print("Connected to database.")
    return driver

def close_connection(driver):
    print("Closed connection.")
    driver.close()