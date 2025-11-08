import math
import json
from typing import Any, Dict, Optional

from backend.compiler.ast_node import ASTNode, ASTNodeType
from backend.compiler.parser import Parser
from backend.compiler.lexer import lex


def _attribute(node: Any, key: str, default: Any = None) -> Any:
    """Read an attribute from the node, preferring the new `attrs` map but
    falling back to `metadata` for backwards compatibility.
    """
    if node is None:
        return default
    # prefer attrs (new name)
    if hasattr(node, 'attrs') and isinstance(node.attrs, dict):
        return node.attrs.get(key, default)
    if hasattr(node, 'metadata') and isinstance(node.metadata, dict):
        return node.metadata.get(key, default)
    # fallback to direct attribute
    return getattr(node, key) if hasattr(node, key) else default


def _node_type_name(node: Any) -> str:
    # Try multiple attributes to determine node type name
    if node is None:
        return 'NONE'
    if hasattr(node, 'node_type') and getattr(node.node_type, 'name', None):
        return node.node_type.name
    if hasattr(node, 'kind') and getattr(node.kind, 'name', None):
        return node.kind.name
    return node.__class__.__name__.upper()


class Interpreter:
    def __init__(self) -> None:
        # Memoria globală pentru variabile (Symbol Table simplu)
        self.globals: Dict[str, Any] = {}

    # --- Helpers ---

    # --- Visitor dispatch ---
    def visit(self, node: Optional[Any]) -> Any:
        """Dispatcher principal: apelează metoda potrivită pentru tipul nodului."""
        if node is None:
            return None

        node_name = _node_type_name(node)
        method_name = f'visit_{node_name}'
        visitor = getattr(self, method_name, None)
        if visitor is None:
            return self.generic_visit(node)
        return visitor(node)

    # --- Node handlers ---
    def visit_LITERAL(self, node: Any) -> Any:
        # Return raw value (convert types where appropriate)
        # Value can be stored both as attribute or inside attrs/metadata
        val = getattr(node, 'value', _attribute(node, 'value'))
        inferred = _attribute(node, 'inferred_type')

        if inferred == 'real':
            return float(val)
        if inferred == 'int':
            return int(val)
        if inferred == 'var':
            var_name = val
            if var_name in self.globals:
                return self.globals[var_name]
            line = _attribute(node, 'line', '?')
            raise NameError(f"Variabilă nedefinită '{var_name}' la linia {line}")
        # strings or other types
        return val

    def visit_BIN_OP(self, node: Any) -> Any:
        # Binary operator: left and right children expected
        if not getattr(node, 'children', None) or len(node.children) < 2:
            raise ValueError('BIN_OP fără doi copii')
        left = self.visit(node.children[0])
        right = self.visit(node.children[1])
        op = _attribute(node, 'operator', getattr(node, 'op', None))
        if op is None:
            raise ValueError('Operator lipsă pentru BIN_OP')

        op_up = str(op).upper()
        if op_up == 'OR':
            return left or right
        if op_up == 'AND':
            return left and right

        if op == '+':
            return left + right
        if op == '-':
            return left - right
        if op == '*':
            return left * right
        if op == '/':
            return left / right
        if op == '%':
            return left % right
        # relational
        if op == '=':
            return left == right
        if op in ('!=', '≠'):
            return left != right
        if op == '<':
            return left < right
        if op == '>':
            return left > right
        if op in ('<=', '≤'):
            return left <= right
        if op in ('>=', '≥'):
            return left >= right
        if op == '^':
            return left ** right

        raise Exception(f"Operator necunoscut: {op}")

    def visit_UNARY_OP(self, node: Any) -> Any:
        if not getattr(node, 'children', None) or len(node.children) < 1:
            raise ValueError('UNARY_OP fără operand')
        op = _attribute(node, 'operator', getattr(node, 'op', None))
        val = self.visit(node.children[0])

        if op == 'SQRT':
            return math.sqrt(val)
        if op == 'FLOOR':
            return math.floor(val)
        if op == 'NOT':
            return not val
        if op == 'MINUS':
            return -val

        raise Exception(f"Operator unar necunoscut: {op}")

    def visit_PROGRAM(self, node: Any) -> None:
        for stmt in getattr(node, 'children', []):
            self.visit(stmt)

    def visit_BLOCK(self, node: Any) -> None:
        for stmt in getattr(node, 'children', []):
            self.visit(stmt)

    def visit_ASSIGNMENT(self, node: Any) -> None:
        # Expect children: [var_literal, expr]
        if not getattr(node, 'children', None) or len(node.children) < 2:
            raise ValueError('ASSIGNMENT nod invalid')
        var_node = node.children[0]
        var_name = getattr(var_node, 'value', None) or _attribute(var_node, 'value')
        val = self.visit(node.children[1])
        if var_name is None:
            raise ValueError('Numele variabilei lipsă la ASSIGNMENT')
        self.globals[var_name] = val

    def visit_IF(self, node: Any) -> None:
        cond = self.visit(node.children[0])
        if cond:
            self.visit(node.children[1])
        else:
            if len(node.children) > 2 and node.children[2]:
                self.visit(node.children[2])

    def visit_WHILE(self, node: Any) -> None:
        # Child 0: condition, Child 1: body
        while self.visit(node.children[0]):
            self.visit(node.children[1])

    def visit_FOR(self, node: Any) -> None:
        # Node children: [start, stop, step, body]
        var_name = _attribute(node, 'iterator')
        if var_name is None:
            raise ValueError('FOR fără iterator în metadata')

        start_val = self.visit(node.children[0])
        stop_val = self.visit(node.children[1])
        step_val = self.visit(node.children[2])
        body = node.children[3]

        self.globals[var_name] = start_val

        while True:
            curr_val = self.globals[var_name]
            if step_val > 0 and curr_val > stop_val:
                break
            if step_val < 0 and curr_val < stop_val:
                break

            self.visit(body)
            self.globals[var_name] += step_val

    def visit_REPEAT_UNTIL(self, node: Any) -> None:
        # Child 0: body, Child 1: condition
        while True:
            self.visit(node.children[0])
            if self.visit(node.children[1]):
                break

    def visit_DO_WHILE(self, node: Any) -> None:
        while True:
            self.visit(node.children[0])
            if not self.visit(node.children[1]):
                break

    def visit_READ(self, node: Any) -> None:
        for var_node in getattr(node, 'children', []):
            var_name = getattr(var_node, 'value', None) or _attribute(var_node, 'value')
            raw_val = input(f"Introduceți valoare pentru {var_name}: ")
            try:
                if '.' in raw_val:
                    val = float(raw_val)
                else:
                    val = int(raw_val)
            except ValueError:
                val = raw_val
            self.globals[var_name] = val

    def visit_WRITE(self, node: Any) -> None:
        output_parts = []
        for expr in getattr(node, 'children', []):
            val = self.visit(expr)
            if isinstance(val, str):
                val = val.replace('\\n', '\n')
            output_parts.append(str(val))
        print("".join(output_parts))

    def generic_visit(self, node: Any) -> None:
        name = _node_type_name(node)
        raise Exception(f'Nu există metodă visit_{name}')


# --- COD MAIN DE TEST ---
if __name__ == "__main__":
    code_sample = """
    daca 1 != 2 si adevarat atunci
        scrie "FALS"
    sfarsit_daca
    
    citeste n
    pentru i <- 1, n - 1 executa
        pentru j <- i + 1, n executa
            daca (i + j) % 2 = 0 atunci
                scrie "PERECHEA (", i, ",", j, ") ESTE O SUMA PARA"
            altfel
                scrie "PERECHEA (", i, ",", j, ") ESTE O SUMA IMPARA"
            sfarsit_daca
        sfarsit_pentru
    sfarsit_pentru
    """

    interpreter = Interpreter()
    try:
        tokens = list(lex(code_sample))
        parser = Parser(tokens)
        ast = parser.parse_program()
        # print AST for debugging
        print(json.dumps(ast.to_json(), indent=2))
    except (SyntaxError, ValueError) as e:
        print(f"Eroare: {e}")
        raise SystemExit(-1)

    try:
        print("--- Început Execuție ---")
        interpreter.visit(ast)
        print("\n--- Final Execuție ---")
        print("Memorie finală:", interpreter.globals)
    except Exception as e:
        print(f"Eroare la execuție: {e}")
        raise
