class Node():
    def __init__(self, nodeId, name, lineno, id, value):
        self.nodeId = nodeId
        self.name = name
        self.lineno = lineno
        self.id = id
        self.value = value

    def __hash__(self):
        return hash((self.nodeId, self.name, self.depth, self.id, self.value))

    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        return self.nodeId == other.nodeId and self.name == other.name and self.depth == other.depth and self.id == other.id and self.value == other.value
