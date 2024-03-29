import os
import sys
import time
import logging
import re
from neo4j import GraphDatabase, exceptions
from ast_parser import get_ast
from metrics import _comment_ratio, _cyclomatic_complexity, _lcom4, _dit, \
_get_all_class_methods, _get_empty_methods, _method_var_number, _loc, _efferent_coupling, \
_afferent_coupling

class Granalys:
    def __init__(self, uri, auth, db, verbose = False):
        self.db = db
        self.verbose = verbose

        logging.info("Connecting to Neo4j ...")
        try:
            self.driver = GraphDatabase.driver(uri, auth=auth)
            self.driver.verify_connectivity()
        except ValueError as e:
            logging.error(f"Failed to connect to Neo4j on {uri}", e)
            sys.exit()
        except exceptions.AuthError as e:
            logging.error("Failed to connect to Neo4j because of bad credentials", e)
            sys.exit()

        if self.verbose:
            logging.info("Connected")

    def get_file_ast(self, filename):
        ast = get_ast(filename)
        if ast is None:
            logging.error(f"Failed to parse ast of file {filename}.")
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
        except Exception as e:
            logging.error("Failed to create graph.", e)
            sys.exit()

    def delete_graph(self, session):
        try:
            session.execute_write(self._delete_graph, self.verbose)
        except:
            logging.error("Failed to delete.")
            sys.exit()

    def start_cmd(self):
        print("************************************\n\n\tG R A N A L Y S\n\n************************************\n")
        help = "help\t\t:Usage information\n" +\
            "f [filename]\t:Parse file\n" +\
            "exit\t\t:Exit Granalys\n"
        print(help)

        alive = True
        while alive:
            try:
                command = input(">> ")

                if command == "help":
                    print(help)

                elif re.match("^f .*\.py$", command):
                    filename = command.split(' ')[1]
                    if os.path.isfile(filename):
                        self.console(filename)
                    else:
                        logging.error(f"Invalid or non-existent file")

                elif command == "exit":
                    alive = False
                    logging.info("Exiting...") 

            except KeyboardInterrupt:
                alive = False

    def console(self, filename):
        self.get_file_ast(filename)
        print(f"Analyzing: {filename}\n")

        try:
            with self.driver.session(database=self.db) as session:
                try:
                    self.create_graph(session)
                    
                    help = "help\t\t:Usage information\n" +\
                            "print\t\t:Print ast of file\n" +\
                            "exit\t\t:Exit tool\n" +\
                            "\nMetrics:\n" +\
                            "comment\t\t:Comment line ratio of file\n" +\
                            "loc\t\t:Lines of code\n" +\
                            "vars\t\t:Number of variables declared per methods\n" +\
                            "complexity\t:Average cyclomatic complexity for methods in file\n" +\
                            "ec\t\t:Efferent coupling of classes\n" +\
                            "ac\t\t:Afferent coupling of classes\n" +\
                            "inst\t\t:Overall class instability\n" +\
                            "lcom4\t\t:Lack of Cohesion in Method measure per classes in file\n" +\
                            "dit\t\t:Depth of Inheritance Tree (in file)\n"
                    print(help)
                    alive = True

                    while alive:
                        command = input(">> ")

                        if command == "help":
                            print(help)

                        elif command == "comment":
                            try:
                                session.execute_read(_comment_ratio, self.verbose)
                            except:
                                logging.error("Failed to execute comment measure")
                                alive = False

                        elif command == "loc":
                            try:
                                session.execute_read(_loc, self.verbose)
                            except:
                                logging.error("Failed to execute loc measure")
                                alive = False

                        elif command == "vars":
                            try:
                                session.execute_read(_method_var_number, self.verbose)
                            except:
                                logging.error("Failed to execute variable number measure")
                                alive = False

                        elif command == "ec":
                            try:
                                session.execute_read(_efferent_coupling, self.verbose)
                            except:
                                logging.error("Failed to execute efferent coupling measure")
                                alive = False
                        
                        elif command == "ac":
                            try:
                                session.execute_read(_afferent_coupling, self.verbose)
                            except:
                                logging.error("Failed to execute afferent coupling measure")
                                alive = False

                        elif command == "inst":
                            try:
                                self.instability(session, self.verbose)
                            except:
                                logging.error("Failed to execute instability measure")
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
                        
                        elif command == "dit":
                            try:
                                session.execute_read(_dit, self.verbose)
                            except Exception as e:
                                logging.error("Failed to execute DIT measure",e)
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
        stats = dict()
        try:
            with self.driver.session(database=self.db) as session:
                try:
                    for f in files:
                        self.get_file_ast(f"{base}/{f}")
                        self.create_graph(session)

                        comment_rat = session.execute_read(_comment_ratio)
                        cc = session.execute_read(_cyclomatic_complexity)
                        ec = session.execute_read(_efferent_coupling)
                        ac = session.execute_read(_afferent_coupling)
                        inst = self.instability(session, self.verbose)
                        loc = session.execute_read(_loc)
                        vars = session.execute_read(_method_var_number)
                        lcom4 = self.lcom4(session, self.verbose)
                        dit = session.execute_read(_dit)

                        with open(f"{base}/{f}", "r") as file:
                            stats[f] = {"comment": "{:.2f}".format(comment_rat), 
                                        "complexity": f"{int(cc)}", 
                                        "loc": f"{int(loc)}",
                                        "ec": self.get_str_of(ec) if len(ec) > 0 else "No coupling",
                                        "ac": self.get_str_of(ac) if len(ac) > 0 else "No coupling",
                                        "inst": inst if type(inst) == str else "{:.2f}".format(inst),
                                        "vars": self.get_str_of_vars(vars),
                                        "lcom4": self.get_str_of(lcom4) if len(lcom4) > 0 else "No classes",
                                        "dit": self.get_str_of(dit) if len(dit) > 0 else "No inheritance",
                                        "content": file.read()}
                        
                        self.delete_graph(session)
                        self.close()
                except Exception as e:
                    print(e)
                    self.delete_graph(session)
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
        result = session.execute_read(_lcom4, all_class_methods, empty_class_methods, verbose)
        e = time.time()
        ms = int((e-s) * 1000)
        if verbose:
            print(f"\t[{ms} ms]")
        return result
    
    @staticmethod
    def instability(session, verbose):
        s = time.time()
        ec = session.execute_read(_efferent_coupling)
        ac = session.execute_read(_afferent_coupling)
        Ce = sum([value for value in ec.values()])
        Ca = sum([value for value in ac.values()])
        e = time.time()
        ms = int((e-s) * 1000)

        if Ce == 0 and Ca == 0:
            i = "No coupling"
        else:
            i = Ce / (Ce + Ca)

        if verbose:
            print(f"Instability: {i}\t[{ms} ms]")
        return i

    @staticmethod
    def get_str_of_vars(vars):
        str = ''
        for key, value in vars.items():
            str += f"<br><b><i> -{key}</i></b>: {len(value)}"
        return str
    
    @staticmethod
    def get_str_of(dict_str_nr):
        str = ''
        for key, value in dict_str_nr.items():
            str += f"<br><b><i> -{key}</i></b>: {value}"
        return str