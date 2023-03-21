def _comment_ratio(tx):
    result = tx.run("""
        MATCH (n:Node {name: $comment})
        WITH count(n) as comment_nr
        MATCH (nn:Node)
        RETURN comment_nr, max(nn.lineno) as lines_nr
        """, comment="Comment")
    [r] = result.data()
    comment_nr = r["comment_nr"]
    lines_nr = r["lines_nr"]
    ratio = comment_nr/lines_nr
    summary = result.consume()
    print(f"Comment ratio: {comment_nr}/{lines_nr} = {ratio}\t[{summary.result_available_after} ms]")

# calculate cyclomatic code complexity from ast, countning the predicate nodes: G(v) = d + 1
decision_nodes = ["For", "AsyncFor", "While", "If", "And", "Or", "Try", "TryStar"]

def _cyclomatic_complexity(tx):
    nodes = [{"name": name} for name in decision_nodes]
    result = tx.run("""
        UNWIND $nodes as node
        MATCH (n:Node {name: node.name})
        RETURN count(n) as cc
        """, nodes=nodes)
    [r] = result.data()
    cc = r["cc"] + 1
    summary = result.consume()
    print(f"Cyclomatic complexity: {cc}\t[{summary.result_available_after} ms]")
