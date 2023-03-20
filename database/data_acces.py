
def clean(tx):
    result = tx.run("""
        MATCH (n)
        DETACH DELETE n
        """)
    summary = result.consume()
    return summary

def create(tx):
    pass
