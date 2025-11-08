import json
from typing import Any, Dict, List, Optional
from backend.src.pseudocode_to_cpp.compiler.ast_node import ASTNodeType, ASTNode, BinOpNode, LiteralNode
# Presupunem că lexer-ul e în lexer.py și funcționează conform discuției anterioare
from backend.src.pseudocode_to_cpp.compiler.lexer import lex


class Parser:
    def __init__(self, tokens: List[Dict[str, Any]]):
        # Use clearer attribute names internally
        self.token_list: List[Dict[str, Any]] = list(tokens)
        self.index: int = 0

    # Backwards-compatible accessors
    @property
    def tokens(self) -> List[Dict[str, Any]]:
        return self.token_list

    @property
    def position(self) -> int:
        return self.index

    @position.setter
    def position(self, value: int) -> None:
        self.index = value

    # --- Low-level token helpers ---
    def current_token(self) -> Dict[str, Any]:
        if self.index < len(self.token_list):
            return self.token_list[self.index]
        # Fallback EOF-like token if we walked past the end
        return {"type": "EOF", "value": "", "line": -1, "col": 0}

    def current_type(self) -> str:
        return self.current_token().get("type", "EOF")

    def peek(self) -> Dict[str, Any]:
        """Compatibility: return the current token (or EOF token)."""
        return self.current_token()

    def consume_token(self, expected_type: Optional[str] = None) -> Dict[str, Any]:
        """Consume and return the current token.

        If expected_type is provided, require the token to match and raise a
        SyntaxError otherwise. If we hit EOF unexpectedly, raise SyntaxError.
        """
        if self.index >= len(self.token_list):
            raise SyntaxError("Unexpected end of input (EOF)")

        token = self.token_list[self.index]
        if expected_type is not None and token.get("type") != expected_type:
            raise SyntaxError(
                f"Așteptam {expected_type}, am găsit {token.get('type')} la linia {token.get('line')}"
            )
        # advance
        self.index += 1
        return token

    def accept_token(self, expected_type: str) -> Optional[Dict[str, Any]]:
        """If the current token matches expected_type, consume and return it;
        otherwise return None (no exception).
        """
        if self.current_type() == expected_type:
            return self.consume_token(expected_type)
        return None

    def expect_token(self, expected_type: str) -> Dict[str, Any]:
        """Like accept but raises with a clear message when the token doesn't match."""
        token = self.accept_token(expected_type)
        if token is None:
            current_token = self.current_token()
            raise SyntaxError(f"Așteptam '{expected_type}' la linia {current_token.get('line')}")
        return token

    # --- High-level parsing API ---
    def parse_program(self) -> ASTNode:
        statements: List[ASTNode] = []
        # Ne oprim explicit când întâlnim token-ul EOF
        while self.current_type() != 'EOF':
            statements.append(self.parse_statement())
        program_node = ASTNode(ASTNodeType.PROGRAM)
        program_node.children = statements
        return program_node

    def parse_statement(self) -> ASTNode:
        token = self.peek()
        token_type = token.get('type')

        if token_type == 'ID':
            return self.parse_assign()
        elif token_type == 'CAT_TIMP':
            return self.parse_while()
        elif token_type == 'CITESTE':
            return self.parse_read()
        elif token_type == 'SCRIE':
            return self.parse_write()
        elif token_type == 'PENTRU':
            return self.parse_for()
        elif token_type == 'DACA':
            return self.parse_if()
        elif token_type == 'REPETA':
            return self.parse_repeat_until()
        elif token_type == 'EXECUTA':
            return self.parse_do_while()

        raise SyntaxError(f"Instrucțiune necunoscută '{token.get('value')}' la linia {token.get('line')}")

    def parse_do_while(self) -> ASTNode:
        line = self.current_token().get('line')
        self.expect_token('EXECUTA')

        # Citim corpul buclei până la 'cat timp'
        body_statements = self.parse_block('CAT_TIMP')

        # consume the delimiter and read the condition
        self.expect_token('CAT_TIMP')
        condition = self.parse_expression()

        do_while_node = ASTNode(ASTNodeType.DO_WHILE)
        do_while_node.metadata['line'] = line

        body_node = ASTNode(ASTNodeType.BLOCK)
        body_node.children = body_statements

        do_while_node.children = [body_node, condition]
        return do_while_node

    def parse_repeat_until(self) -> ASTNode:
        line = self.current_token().get('line')
        self.expect_token('REPETA')

        body_stmts = self.parse_block('PANA_CAND')

        self.expect_token('PANA_CAND')
        condition = self.parse_expression()

        repeat_node = ASTNode(ASTNodeType.REPEAT_UNTIL)
        repeat_node.metadata['line'] = line

        body_node = ASTNode(ASTNodeType.BLOCK)
        body_node.children = body_stmts

        repeat_node.children = [body_node, condition]
        return repeat_node

    def parse_if(self) -> ASTNode:
        line = self.current_token().get('line')
        self.expect_token('DACA')

        condition = self.parse_expression()

        # Expect 'ATUNCI'
        if not self.accept_token('ATUNCI'):
            raise SyntaxError(f"Așteptam 'atunci' după condiție la linia {self.current_token().get('line')}")

        # then branch
        then_stmts: List[ASTNode] = []
        while self.current_type() not in ('ALTFEL', 'SFARSIT_DACA', 'EOF'):
            then_stmts.append(self.parse_statement())

        # optional else
        else_stmts: List[ASTNode] = []
        if self.accept_token('ALTFEL'):
            while self.current_type() not in ('SFARSIT_DACA', 'EOF'):
                else_stmts.append(self.parse_statement())

        # require sfarsit_daca
        if not self.accept_token('SFARSIT_DACA'):
            raise SyntaxError("Lipsește 'sfarsit_daca' pentru structura alternativă curentă.")

        if_node = ASTNode(ASTNodeType.IF)
        if_node.metadata['line'] = line

        then_block = ASTNode(ASTNodeType.BLOCK)
        then_block.children = then_stmts

        else_block = ASTNode(ASTNodeType.BLOCK)
        else_block.children = else_stmts

        if_node.children = [condition, then_block, else_block]
        return if_node

    def parse_for(self) -> ASTNode:
        line = self.current_token().get('line')
        self.expect_token('PENTRU')

        if self.current_type() != 'ID':
            raise SyntaxError(f"Așteptam o variabilă după 'pentru' la linia {line}")
        var_name = self.consume_token('ID')['value']

        # initial assignment
        self.expect_token('ASSIGN')
        start_expr = self.parse_expression()

        # comma and stop expression
        self.expect_token('COMMA')
        stop_expr = self.parse_expression()

        # optional step
        step_expr = None
        if self.current_type() == 'COMMA':
            self.consume_token('COMMA')
            step_expr = self.parse_expression()
        else:
            step_expr = LiteralNode('1', 'int')

        # expect 'EXECUTA'
        if not self.accept_token('EXECUTA'):
            raise SyntaxError(f"Așteptam 'executa' la linia {self.current_token().get('line')}")

        body_stmts = self.parse_block('SFARSIT_PENTRU')
        # consume end
        self.expect_token('SFARSIT_PENTRU')

        for_node = ASTNode(ASTNodeType.FOR)
        for_node.metadata['line'] = line
        for_node.metadata['iterator'] = var_name

        body_node = ASTNode(ASTNodeType.BLOCK)
        body_node.children = body_stmts

        for_node.children = [start_expr, stop_expr, step_expr, body_node]
        return for_node

    def parse_write(self) -> ASTNode:
        line = self.current_token().get('line')
        self.expect_token('SCRIE')

        expressions: List[ASTNode] = []
        expressions.append(self.parse_expression())

        while self.current_type() == 'COMMA':
            self.consume_token('COMMA')
            expressions.append(self.parse_expression())

        write_node = ASTNode(ASTNodeType.WRITE)
        write_node.metadata['line'] = line
        write_node.children = expressions
        return write_node

    def parse_read(self) -> ASTNode:
        line = self.current_token().get('line')
        self.expect_token('CITESTE')

        variables: List[str] = []
        if self.current_type() != 'ID':
            raise SyntaxError(f"Așteptam un nume de variabilă după 'citeste' la linia {line}")

        variables.append(self.consume_token('ID')['value'])
        while self.current_type() == 'COMMA':
            self.consume_token('COMMA')
            if self.current_type() != 'ID':
                raise SyntaxError(f"Așteptam variabilă după ',' la linia {self.current_token().get('line')}")
            variables.append(self.consume_token('ID')['value'])

        read_node = ASTNode(ASTNodeType.READ)
        read_node.metadata['line'] = line
        read_node.children = [LiteralNode(v, 'var') for v in variables]
        return read_node

    def parse_assign(self) -> ASTNode:
        line = self.current_token().get('line')
        var_name = self.consume_token('ID')['value']
        # Verificăm dacă urmează o atribuire
        if self.current_type() == 'ASSIGN':
            self.consume_token('ASSIGN')
            expr = self.parse_expression()
            node = ASTNode(ASTNodeType.ASSIGNMENT)
            node.metadata['line'] = line
            node.children = [LiteralNode(var_name, 'var'), expr]
            return node
        else:
            raise SyntaxError(f"Așteptam '<-' după {var_name} la linia {line}")

    def parse_block(self, end_token_type: str) -> List[ASTNode]:
        stmts: List[ASTNode] = []
        # Citim instrucțiuni până la EOF sau până la token-ul de final specificat (ex: SFARSIT_CAT)
        while self.current_type() != 'EOF' and self.current_type() != end_token_type:
            stmts.append(self.parse_statement())
        return stmts

    def parse_while(self) -> ASTNode:
        line = self.current_token().get('line')
        self.expect_token('CAT_TIMP')
        condition = self.parse_expression()

        if not self.accept_token('EXECUTA'):
            raise SyntaxError(f"Așteptam 'executa' la linia {self.current_token().get('line')}")

        stmts = self.parse_block('SFARSIT_CAT')

        # require end token
        if not self.accept_token('SFARSIT_CAT'):
            raise SyntaxError("Lipsește 'sfarsit_cat_timp' pentru bucla curentă.")

        while_node = ASTNode(ASTNodeType.WHILE)
        while_node.metadata['line'] = line

        body_node = ASTNode(ASTNodeType.BLOCK)
        body_node.children = stmts  # <-- FIX: Atașăm instrucțiunile la nod

        while_node.children = [condition, body_node]
        return while_node

    def parse_expression(self) -> ASTNode:
        """Nivelul cel mai de jos: SAU"""
        left = self.parse_logic_term()
        while self.current_type() == 'OR':
            _ = self.consume_token()
            right = self.parse_logic_term()
            left = BinOpNode(left, 'OR', right)
        return left

    def parse_logic_term(self) -> ASTNode:
        """Nivelul SI"""
        left = self.parse_not_factor()
        while self.current_type() == 'AND':
            _ = self.consume_token()
            right = self.parse_not_factor()
            left = BinOpNode(left, 'AND', right)
        return left

    def parse_not_factor(self) -> ASTNode:
        """Nivelul NOT (unar)"""
        if self.current_type() == 'NOT':
            self.consume_token('NOT')
            operand = self.parse_not_factor()  # Recursiv pentru 'not not a'
            node = ASTNode(ASTNodeType.UNARY_OP)
            node.metadata['operator'] = 'NOT'
            node.children = [operand]
            return node
        return self.parse_relational()

    def parse_relational(self) -> ASTNode:
        """Nivelul operatorilor relaționali (=, <, >, etc.)"""
        left = self.parse_arithmetic()
        # Aici permitem doar o singură comparație pentru simplitate (ex: a < b),
        # nu 'a < b < c' (care ar necesita logică specială).
        if self.current_type() in ('EQ', 'NEQ', 'LT', 'LTE', 'GT', 'GTE'):
            op_token = self.consume_token()
            right = self.parse_arithmetic()
            return BinOpNode(left, op_token['value'], right)
        return left

    def parse_arithmetic(self) -> ASTNode:
        """Nivelul +, -"""
        left = self.parse_term_arithmetic()
        while self.current_type() in ('PLUS', 'MINUS'):
            op_token = self.consume_token()
            right = self.parse_term_arithmetic()
            left = BinOpNode(left, op_token['value'], right)
        return left

    def parse_term_arithmetic(self) -> ASTNode:
        """Nivelul *, /, %"""
        left = self.parse_pow()
        while self.current_type() in ('MUL', 'DIV', 'MOD'):
            op_token = self.consume_token()
            right = self.parse_pow()
            left = BinOpNode(left, op_token['value'], right)
        return left

    def parse_pow(self) -> ASTNode:
        """Nivelul ^"""
        left = self.parse_factor()
        while self.current_type() == 'POW':
            op_token = self.consume_token()
            right = self.parse_factor()
            left = BinOpNode(left, op_token['value'], right)
        return left

    def parse_factor(self) -> ASTNode:
        """Cel mai înalt nivel: literali, variabile, paranteze, unari aritmetici"""
        if self.current_type() == 'MINUS':  # Unary minus (-5)
            self.consume_token('MINUS')
            expr = self.parse_factor()
            node = ASTNode(ASTNodeType.UNARY_OP)
            node.metadata['operator'] = 'MINUS'
            node.children = [expr]
            return node
        # ... apelurile existente către _handle_number, _handle_id, etc ...
        return self.parse_term()  # Redenumit vechiul parse_term

    def parse_term(self) -> ASTNode:
        token = self.consume_token()

        if token['type'] == 'NUMBER':
            return self._handle_number(token)
        elif token['type'] == 'STRING':
            return self._handle_string(token)
        elif token['type'] == 'ID':
            return self._handle_id(token)
        elif token['type'] == 'SQRT':
            return self._handle_sqrt(token)
        elif token['type'] == 'LBRACKET':
            return self._handle_floor(token)
        elif token['type'] == 'LPAREN':
            return self._handle_grouped_expr(token)
        elif token["type"] == "TRUE" or token["type"] == "FALSE":
            return LiteralNode(token["value"], 'bool')
        else:
            raise SyntaxError(f"Termen neașteptat '{token['value']}' la linia {token['line']}")

    # --- Helper Methods for Term Parsing ---

    def _handle_number(self, token: Dict[str, Any]) -> LiteralNode:
        v_type = 'real' if '.' in token['value'] else 'int'
        return LiteralNode(token['value'], v_type)

    def _handle_string(self, token: Dict[str, Any]) -> LiteralNode:
        # Strip surrounding quotes (both single and double) and unescape simple escapes
        raw = token['value']
        if raw.startswith(('"', "'")) and raw.endswith(('"', "'")):
            inner = raw[1:-1]
        else:
            inner = raw
        inner = inner.replace('\\"', '"').replace("\\'", "'")
        return LiteralNode(inner, 'string')

    def _handle_id(self, token: Dict[str, Any]) -> LiteralNode:
        return LiteralNode(token['value'], 'var')

    def _handle_sqrt(self, sqrt_token: Dict[str, Any]) -> ASTNode:
        # Expect an opening '('
        if not self.accept_token('LPAREN'):
            raise SyntaxError(f"Așteptam '(' după 'sqrt' la linia {sqrt_token.get('line')}")

        expr = self.parse_expression()

        if not self.accept_token('RPAREN'):
            current_line = self.current_token().get('line')
            raise SyntaxError(f"Așteptam ')' după expresia din 'sqrt' la linia {current_line}")

        node = ASTNode(ASTNodeType.UNARY_OP)
        node.metadata['operator'] = 'SQRT'
        node.metadata['line'] = sqrt_token.get('line')
        node.children = [expr]
        return node

    def _handle_floor(self, token: Dict[str, Any]) -> ASTNode:
        # Handles [ expression ]
        expr = self.parse_expression()
        if not self.accept_token('RBRACKET'):
            current_line = self.current_token().get('line')
            raise SyntaxError(f"Așteptam ']' pentru închiderea părții întregi la linia {current_line}")

        node = ASTNode(ASTNodeType.UNARY_OP)
        node.metadata['operator'] = 'FLOOR'
        node.children = [expr]
        return node

    def _handle_grouped_expr(self, token: Dict[str, Any]) -> ASTNode:
        # Handles ( expression )
        expr = self.parse_expression()
        if not self.accept_token('RPAREN'):
            current_line = self.current_token().get('line')
            raise SyntaxError(f"Așteptam ')' pentru închiderea parantezei la linia {current_line}")
        return expr


# --- TESTARE ---
code_sample = """
daca 1 != 1 si adevarat atunci
    scrie "B"
sfarsit_daca
executa
    a <- sqrt(2^2)  
cat timp a = 6 si a = 3
a <- 10
b <- 20
citeste d, e, f
cat timp a = 3 executa
    s <- a + [b / 3]
sfarsit_cat_timp
"""

if __name__ == "__main__":
    try:
        tokens = list(lex(code_sample))
        parser = Parser(tokens)
        ast = parser.parse_program()
        print(json.dumps(ast.to_json(), indent=2))
    except (SyntaxError, ValueError) as e:
        print(f"Eroare: {e}")