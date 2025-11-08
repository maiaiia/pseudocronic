import math
import json
from typing import Any, Dict, List, Optional

# Use the refactored compiler modules (capitalized filenames)
from backend.compiler.ast_node import ASTNodeType, ASTNode
from backend.compiler.parser import Parser
from backend.compiler.lexer import lex


class CppTranspiler:
    def __init__(self) -> None:
        self.vars: Dict[str, str] = {}  # Stochează tipul variabilelor: 'long long' sau 'double' etc.
        self.indent_level: int = 1
        self.output: List[str] = []

    def transpile(self, ast: ASTNode) -> str:
        """Metoda principală care orchestrează transpilarea."""
        # Pas 1: Colectează variabilele și deduce tipurile de bază
        self.vars.clear()
        self.output.clear()
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

    def emit(self, code: str, newline: bool = True) -> None:
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

    def _collect_vars(self, node: Optional[ASTNode]) -> None:
        """Parcurgere preliminară pentru a găsi toate variabilele și a le deduce tipul."""
        if not node:
            return

        # Dacă e o atribuire sau citire, marcăm variabila
        if getattr(node, 'node_type', None) == ASTNodeType.ASSIGNMENT:
            var_name = getattr(node.children[0], 'value', None)
            self._mark_var(var_name, 'int')  # Tip implicit
            # Verificăm expresia atribuită pentru a vedea dacă necesită promovare la double
            self._check_expr_type(node.children[1], var_name)

        elif getattr(node, 'node_type', None) == ASTNodeType.READ:
            for child in node.children:
                child_name = getattr(child, 'value', None)
                if child_name is not None:
                    self._mark_var(child_name, 'int')

        elif getattr(node, 'node_type', None) == ASTNodeType.FOR:
            # metadata kept for backward compatibility
            iterator = None
            if hasattr(node, 'metadata') and isinstance(node.metadata, dict):
                iterator = node.metadata.get('iterator')
            if iterator is None and hasattr(node, 'attrs') and isinstance(node.attrs, dict):
                iterator = node.attrs.get('iterator')
            if iterator:
                self._mark_var(iterator, 'int')

        # Recursivitate pentru copii
        if hasattr(node, 'children'):
            for child in node.children:
                if hasattr(child, 'node_type') or hasattr(child, 'kind'):
                    self._collect_vars(child)

    def _mark_var(self, name: str, vtype: str) -> None:
        """Înregistrează o variabilă. Promovează la double dacă e cazul."""
        if name not in self.vars:
            self.vars[name] = vtype
        elif vtype == "bool" and self.vars[name] in ("int", "long long"):
            self.vars[name] = "bool"
        elif vtype == 'double' and self.vars[name] in ("int", "long long"):
            self.vars[name] = 'double'  # Promovare

    def _check_expr_type(self, node: Optional[ASTNode], target_var: Optional[str] = None) -> None:
        """Verifică dacă o expresie forțează tipul 'double'."""
        if not node or not (hasattr(node, 'node_type') or hasattr(node, 'kind')):
            return
        node_type = getattr(node, 'node_type', None) or getattr(node, 'kind', None)
        if node_type == ASTNodeType.BIN_OP:
            # operator may be stored in metadata or attrs
            op = None
            if hasattr(node, 'metadata') and isinstance(node.metadata, dict):
                op = node.metadata.get('operator')
            if op is None and hasattr(node, 'attrs') and isinstance(node.attrs, dict):
                op = node.attrs.get('operator')
            if op == '/' or op == 'DIV':  # Împărțirea reală promovează tipul
                if target_var:
                    self._mark_var(target_var, 'double')
            self._check_expr_type(node.children[0], target_var)
            self._check_expr_type(node.children[1], target_var)
        elif node_type == ASTNodeType.UNARY_OP:
            op = None
            if hasattr(node, 'metadata') and isinstance(node.metadata, dict):
                op = node.metadata.get('operator')
            if op == 'SQRT' and target_var:
                self._mark_var(target_var, 'double')
            self._check_expr_type(node.children[0], target_var)
        elif node_type == ASTNodeType.LITERAL:
            val = getattr(node, 'value', None)
            if val is not None and '.' in str(val):
                if target_var:
                    self._mark_var(target_var, 'double')
            elif val in ("adevarat", "fals"):
                if target_var:
                    self._mark_var(target_var, 'bool')

    # --- VISITOR METHODS ---

    def visit(self, node: ASTNode) -> None:
        method_name = f'visit_{getattr(node, "node_type", getattr(node, "kind", None)).name}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: ASTNode):
        # Support both metadata and attrs for friendly error message
        nodename = getattr(node, 'node_type', getattr(node, 'kind', node.__class__)).name
        raise Exception(f'No C++ transpiler method for {nodename}')

    def visit_PROGRAM(self, node: ASTNode) -> None:
        for stmt in node.children:
            self.visit(stmt)

    def visit_BLOCK(self, node: ASTNode) -> None:
        # Blocurile din {} sunt gestionate de instrucțiunile părinte (IF, WHILE etc),
        # dar dacă avem un bloc independent, îl putem parcurge direct.
        for stmt in node.children:
            self.visit(stmt)

    def visit_ASSIGNMENT(self, node: ASTNode) -> None:
        var_name = getattr(node.children[0], 'value', None)
        expr = self.visit_expression(node.children[1])
        self.emit(f"{var_name} = {expr};")

    def visit_READ(self, node: ASTNode) -> None:
        vars_str = " >> ".join([str(getattr(child, 'value', '')) for child in node.children])
        self.emit(f"cin >> {vars_str};")

    def visit_WRITE(self, node: ASTNode) -> None:
        parts: List[str] = []
        for child in node.children:
            parts.append(self.visit_expression(child))
        output_str = " << ".join(parts)
        self.emit(f"cout << {output_str};")

    def visit_IF(self, node: ASTNode) -> None:
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

    def visit_WHILE(self, node: ASTNode) -> None:
        cond = self.visit_expression(node.children[0])
        self.emit(f"while ({cond}) {{")
        self.indent_level += 1
        self.visit(node.children[1])
        self.indent_level -= 1
        self.emit("}")

    def visit_DO_WHILE(self, node: ASTNode) -> None:
        self.emit("do {")
        self.indent_level += 1
        self.visit(node.children[0])  # Body first
        self.indent_level -= 1
        cond = self.visit_expression(node.children[1])
        self.emit(f"}} while ({cond});")

    def visit_REPEAT_UNTIL(self, node: ASTNode) -> None:
        self.emit("do {")
        self.indent_level += 1
        self.visit(node.children[0])
        self.indent_level -= 1
        cond = self.visit_expression(node.children[1])
        # IMPORTANT: repeat...until(cond) este echivalent cu while(!cond)
        self.emit(f"}} while (!({cond}));")

    def visit_FOR(self, node: ASTNode) -> None:
        var = None
        if hasattr(node, 'metadata') and isinstance(node.metadata, dict):
            var = node.metadata.get('iterator')
        if var is None and hasattr(node, 'attrs') and isinstance(node.attrs, dict):
            var = node.attrs.get('iterator')
        start = self.visit_expression(node.children[0])
        stop = self.visit_expression(node.children[1])
        step_node = node.children[2]

        # Optimizare: dacă pasul e literal, putem genera cod mai curat
        step_val = 1
        if getattr(step_node, 'node_type', None) == ASTNodeType.LITERAL and (
                (hasattr(step_node, 'metadata') and step_node.metadata.get('inferred_type') == 'int') or
                (hasattr(step_node, 'attrs') and step_node.attrs.get('inferred_type') == 'int')
        ):
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
        if getattr(step_node, 'node_type', None) != ASTNodeType.LITERAL:
            cond_expr = f"({step_expr} >= 0 ? {var} <= {stop} : {var} >= {stop})"
        else:
            cond_expr = f"{var} {cond_op} {stop}"

        self.emit(f"for ({var} = {start}; {cond_expr}; {inc_op}) {{")
        self.indent_level += 1
        self.visit(node.children[3])
        self.indent_level -= 1
        self.emit("}")

    def visit_expression(self, node: ASTNode) -> str:
         """Metodă helper care returnează string-ul expresiei, nu emite linie nouă."""
         # Support both node_type and kind naming
         node_type = getattr(node, 'node_type', getattr(node, 'kind', None))
         if node_type == ASTNodeType.LITERAL:
             # prefer metadata then attrs
             inferred = None
             if hasattr(node, 'metadata') and isinstance(node.metadata, dict):
                 inferred = node.metadata.get('inferred_type')
             elif hasattr(node, 'attrs') and isinstance(node.attrs, dict):
                 inferred = node.attrs.get('inferred_type')

             val = getattr(node, 'value', None)
             if inferred == 'bool':
                 boolean_lut: Dict[str, str] = {
                     "adevarat": "true",
                     "fals": "false"
                 }
                 return f"{boolean_lut.get(val, 'false')}"
             elif inferred == 'string':
                 return f'"{val}"'
             # numeric or var: return as-is
             return str(val)

         elif node_type == ASTNodeType.BIN_OP:
             left = self.visit_expression(node.children[0])
             right = self.visit_expression(node.children[1])
             # operator stored in metadata or attrs
             op = None
             if hasattr(node, 'metadata') and isinstance(node.metadata, dict):
                 op = node.metadata.get('operator')
             if op is None and hasattr(node, 'attrs') and isinstance(node.attrs, dict):
                 op = node.attrs.get('operator')

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

         elif node_type == ASTNodeType.UNARY_OP:
             # operator in metadata/attrs
             op = None
             if hasattr(node, 'metadata') and isinstance(node.metadata, dict):
                 op = node.metadata.get('operator')
             if op is None and hasattr(node, 'attrs') and isinstance(node.attrs, dict):
                 op = node.attrs.get('operator')
             expr = self.visit_expression(node.children[0])
             if op == 'SQRT':
                 return f"sqrt({expr})"
             if op == 'FLOOR':
                 return f"(long long)({expr})"  # CAST la int
             if op == 'NOT':
                 return f"!({expr})"
             if op == 'MINUS':
                 return f"-({expr})"

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