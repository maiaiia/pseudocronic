import json
from enum import Enum, auto

class ASTNodeType(Enum):
    PROGRAM = auto()
    VAR_DECL = auto()
    ASSIGNMENT = auto()
    IF = auto()
    WHILE = auto()         # cat timp ... executa
    DO_WHILE = auto()      # executa ... cat timp
    REPEAT_UNTIL = auto()  # repeta ... pana cand
    FOR = auto()           # pentru
    READ = auto()          # citeste
    WRITE = auto()         # scrie
    BIN_OP = auto()        # +, -, *, /, %, AND, OR, <, >, =, etc.
    UNARY_OP = auto()      # NOT, -, [ ] (cast la int)
    LITERAL = auto()       # numere, string-uri
    VARIABLE = auto()      # identificatori
    BLOCK = auto()
    EOF = auto()

class ASTNode:
    def __init__(self, node_type: ASTNodeType):
        self.node_type = node_type
        self.children = []
        self.metadata = {} # Pentru type inference, nr. linie, etc.

    def to_json(self):
        """Returnează o reprezentare dict pentru serializare JSON."""
        return {
            "type": self.node_type.name,
            "metadata": self.metadata,
            "children": [child.to_json() if isinstance(child, ASTNode) else child for child in self.children]
        }

# Exemple de noduri specifice
class BinOpNode(ASTNode):
    def __init__(self, left, op, right):
        super().__init__(ASTNodeType.BIN_OP)
        self.op = op
        self.children = [left, right]
        self.metadata['operator'] = op

class LiteralNode(ASTNode):
    def __init__(self, value, value_type):
        super().__init__(ASTNodeType.LITERAL)
        self.value = value
        self.metadata['value'] = value
        self.metadata['inferred_type'] = value_type # 'int', 'real', 'bool', 'string'