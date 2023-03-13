from database import get_traversal_source, close_connection
from src.measures import comment_ratio, cyclomatic_complexity, lcom4

g = get_traversal_source()

# comment_ratio(g)
# cyclomatic_complexity(g)
lcom4(g)

close_connection()