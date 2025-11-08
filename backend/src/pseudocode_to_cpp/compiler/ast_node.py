import json
from enum import Enum, auto
from typing import Any, Dict, List, Union

class ASTNodeType(Enum):
    PROGRAM = auto()
    VAR_DECL = auto()
    ASSIGNMENT = auto()
    IF = auto()
    WHILE = auto()         # cat timp ... executa / do ... while ()
    DO_WHILE = auto()      # executa ... cat timp / while
    REPEAT_UNTIL = auto()  # repeta ... pana cand / do ... while (not ...)
    FOR = auto()           # pentru / for
    READ = auto()          # citeste / cin >>
    WRITE = auto()         # scrie / cout <<
    BIN_OP = auto()        # +, -, *, /, %, AND, OR, <, >, =, etc.
    UNARY_OP = auto()      # NOT, -, [ ] (cast la int)
    LITERAL = auto()       # numere, string-uri
    VARIABLE = auto()      # identificatori
    BLOCK = auto()
    EOF = auto()

class ASTNode:
    """Base AST node.

    - `kind` is the node type (ASTNodeType).
    - `children` is a list of child ASTNode objects or simple values.
    - `attrs` holds auxiliary information (type inference, source location, etc.).

    Backwards-compatibility: `node_type` and `metadata` properties map to the new names.
    """

    def __init__(self, kind: ASTNodeType):
        self.kind: ASTNodeType = kind
        self.children: List[Union["ASTNode", Any]] = []
        self.attrs: Dict[str, Any] = {}

    @property
    def node_type(self) -> ASTNodeType:
        return self.kind

    @node_type.setter
    def node_type(self, value: ASTNodeType) -> None:
        self.kind = value

    @property
    def metadata(self) -> Dict[str, Any]:
        return self.attrs

    @metadata.setter
    def metadata(self, value: Dict[str, Any]) -> None:
        self.attrs = value

    def add_child(self, child: Union["ASTNode", Any]) -> None:
        """Append a child (ASTNode or raw value)."""
        self.children.append(child)

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-serializable representation (as a dict)."""
        def serialize(item: Union["ASTNode", Any]):
            if isinstance(item, ASTNode):
                return item.to_dict()
            if isinstance(item, list):
                return [serialize(i) for i in item]
            return item

        return {
            "type": self.kind.name,
            "attrs": dict(self.attrs),
            "children": [serialize(c) for c in self.children],
        }

    def to_json(self) -> Dict[str, Any]:
        """Compatibility method: previously returned a dict for JSON serialization.

        Keep this method name to avoid breaking callers that expect `to_json()`.
        """
        return self.to_dict()

    def to_json_str(self, **json_kwargs) -> str:
        """Return a JSON string. Pass kwargs to json.dumps if needed."""
        return json.dumps(self.to_dict(), ensure_ascii=False, **json_kwargs)

    def __repr__(self) -> str:
        return f"<ASTNode {self.kind.name} children={len(self.children)} attrs={self.attrs}>"


# Examples of specialized nodes
class BinOpNode(ASTNode):
    def __init__(self, left: Union[ASTNode, Any], op: str, right: Union[ASTNode, Any]):
        super().__init__(ASTNodeType.BIN_OP)
        # keep a short-name for backward compatibility but prefer `operator`
        self.operator: str = op
        self.op: str = op
        self.children = [left, right]
        self.attrs["operator"] = op

    def __repr__(self) -> str:
        return f"<BinOpNode op={self.operator} children={len(self.children)}>"

class LiteralNode(ASTNode):
    def __init__(self, value: Any, value_type: str):
        super().__init__(ASTNodeType.LITERAL)
        self.value: Any = value
        self.inferred_type: str = value_type  # 'int', 'real', 'bool', 'string'
        self.attrs["value"] = value
        self.attrs["inferred_type"] = value_type

    def __repr__(self) -> str:
        return f"<LiteralNode {self.value!r}:{self.inferred_type}>"
