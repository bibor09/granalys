from database import get_traversal_source, close_connection, clean_graph

g = get_traversal_source()

clean_graph(g)

close_connection()