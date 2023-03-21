def _comment_ratio(tx):
    result = tx.run("""
        MATCH (n:Node {name: $comment})
        WITH count(n) as comment_nr
        MATCH (nn:Node)
        RETURN comment_nr, max(nn.lineno) as lines_nr
        """, comment="Comment")
    [c] = result.data()
    comment_nr = c["comment_nr"]
    lines_nr = c["lines_nr"]
    ratio = comment_nr/lines_nr
    summary = result.consume()
    print(f"Comment ratio: {comment_nr}/{lines_nr} = {ratio}\t[{summary.result_available_after} ms]")