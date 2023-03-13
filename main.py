import sys
import os
from python_ast.parse_python_ast import get_ast
from database import create, get_traversal_source, close_connection, clean_graph
from src.measures import comment_ratio, cyclomatic_complexity, lcom4

def main():
    if len(sys.argv) < 2 or not os.path.isfile(sys.argv[1]):
        print(f"Correct format: {sys.argv[0]} file")
        sys.exit()

    # Parse code
    edges = get_ast(sys.argv[1])
    g = get_traversal_source()

    # Create graph from edges
    create.graph(g, edges)

    # Measures
    # comment_ratio(g)
    # cyclomatic_complexity(g)
    # lcom4(g)

    # clean_graph(g)

    close_connection()


if __name__ == "__main__":
    main()