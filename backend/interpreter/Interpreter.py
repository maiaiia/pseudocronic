import math
from backend.compiler.ASTNode import ASTNodeType
from backend.compiler.Parser import Parser
from backend.compiler.lexer import lex
import json


class Interpreter:
    def __init__(self):
        # Memoria globală pentru variabile (Symbol Table simplu)
        self.globals = {}

    def visit(self, node):
        """Dispatcher principal: apelează metoda potrivită pentru tipul nodului."""
        if node is None:
            return None

        # Construim dinamic numele metodei, ex: 'visit_BIN_OP'
        method_name = f'visit_{node.node_type.name}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def visit_LITERAL(self, node):
        # Returnează valoarea raw. Dacă e număr, asigură-te că e tipul corect Python.
        val = node.value
        if node.metadata.get('inferred_type') == 'real':
            return float(val)
        elif node.metadata.get('inferred_type') == 'int':
            return int(val)
        elif node.metadata.get('inferred_type') == 'var':
            # Este o variabilă, o căutăm în memorie
            var_name = node.value
            if var_name in self.globals:
                return self.globals[var_name]
            else:
                raise NameError(f"Variabilă nedefinită '{var_name}' la linia {node.metadata.get('line', '?')}")
        return val  # String-uri sau alte tipuri

    def visit_BIN_OP(self, node):
        left = self.visit(node.children[0])
        right = self.visit(node.children[1])
        op = node.metadata['operator']

        if op.upper() == 'OR': return left or right
        if op.upper() == 'AND': return left and right
        if op == '+': return left + right
        if op == '-': return left - right
        if op == '*': return left * right
        if op == '/': return left / right  # Împărțire reală
        if op == '%': return left % right
        # Operatori relaționali
        if op == '=': return left == right
        if op == '!=' or op == '≠': return left != right
        if op == '<': return left < right
        if op == '>': return left > right
        if op == '<=' or op == '≤': return left <= right
        if op == '>=' or op == '≥': return left >= right
        if op == '^': return left ** right

        raise Exception(f"Operator necunoscut: {op}")

    def visit_UNARY_OP(self, node):
        op = node.metadata['operator']
        expr_val = self.visit(node.children[0])

        if op == 'SQRT':
            return math.sqrt(expr_val)
        elif op == 'FLOOR':
            return math.floor(expr_val)  # Sau int(expr_val) pentru trunchiere
        elif op == 'NOT':
            return not expr_val
        elif op == 'MINUS':  # Negare unară (-x)
            return -expr_val

        raise Exception(f"Operator unar necunoscut: {op}")

    def visit_PROGRAM(self, node):
        for stmt in node.children:
            self.visit(stmt)

    def visit_BLOCK(self, node):
        for stmt in node.children:
            self.visit(stmt)

    def visit_ASSIGNMENT(self, node):
        var_name = node.children[0].value
        expr_val = self.visit(node.children[1])
        self.globals[var_name] = expr_val

    def visit_IF(self, node):
        condition = self.visit(node.children[0])
        if condition:
            self.visit(node.children[1])  # Ramura THEN
        else:
            # Verificăm dacă există ramura ELSE (poate fi un Block gol sau lipsă)
            if len(node.children) > 2 and node.children[2]:
                self.visit(node.children[2])

    def visit_WHILE(self, node):
        # Copil 0: Condiție, Copil 1: Corp
        while self.visit(node.children[0]):
            self.visit(node.children[1])

    def visit_FOR(self, node):
        # Structura nodului FOR: [start_expr, stop_expr, step_expr, body_block]
        # Metadata: iterator (numele variabilei)

        var_name = node.metadata['iterator']
        start_val = self.visit(node.children[0])
        stop_val = self.visit(node.children[1])
        step_val = self.visit(node.children[2])
        body = node.children[3]

        # Inițializare
        self.globals[var_name] = start_val

        # Execuție buclă (implementare manuală pentru a respecta pasul variabil)
        # Atenție: trebuie să gestionăm pas pozitiv vs negativ pentru condiția de oprire
        while True:
            curr_val = self.globals[var_name]
            if step_val > 0 and curr_val > stop_val:
                break
            if step_val < 0 and curr_val < stop_val:
                break

            self.visit(body)
            self.globals[var_name] += step_val

    def visit_REPEAT_UNTIL(self, node):
        # Copil 0: Corp, Copil 1: Condiție
        # Execută cel puțin o dată, se oprește când condiția devine ADEVĂRATĂ
        while True:
            self.visit(node.children[0])
            condition = self.visit(node.children[1])
            if condition:
                break

    def visit_DO_WHILE(self, node):
        # Copil 0: Corp, Copil 1: Condiție
        # Execută cel puțin o dată, continuă CÂT TIMP condiția e ADEVĂRATĂ
        while True:
            self.visit(node.children[0])
            condition = self.visit(node.children[1])
            if not condition:
                break

    def visit_READ(self, node):
        for var_node in node.children:
            var_name = var_node.value
            # O implementare simplă care cere input de la tastatură pentru fiecare variabilă.
            # Într-un mediu real (web), ai lua valorile dintr-un input buffer pre-populat.
            raw_val = input(f"Introduceți valoare pentru {var_name}: ")
            try:
                # Încercăm să convertim automat la număr dacă e posibil
                if '.' in raw_val:
                    val = float(raw_val)
                else:
                    val = int(raw_val)
            except ValueError:
                # Dacă nu e număr, rămâne string
                val = raw_val
            self.globals[var_name] = val

    def visit_WRITE(self, node):
        output_parts = []
        for expr in node.children:
            val = self.visit(expr)
            # Gestionăm caractere speciale basic, ex: \n
            if isinstance(val, str):
                val = val.replace('\\n', '\n')
            output_parts.append(str(val))
        print("".join(output_parts))

    def generic_visit(self, node):
        raise Exception(f'Nu există metodă visit_{node.node_type.name}')


# --- COD MAIN DE TEST ---
if __name__ == "__main__":
    # Presupunem că avem deja 'ast' generat de parser din exemplul anterior
    # cod_test = """ ... """ -> lex -> parse -> ast

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
        print(json.dumps(ast.to_json(), indent=2))
    except (SyntaxError, ValueError) as e:
        print(f"Eroare: {e}")
        exit(-1)

    try:
        print("--- Început Execuție ---")
        interpreter.visit(ast)
        print("\n--- Final Execuție ---")
        print("Memorie finală:", interpreter.globals)
    except Exception as e:
        print(f"Eroare la execuție: {e}")