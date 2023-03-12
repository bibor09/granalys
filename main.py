import sys
import os
from python_ast.parse_python_ast import get_ast
from database import create, get_traversal_source, close_connection, clean_graph
from src.measures import comment_ratio

def main():
    if len(sys.argv) < 2 or not os.path.isfile(sys.argv[1]):
        print(f"Correct format: {sys.argv[0]} file")
        sys.exit()

    # Parse code
    edges = get_ast(sys.argv[1])
    g = get_traversal_source()

    # Create graph from edges
    create.graph(g, edges)
    comment_ratio(g)
    clean_graph(g)

    close_connection()


if __name__ == "__main__":
    main()