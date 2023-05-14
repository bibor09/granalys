import sys
import time
import logging
from neo4j import GraphDatabase, exceptions
from ast_parser import get_ast
from measure import _comment_ratio, _cyclomatic_complexity, _lcom4, _duplicates, _get_all_class_methods, _get_empty_methods

class Granalys:
    def __init__(self, uri, auth, db, verbose = False):
        self.db = db
        self.verbose = verbose

        logging.info("Connecting to Neo4j ...")
        try:
            self.driver = GraphDatabase.driver(uri, auth=auth)
            self.driver.verify_connectivity()
        except ValueError:
            logging.error(f"Failed to connect to Neo4j on {uri}")
            sys.exit()
        except exceptions.AuthError:
            logging.error("Failed to connect to Neo4j because of bad credentials")
            sys.exit()

        if self.verbose:
            logging.info("Connected")

    def get_file_ast(self, filename):
        ast = get_ast(filename)
        if ast is None:
            logging.error("Failed to parse ast of file.")
            sys.exit()
        self.nodes, self.edges, self.ast_str = ast

    def close(self):
        try:
            self.driver.close()
        except:
            logging.error("Failed to close connection.")
            sys.exit()
        if self.verbose:
            logging.info("Closed connection")

    def create_graph(self, session):
        try:
            session.execute_write(self._create_graph, self.nodes, self.edges, self.verbose)
        except:
            logging.error("Failed to create graph.")
            sys.exit()

    def delete_graph(self, session):
        try:
            session.execute_write(self._delete_graph, self.verbose)
        except:
            logging.error("Failed to delete.")
            sys.exit()

    def start_cmd(self, filename):
        self.get_file_ast(filename)

        try:
            with self.driver.session(database=self.db) as session:
                try:
                    self.create_graph(session)
                    print("************************************\n\n\tG R A N A L Y S\n\n************************************")
                    help = "help\t\t:Usage information\n" +\
                            "print\t\t:Print ast of file\n" +\
                            "exit\t\t:Exit tool\n" +\
                            "\nMetrics:\n" +\
                            "comment\t\t:Comment line ratio of file\n" +\
                            "complexity\t:Cyclomatic complexity of file\n" +\
                            "lcom4\t\t:Lack of Cohesion in Method measure per classes in file\n" +\
                            "duplicates\t:Duplicates in file\n" 
                    print(help)
                    alive = True

                    while alive:
                        command = input(">> ")
                        if command == "help":
                            
                            logging.info(help)

                        if command == "comment":
                            try:
                                session.execute_read(_comment_ratio, self.verbose)
                            except:
                                logging.error("Failed to execute comment measure")
                                alive = False
                                
                        elif command == "complexity":
                            try:
                                session.execute_read(_cyclomatic_complexity, self.verbose)
                            except:
                                logging.error("Failed to execute complexity measure")
                                alive = False

                        elif command == "lcom4":
                            try:
                                self.lcom4(session, self.verbose)
                            except:
                                logging.error("Failed to execute lcom4 measure")
                                alive = False

                        elif command == "duplicates":
                            try:
                                session.execute_read(_duplicates, self.verbose)
                            except:
                                logging.error("Failed to execute duplicate measure")
                                alive = False

                        elif command == "print":
                            print(self.ast_str) 

                        elif command == "exit":
                            alive = False
                            logging.info("Exiting...") 

                    self.delete_graph(session)
                except KeyboardInterrupt:
                    self.delete_graph(session)
        except exceptions.ClientError as e:
            logging.error(e.message)
            sys.exit()

    def analyze_files(self, base, files):
        # dict: {filename: dict(stats)}
        stats = dict()
        try:
            with self.driver.session(database=self.db) as session:
                try:
                    for f in files:
                        self.get_file_ast(f"{base}/{f}")
                        self.create_graph(session)

                        comment_rat = session.execute_read(_comment_ratio)
                        cc = session.execute_read(_cyclomatic_complexity)

                        with open(f"{base}/{f}", "r") as file:
                            stats[f] = {"comment":comment_rat, "complexity": cc, "content": file.read()}
                        
                        self.delete_graph(session)
                        self.close()
                except:
                    return None
        except:
            return None
        return stats

    @staticmethod
    def _create_graph(tx,  nodes, edges, verbose):
        # Add nodes
        names = [{"name":node.name, "value":node.value, "lineno":node.lineno, "id":node.id, "nodeId":node.nodeId} for node in nodes]
        result = tx.run("""
                WITH $names AS batch
                UNWIND batch AS node
                CREATE (n:Node)
                SET n = {name:node.name, value:node.value, lineno:node.lineno, id:node.id, nodeId:node.nodeId}
                """, names=names)
        summary = result.consume()
        if verbose:
            logging.info(f"Added nodes\t[{summary.result_available_after} ms]")

        # Add edges
        result = tx.run("""
            UNWIND $batch AS edge
            MATCH
                (p:Node {nodeId: edge.from}),
                (c:Node {nodeId: edge.to})
            CREATE (p)-[r:Child]->(c)
            """, batch=edges)
        summary = result.consume()
        if verbose:
            logging.info(f"Added edges\t[{summary.result_available_after} ms]")

    @staticmethod
    def _delete_graph(tx, verbose):
        # Delete
        result = tx.run("""
            MATCH (n)
            DETACH DELETE n
            """)
        summary = result.consume()
        if verbose:
            logging.info(f"Delete graph\t[{summary.result_available_after} ms]")

    @staticmethod
    def lcom4(session, verbose):
        s = time.time()
        all_class_methods = session.execute_read(_get_all_class_methods)
        empty_class_methods = session.execute_read(_get_empty_methods)
        session.execute_read(_lcom4, all_class_methods, empty_class_methods, verbose = False)
        e = time.time()
        ms = int((e-s) * 1000)
        if verbose:
            logging.info(f"\t[{ms} ms]")