import math
from backend.compiler.ASTNode import ASTNodeType
from backend.compiler.Parser import Parser
from backend.compiler.lexer import lex
import json

class CppTranspiler:
    def __init__(self):
        self.vars = {}  # Stochează tipul variabilelor: 'long long' sau 'double'
        self.indent_level = 1
        self.output = []

    def transpile(self, ast):
        """Metoda principală care orchestrează transpilarea."""
        # Pas 1: Colectează variabilele și deduce tipurile de bază
        self._collect_vars(ast)

        # Pas 2: Generează header-ul standard
        self.emit("#include <iostream>")
        self.emit("#include <cmath>")
        self.emit("")
        self.emit("using namespace std;")
        self.emit("")
        self.emit("int main() {")

        # Pas 3: Declară variabilele colectate
        if self.vars:
            # Grupăm variabilele după tip pentru o declarare mai curată
            long_vars = [v for v, t in self.vars.items() if t == 'long long']
            double_vars = [v for v, t in self.vars.items() if t == 'double']
            int_vals = [v for v, t in self.vars.items() if t == 'int']
            boolean_vals = [v for v, t in self.vars.items() if t == 'bool']

            if long_vars:
                self.emit(f"    long long {', '.join(long_vars)};")
            if double_vars:
                self.emit(f"    double {', '.join(double_vars)};")
            if int_vals:
                self.emit(f"    int {', '.join(int_vals)};")
            if boolean_vals:
                self.emit(f"    bool {', '.join(boolean_vals)};")
            self.emit("")

        # Pas 4: Parcurge AST-ul și generează codul efectiv
        self.visit(ast)

        # Pas 5: Finalizare
        self.emit("")
        self.emit("    return 0;")
        self.emit("}")

        return "\n".join(self.output)

    def emit(self, code, newline=True):
        """Helper pentru adăugarea de cod în bufferul de ieșire."""
        prefix = ""
        # Nu indentăm liniile care încep cu # (directive preprocesor) sau sunt goale
        if code.strip() and not code.startswith("#") and not code.startswith(
                "using") and "main" not in code and "}" not in code:
            prefix = "    " * self.indent_level

        # Tratament special pentru acolada de închidere
        if code.startswith("}"):
            prefix = "    " * (self.indent_level - 1)

        self.output.append(f"{prefix}{code}")

    def _collect_vars(self, node):
        """Parcurgere preliminară pentru a găsi toate variabilele și a le deduce tipul."""
        if not node: return

        # Dacă e o atribuire sau citire, marcăm variabila
        if node.node_type == ASTNodeType.ASSIGNMENT:
            var_name = node.children[0].value
            self._mark_var(var_name, 'int')  # Tip implicit
            # Verificăm expresia atribuită pentru a vedea dacă necesită promovare la double
            self._check_expr_type(node.children[1], var_name)

        elif node.node_type == ASTNodeType.READ:
            for child in node.children:
                self._mark_var(child.value, 'int')

        elif node.node_type == ASTNodeType.FOR:
            self._mark_var(node.metadata['iterator'], 'int')

        # Recursivitate pentru copii
        if hasattr(node, 'children'):
            for child in node.children:
                if hasattr(child, 'node_type'):  # Verificăm să fie ASTNode
                    self._collect_vars(child)

    def _mark_var(self, name, vtype):
        """Înregistrează o variabilă. Promovează la double dacă e cazul."""
        if name not in self.vars:
            self.vars[name] = vtype
        elif vtype == "bool" and self.vars[name] in ("int", "long long"):
            self.vars[name] = "bool"
        elif vtype == 'double' and self.vars[name] in ("int", "long long"):
            self.vars[name] = 'double'  # Promovare

    def _check_expr_type(self, node, target_var=None):
        """Verifică dacă o expresie forțează tipul 'double'."""
        if not node or not hasattr(node, 'node_type'): return
        if node.node_type == ASTNodeType.BIN_OP:
            op = node.metadata['operator']
            if op == '/' or op == 'DIV':  # Împărțirea reală promovează tipul
                if target_var: self._mark_var(target_var, 'double')
            self._check_expr_type(node.children[0], target_var)
            self._check_expr_type(node.children[1], target_var)
        elif node.node_type == ASTNodeType.UNARY_OP:
            if node.metadata['operator'] == 'SQRT':
                if target_var: self._mark_var(target_var, 'double')
            self._check_expr_type(node.children[0], target_var)
        elif node.node_type == ASTNodeType.LITERAL:
            if '.' in str(node.value):
                if target_var: self._mark_var(target_var, 'double')
            elif node.value in ("adevarat", "fals"):
                if target_var: self._mark_var(target_var, 'bool')

    # --- VISITOR METHODS ---

    def visit(self, node):
        method_name = f'visit_{node.node_type.name}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f'No C++ transpiler method for {node.node_type.name}')

    def visit_PROGRAM(self, node):
        for stmt in node.children:
            self.visit(stmt)

    def visit_BLOCK(self, node):
        # Blocurile din {} sunt gestionate de instrucțiunile părinte (IF, WHILE etc),
        # dar dacă avem un bloc independent, îl putem parcurge direct.
        for stmt in node.children:
            self.visit(stmt)

    def visit_ASSIGNMENT(self, node):
        var_name = node.children[0].value
        expr = self.visit_expression(node.children[1])
        self.emit(f"{var_name} = {expr};")

    def visit_READ(self, node):
        vars_str = " >> ".join([child.value for child in node.children])
        self.emit(f"cin >> {vars_str};")

    def visit_WRITE(self, node):
        parts = []
        for child in node.children:
            parts.append(self.visit_expression(child))
        output_str = " << ".join(parts)
        self.emit(f"cout << {output_str};")

    def visit_IF(self, node):
        cond = self.visit_expression(node.children[0])
        self.emit(f"if ({cond}) {{")
        self.indent_level += 1
        self.visit(node.children[1])  # THEN branch
        self.indent_level -= 1

        if len(node.children) > 2 and node.children[2] and node.children[2].children:
            self.emit("} else {")
            self.indent_level += 1
            self.visit(node.children[2])  # ELSE branch
            self.indent_level -= 1

        self.emit("}")

    def visit_WHILE(self, node):
        cond = self.visit_expression(node.children[0])
        self.emit(f"while ({cond}) {{")
        self.indent_level += 1
        self.visit(node.children[1])
        self.indent_level -= 1
        self.emit("}")

    def visit_DO_WHILE(self, node):
        self.emit("do {")
        self.indent_level += 1
        self.visit(node.children[0])  # Body first
        self.indent_level -= 1
        cond = self.visit_expression(node.children[1])
        self.emit(f"}} while ({cond});")

    def visit_REPEAT_UNTIL(self, node):
        self.emit("do {")
        self.indent_level += 1
        self.visit(node.children[0])
        self.indent_level -= 1
        cond = self.visit_expression(node.children[1])
        # IMPORTANT: repeat...until(cond) este echivalent cu while(!cond)
        self.emit(f"}} while (!({cond}));")

    def visit_FOR(self, node):
        var = node.metadata['iterator']
        start = self.visit_expression(node.children[0])
        stop = self.visit_expression(node.children[1])
        step_node = node.children[2]

        # Optimizare: dacă pasul e literal, putem genera cod mai curat
        step_val = 1
        if step_node.node_type == ASTNodeType.LITERAL and step_node.metadata['inferred_type'] == 'int':
            step_val = int(step_node.value)

        step_expr = self.visit_expression(step_node)

        # Generăm o buclă for care încearcă să detecteze direcția.
        # Pentru cazuri simple (pas 1 sau -1), putem hardcoda operatorul de comparație.
        # Pentru caz general, folosim operatorul ternar în condiție: (pas > 0 ? i <= stop : i >= stop)

        cond_op = "<="
        inc_op = f"{var} += {step_expr}"
        if step_val == 1:
            inc_op = f"{var}++"
        elif step_val == -1:
            cond_op = ">="
            inc_op = f"{var}--"
        elif step_val < 0:
            cond_op = ">="

        # Dacă pasul nu e un literal cunoscut, trebuie o condiție generică (mai urâtă, dar sigură)
        if step_node.node_type != ASTNodeType.LITERAL:
            cond_expr = f"({step_expr} >= 0 ? {var} <= {stop} : {var} >= {stop})"
        else:
            cond_expr = f"{var} {cond_op} {stop}"

        self.emit(f"for ({var} = {start}; {cond_expr}; {inc_op}) {{")
        self.indent_level += 1
        self.visit(node.children[3])
        self.indent_level -= 1
        self.emit("}")

    def visit_expression(self, node):
        """Metodă helper care returnează string-ul expresiei, nu emite linie nouă."""
        if node.node_type == ASTNodeType.LITERAL:
            if node.metadata.get('inferred_type') == 'bool':
                boolean_lut: dict = {
                    "adevarat": "true",
                    "fals": "false"
                }
                return f"{boolean_lut[node.value]}"
            elif node.metadata.get('inferred_type') == 'string':
                return f'"{node.value}"'
            return node.value

        elif node.node_type == ASTNodeType.BIN_OP:
            left = self.visit_expression(node.children[0])
            right = self.visit_expression(node.children[1])
            op = node.metadata['operator']

            if op == '/':
                return f"((double){left} / {right})"

            # Mapare operatori pseudocod -> C++
            op_map = {
                '=': '==', '!=': '!=', '≤': '<=', '≥': '>=',
                'AND': '&&', 'OR': '||', 'MOD': '%'
            }
            cpp_op = op_map.get(op, op)
            if op == '^':
                return f"pow({left}, {right})"
            return f"({left} {cpp_op} {right})"

        elif node.node_type == ASTNodeType.UNARY_OP:
            op = node.metadata['operator']
            expr = self.visit_expression(node.children[0])
            if op == 'SQRT': return f"sqrt({expr})"
            if op == 'FLOOR': return f"(long long)({expr})"  # CAST la int
            if op == 'NOT': return f"!({expr})"
            if op == 'MINUS': return f"-({expr})"

        return ""

if __name__ == '__main__':
    code_sample = """
        citeste n
        s <- 0
        ok <- adevarat
        pentru i <- 1, n executa
            s <- s + i
        sfarsit_pentru
        ma <- s / n
        scrie ma
        """

    try:
        tokens = list(lex(code_sample))
        parser = Parser(tokens)
        ast = parser.parse_program()
        print(json.dumps(ast.to_json(), indent=2))
    except (SyntaxError, ValueError) as e:
        print(f"Eroare: {e}")
        exit(-1)

    transpiler = CppTranspiler()
    try:
        print(transpiler.transpile(ast))
    except Exception as e:
        print(f"Eroare la execuție: {e}")