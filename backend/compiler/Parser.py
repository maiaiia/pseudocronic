import json
from backend.compiler.ASTNode import ASTNodeType, ASTNode, BinOpNode, LiteralNode
# Presupunem că lexer-ul e în lexer.py și funcționează conform discuției anterioare
from backend.compiler.lexer import lex


class Parser:
    def __init__(self, tokens):
        self.tokens = list(tokens)
        self.pos = 0

    def consume(self, expected_type=None):
        if self.pos < len(self.tokens):
            token = self.tokens[self.pos]
            if expected_type and token['type'] != expected_type:
                raise SyntaxError(f"Așteptam {expected_type}, am găsit {token['type']} la linia {token['line']}")
            self.pos += 1
            return token
        return None

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def parse_program(self):
        stmts = []
        # Ne oprim explicit când întâlnim token-ul EOF
        while self.peek() and self.peek()['type'] != 'EOF':
            stmts.append(self.parse_statement())
        program_node = ASTNode(ASTNodeType.PROGRAM)
        program_node.children = stmts
        return program_node

    def parse_statement(self):
        token = self.peek()

        if token['type'] == 'ID':
            return self.parse_assign()
        elif token['type'] == 'CAT_TIMP':
            return self.parse_while()
        elif token['type'] == 'CITESTE':
            return self.parse_read()
        elif token['type'] == 'SCRIE':
            return self.parse_write()
        elif token['type'] == 'PENTRU':
            return self.parse_for()
        elif token['type'] == 'DACA':
            return self.parse_if()
        elif token['type'] == 'REPETA':
            return self.parse_repeat_until()
        elif token['type'] == 'EXECUTA':
            return self.parse_do_while()

        raise SyntaxError(f"Instrucțiune necunoscută '{token['value']}' la linia {token['line']}")

    def parse_do_while(self):
        line = self.peek()['line']
        self.consume('EXECUTA')

        # Citim corpul buclei până la 'cat timp'
        # Atenție: Aici 'cat timp' este folosit ca delimitator final, nu ca început de buclă.
        body_stmts = self.parse_block('CAT_TIMP')

        self.consume('CAT_TIMP')
        condition = self.parse_expression()

        # Creăm nodul DO_WHILE
        do_while_node = ASTNode(ASTNodeType.DO_WHILE)
        do_while_node.metadata['line'] = line

        body_node = ASTNode(ASTNodeType.BLOCK)
        body_node.children = body_stmts

        # Ordinea copiilor: bloc instrucțiuni, apoi condiția
        do_while_node.children = [body_node, condition]

        return do_while_node

    def parse_repeat_until(self):
        line = self.peek()['line']
        self.consume('REPETA')

        # Citim corpul buclei până la 'pana cand'
        body_stmts = self.parse_block('PANA_CAND')

        self.consume('PANA_CAND')
        condition = self.parse_expression()

        # Creăm nodul REPEAT_UNTIL
        repeat_node = ASTNode(ASTNodeType.REPEAT_UNTIL)
        repeat_node.metadata['line'] = line

        body_node = ASTNode(ASTNodeType.BLOCK)
        body_node.children = body_stmts

        # Ordinea copiilor: bloc instrucțiuni, apoi condiția
        repeat_node.children = [body_node, condition]

        return repeat_node

    def parse_if(self):
        line = self.peek()['line']
        self.consume('DACA')

        # 1. Condiția
        condition = self.parse_expression()

        # 2. 'atunci'
        if not self.consume('ATUNCI'):
            raise SyntaxError(f"Așteptam 'atunci' după condiție la linia {self.peek()['line']}")

        # 3. Ramura 'then' (adevărat)
        # Citim până la 'ALTFEL', 'SFARSIT_DACA' sau 'EOF'
        then_stmts = []
        while self.peek()['type'] not in ('ALTFEL', 'SFARSIT_DACA', 'EOF'):
            then_stmts.append(self.parse_statement())

        # 4. Ramura 'else' (opțională)
        else_stmts = []
        if self.peek()['type'] == 'ALTFEL':
            self.consume('ALTFEL')
            # Citim până la 'SFARSIT_DACA' sau 'EOF'
            while self.peek()['type'] not in ('SFARSIT_DACA', 'EOF'):
                else_stmts.append(self.parse_statement())

        # 5. 'sfarsit_daca'
        if not self.consume('SFARSIT_DACA'):
            raise SyntaxError("Lipsește 'sfarsit_daca' pentru structura alternativă curentă.")

        # 6. Construirea nodului IF
        if_node = ASTNode(ASTNodeType.IF)
        if_node.metadata['line'] = line

        then_block = ASTNode(ASTNodeType.BLOCK)
        then_block.children = then_stmts

        else_block = ASTNode(ASTNodeType.BLOCK)
        else_block.children = else_stmts

        # Copiii vor fi: [condiție, bloc_then, bloc_else]
        if_node.children = [condition, then_block, else_block]

        return if_node

    def parse_for(self):
        line = self.peek()['line']
        self.consume('PENTRU')

        # 1. Variabila contor
        if self.peek()['type'] != 'ID':
            raise SyntaxError(f"Așteptam o variabilă după 'pentru' la linia {line}")
        var_name = self.consume('ID')['value']

        # 2. Atribuirea valorii inițiale
        if not self.consume('ASSIGN'):  # Acceptă <- sau :=
            raise SyntaxError(f"Așteptam '<-' după variabila contor la linia {line}")
        start_expr = self.parse_expression()

        # 3. Virgula și valoarea finală
        self.consume('COMMA')
        stop_expr = self.parse_expression()

        # 4. Pasul opțional
        step_expr = None
        if self.peek()['type'] == 'COMMA':
            self.consume('COMMA')
            step_expr = self.parse_expression()
        else:
            # Dacă lipsește, pasul implicit este 1 (vom gestiona asta la execuție/transpilare,
            # dar putem pune un LiteralNode(1) aici pentru consistență)
            step_expr = LiteralNode('1', 'int')

        # 5. Corpul buclei
        if not self.consume('EXECUTA'):
            raise SyntaxError(f"Așteptam 'executa' la linia {self.peek()['line']}")

        body_stmts = self.parse_block('SFARSIT_PENTRU')
        self.consume('SFARSIT_PENTRU')  # Presupunem că există acest token, sau folosim un generic SFARSIT

        # 6. Construirea nodului FOR
        for_node = ASTNode(ASTNodeType.FOR)
        for_node.metadata['line'] = line
        for_node.metadata['iterator'] = var_name

        body_node = ASTNode(ASTNodeType.BLOCK)
        body_node.children = body_stmts

        # Ordinea copiilor: start, stop, step, body
        for_node.children = [start_expr, stop_expr, step_expr, body_node]

        return for_node

    def parse_write(self):
        line = self.peek()['line']
        self.consume('SCRIE')  # Consumă 'scrie'

        expressions = []
        # Prima expresie este obligatorie
        expressions.append(self.parse_expression())

        # Cât timp găsim virgule, continuăm să citim expresii
        while self.peek()['type'] == 'COMMA':
            self.consume('COMMA')
            expressions.append(self.parse_expression())

        # Creăm nodul WRITE
        write_node = ASTNode(ASTNodeType.WRITE)
        write_node.metadata['line'] = line
        # Copiii nodului WRITE sunt expresiile ce trebuie evaluate și afișate
        write_node.children = expressions

        return write_node

    def parse_read(self):
        line = self.peek()['line']
        self.consume('CITESTE')

        variables = []
        if self.peek()['type'] != 'ID':
            raise SyntaxError(f"Așteptam un nume de variabilă după 'citeste' la linia {line}")

        variables.append(self.consume('ID')['value'])

        while self.peek()['type'] == 'COMMA':
            self.consume('COMMA')
            if self.peek()['type'] != 'ID':
                raise SyntaxError(f"Așteptam variabilă după ',' la linia {self.peek()['line']}")
            variables.append(self.consume('ID')['value'])

        read_node = ASTNode(ASTNodeType.READ)
        read_node.metadata['line'] = line
        read_node.children = [LiteralNode(v, 'var') for v in variables]
        return read_node

    def parse_assign(self):
        line = self.peek()['line']
        var_name = self.consume('ID')['value']
        # Verificăm dacă urmează o atribuire
        if self.peek()['type'] == 'ASSIGN':
            self.consume('ASSIGN')
            expr = self.parse_expression()
            node = ASTNode(ASTNodeType.ASSIGNMENT)
            node.metadata['line'] = line
            node.children = [LiteralNode(var_name, 'var'), expr]
            return node
        else:
            raise SyntaxError(f"Așteptam '<-' după {var_name} la linia {line}")

    def parse_block(self, end_token_type):
        stmts = []
        # Citim instrucțiuni până la EOF sau până la token-ul de final specificat (ex: SFARSIT_CAT)
        while self.peek()['type'] != 'EOF' and self.peek()['type'] != end_token_type:
            stmts.append(self.parse_statement())
        return stmts

    def parse_while(self):
        line = self.peek()['line']
        self.consume("CAT_TIMP")
        condition = self.parse_expression()

        if not self.consume('EXECUTA'):
            raise SyntaxError(f"Așteptam 'executa' la linia {self.peek()['line']}")

        stmts = self.parse_block('SFARSIT_CAT')

        if not self.consume('SFARSIT_CAT'):
            raise SyntaxError("Lipsește 'sfarsit_cat_timp' pentru bucla curentă.")

        while_node = ASTNode(ASTNodeType.WHILE)
        while_node.metadata['line'] = line

        # Creăm un nod BLOCK pentru a grupa instrucțiunile din corp
        body_node = ASTNode(ASTNodeType.BLOCK)
        body_node.children = stmts  # <-- FIX: Atașăm instrucțiunile la nod

        while_node.children = [condition, body_node]
        return while_node

    def parse_expression(self):
        """Nivelul cel mai de jos: SAU"""
        left = self.parse_logic_term()
        while self.peek()['type'] == 'OR':
            op = self.consume()['value'] # 'sau'
            right = self.parse_logic_term()
            left = BinOpNode(left, 'OR', right)
        return left

    def parse_logic_term(self):
        """Nivelul SI"""
        left = self.parse_not_factor()
        while self.peek()['type'] == 'AND':
            op = self.consume()['value'] # 'si'
            right = self.parse_not_factor()
            left = BinOpNode(left, 'AND', right)
        return left

    def parse_not_factor(self):
        """Nivelul NOT (unar)"""
        if self.peek()['type'] == 'NOT':
            self.consume('NOT')
            operand = self.parse_not_factor() # Recursiv pentru 'not not a'
            node = ASTNode(ASTNodeType.UNARY_OP)
            node.metadata['operator'] = 'NOT'
            node.children = [operand]
            return node
        return self.parse_relational()

    def parse_relational(self):
        """Nivelul operatorilor relaționali (=, <, >, etc.)"""
        left = self.parse_arithmetic()
        # Aici permitem doar o singură comparație pentru simplitate (ex: a < b),
        # nu 'a < b < c' (care ar necesita logică specială).
        if self.peek()['type'] in ('EQ', 'NEQ', 'LT', 'LTE', 'GT', 'GTE'):
            op_token = self.consume()
            right = self.parse_arithmetic()
            return BinOpNode(left, op_token['value'], right)
        return left

    def parse_arithmetic(self):
        """Nivelul +, -"""
        left = self.parse_term_arithmetic()
        while self.peek()['type'] in ('PLUS', 'MINUS'):
            op = self.consume()['value']
            right = self.parse_term_arithmetic()
            left = BinOpNode(left, op, right)
        return left

    def parse_term_arithmetic(self):
        """Nivelul *, /, %"""
        left = self.parse_pow()
        while self.peek()['type'] in ('MUL', 'DIV', 'MOD'):
            op = self.consume()['value']
            right = self.parse_pow()
            left = BinOpNode(left, op, right)
        return left

    def parse_pow(self):
        """Nivelul ^"""
        left = self.parse_factor()
        while self.peek()['type'] == 'POW':
            op = self.consume()['value']
            right = self.parse_factor()
            left = BinOpNode(left, op, right)
        return left

    def parse_factor(self):
        """Cel mai înalt nivel: literali, variabile, paranteze, unari aritmetici"""
        token = self.peek()
        if token['type'] == 'MINUS': # Unary minus (-5)
            self.consume()
            expr = self.parse_factor()
            node = ASTNode(ASTNodeType.UNARY_OP)
            node.metadata['operator'] = 'MINUS'
            node.children = [expr]
            return node
        # ... apelurile existente către _handle_number, _handle_id, etc ...
        return self.parse_term() # Redenumit vechiul parse_term

    def parse_term(self):
        token = self.consume()

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

    def _handle_number(self, token):
        v_type = 'real' if '.' in token['value'] else 'int'
        return LiteralNode(token['value'], v_type)

    def _handle_string(self, token):
        return LiteralNode(token['value'].strip('"\''), 'string')

    def _handle_id(self, token):
        return LiteralNode(token['value'], 'var')

    def _handle_sqrt(self, sqrt_token):
        if not self.consume('LPAREN'):
            raise SyntaxError(f"Așteptam '(' după 'sqrt' la linia {sqrt_token['line']}")

        expr = self.parse_expression()

        if not self.consume('RPAREN'):
            # Uses peek() here because we haven't consumed the wrong token yet
            current_line = self.peek()['line'] if self.peek() else 'EOF'
            raise SyntaxError(f"Așteptam ')' după expresia din 'sqrt' la linia {current_line}")

        node = ASTNode(ASTNodeType.UNARY_OP)
        node.metadata['operator'] = 'SQRT'
        node.metadata['line'] = sqrt_token['line']
        node.children = [expr]
        return node

    def _handle_floor(self, token):
        # Handles [ expression ]
        expr = self.parse_expression()
        if not self.consume('RBRACKET'):
            current_line = self.peek()['line'] if self.peek() else 'EOF'
            raise SyntaxError(f"Așteptam ']' pentru închiderea părții întregi la linia {current_line}")

        node = ASTNode(ASTNodeType.UNARY_OP)
        node.metadata['operator'] = 'FLOOR'
        node.children = [expr]
        return node

    def _handle_grouped_expr(self, token):
        # Handles ( expression )
        expr = self.parse_expression()
        if not self.consume('RPAREN'):
            current_line = self.peek()['line'] if self.peek() else 'EOF'
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