import math
import json
from typing import Any, Dict, Optional, List, Callable
from dataclasses import dataclass, field
from io import StringIO


@dataclass
class ExecutionStep:
    """Represents one step in the execution trace"""
    step_number: int
    node_type: str
    line: int
    description: str
    variables_snapshot: Dict[str, Any] = field(default_factory=dict)
    current_value: Any = None
    node_details: Dict[str, Any] = field(default_factory=dict)
    output_so_far: str = ""  # NEW: Output accumulated up to this point


def _attribute(node: Any, key: str, default: Any = None) -> Any:
    """Read an attribute from the node, preferring the new `attrs` map but
    falling back to `metadata` for backwards compatibility.
    """
    if node is None:
        return default
    if hasattr(node, 'attrs') and isinstance(node.attrs, dict):
        return node.attrs.get(key, default)
    if hasattr(node, 'metadata') and isinstance(node.metadata, dict):
        return node.metadata.get(key, default)
    return getattr(node, key) if hasattr(node, key) else default


def _node_type_name(node: Any) -> str:
    if node is None:
        return 'NONE'
    if hasattr(node, 'node_type') and getattr(node.node_type, 'name', None):
        return node.node_type.name
    if hasattr(node, 'kind') and getattr(node.kind, 'name', None):
        return node.kind.name
    return node.__class__.__name__.upper()


class StepByStepInterpreter:
    def __init__(self, enable_debug: bool = True) -> None:
        """
        Args:
            enable_debug: If True, collect execution steps for debugging
        """
        self.globals: Dict[str, Any] = {}
        self.enable_debug = enable_debug
        self.execution_trace: List[ExecutionStep] = []
        self.step_counter = 0
        self.paused = False
        self.step_callback: Optional[Callable[[ExecutionStep], None]] = None

        # NEW: Output capture
        self.output_buffer = StringIO()
        self.output_history: List[str] = []  # List of all outputs in order

    def set_step_callback(self, callback: Callable[[ExecutionStep], None]) -> None:
        """Set a callback function that gets called after each step"""
        self.step_callback = callback

    def _record_step(self, node: Any, description: str, value: Any = None) -> None:
        """Record an execution step for debugging"""
        if not self.enable_debug:
            return

        self.step_counter += 1
        line = _attribute(node, 'line', 0)
        node_type = _node_type_name(node)

        # Create a snapshot of current variables
        variables_snapshot = self.globals.copy()

        # Extract relevant node details
        node_details = {}
        if hasattr(node, 'attrs'):
            node_details = node.attrs.copy() if isinstance(node.attrs, dict) else {}
        elif hasattr(node, 'metadata'):
            node_details = node.metadata.copy() if isinstance(node.metadata, dict) else {}

        # Capture current output state
        current_output = self.output_buffer.getvalue()

        step = ExecutionStep(
            step_number=self.step_counter,
            node_type=node_type,
            line=line,
            description=description,
            variables_snapshot=variables_snapshot,
            current_value=value,
            node_details=node_details,
            output_so_far=current_output
        )

        self.execution_trace.append(step)

        # Call callback if set (for real-time debugging)
        if self.step_callback:
            self.step_callback(step)

    def get_execution_trace(self) -> List[ExecutionStep]:
        """Get the full execution trace"""
        return self.execution_trace

    def get_output_history(self) -> List[str]:
        """Get all output messages in order"""
        return self.output_history.copy()

    def get_final_output(self) -> str:
        """Get the complete final output"""
        return self.output_buffer.getvalue()

    def print_execution_trace(self) -> None:
        """Print the execution trace in a readable format"""
        print("\n" + "=" * 80)
        print("URMĂRIRE EXECUȚIE PAS CU PAS")
        print("=" * 80 + "\n")

        for step in self.execution_trace:
            print(f"Pasul {step.step_number} | Linia {step.line} | {step.node_type}")
            print(f"  → {step.description}")
            if step.current_value is not None:
                print(f"  Valoare: {step.current_value}")
            if step.variables_snapshot:
                print(f"  Variabile: {step.variables_snapshot}")
            if step.output_so_far:
                print(f"  Output până acum: {repr(step.output_so_far)}")
            print()

    def export_trace_json(self) -> str:
        """Export execution trace as JSON"""
        trace_data = []
        for step in self.execution_trace:
            trace_data.append({
                'step': step.step_number,
                'line': step.line,
                'type': step.node_type,
                'description': step.description,
                'value': str(step.current_value) if step.current_value is not None else None,
                'variables': step.variables_snapshot,
                'output': step.output_so_far
            })
        return json.dumps(trace_data, indent=2, ensure_ascii=False)

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
        val = getattr(node, 'value', _attribute(node, 'value'))
        inferred = _attribute(node, 'inferred_type')

        if inferred == 'real':
            result = float(val)
            self._record_step(node, f"Evaluare literal real: {val}", result)
            return result
        if inferred == 'int':
            result = int(val)
            self._record_step(node, f"Evaluare literal întreg: {val}", result)
            return result
        if inferred == 'var':
            var_name = val
            if var_name in self.globals:
                result = self.globals[var_name]
                self._record_step(node, f"Citire variabilă '{var_name}'", result)
                return result
            line = _attribute(node, 'line', '?')
            raise NameError(f"Variabilă nedefinită '{var_name}' la linia {line}")

        self._record_step(node, f"Evaluare literal: {val}", val)
        return val

    def visit_BIN_OP(self, node: Any) -> Any:
        if not getattr(node, 'children', None) or len(node.children) < 2:
            raise ValueError('BIN_OP fără doi copii')

        op = _attribute(node, 'operator', getattr(node, 'op', None))
        if op is None:
            raise ValueError('Operator lipsă pentru BIN_OP')

        left = self.visit(node.children[0])
        right = self.visit(node.children[1])

        op_up = str(op).upper()
        result = None

        if op_up == 'OR':
            result = left or right
        elif op_up == 'AND':
            result = left and right
        elif op == '+':
            result = left + right
        elif op == '-':
            result = left - right
        elif op == '*':
            result = left * right
        elif op == '/':
            result = left / right
        elif op == '%':
            result = left % right
        elif op == '=':
            result = left == right
        elif op in ('!=', '≠'):
            result = left != right
        elif op == '<':
            result = left < right
        elif op == '>':
            result = left > right
        elif op in ('<=', '≤'):
            result = left <= right
        elif op in ('>=', '≥'):
            result = left >= right
        elif op == '^':
            result = left ** right
        else:
            raise Exception(f"Operator necunoscut: {op}")

        self._record_step(node, f"Operație binară: {left} {op} {right}", result)
        return result

    def visit_UNARY_OP(self, node: Any) -> Any:
        if not getattr(node, 'children', None) or len(node.children) < 1:
            raise ValueError('UNARY_OP fără operand')

        op = _attribute(node, 'operator', getattr(node, 'op', None))
        val = self.visit(node.children[0])

        result = None
        if op == 'SQRT':
            result = math.sqrt(val)
        elif op == 'FLOOR':
            result = math.floor(val)
        elif op == 'NOT':
            result = not val
        elif op == 'MINUS':
            result = -val
        else:
            raise Exception(f"Operator unar necunoscut: {op}")

        self._record_step(node, f"Operație unară: {op}({val})", result)
        return result

    def visit_PROGRAM(self, node: Any) -> None:
        self._record_step(node, "Începere program", None)
        for stmt in getattr(node, 'children', []):
            self.visit(stmt)
        self._record_step(node, "Terminare program", None)

    def visit_BLOCK(self, node: Any) -> None:
        self._record_step(node, "Intrare în bloc", None)
        for stmt in getattr(node, 'children', []):
            self.visit(stmt)
        self._record_step(node, "Ieșire din bloc", None)

    def visit_ASSIGNMENT(self, node: Any) -> None:
        if not getattr(node, 'children', None) or len(node.children) < 2:
            raise ValueError('ASSIGNMENT nod invalid')

        var_node = node.children[0]
        var_name = getattr(var_node, 'value', None) or _attribute(var_node, 'value')
        val = self.visit(node.children[1])

        if var_name is None:
            raise ValueError('Numele variabilei lipsă la ASSIGNMENT')

        self.globals[var_name] = val
        self._record_step(node, f"Atribuire: {var_name} ← {val}", val)

    def visit_IF(self, node: Any) -> None:
        cond = self.visit(node.children[0])
        self._record_step(node, f"Evaluare IF: condiție = {cond}", cond)

        if cond:
            self._record_step(node, "Execuție ramură THEN", None)
            self.visit(node.children[1])
        else:
            if len(node.children) > 2 and node.children[2]:
                self._record_step(node, "Execuție ramură ELSE", None)
                self.visit(node.children[2])
            else:
                self._record_step(node, "Salt peste IF (condiție falsă)", None)

    def visit_WHILE(self, node: Any) -> None:
        iteration = 0
        self._record_step(node, "Intrare în bucla WHILE", None)

        while True:
            cond = self.visit(node.children[0])
            iteration += 1
            self._record_step(node, f"WHILE iterația {iteration}: condiție = {cond}", cond)

            if not cond:
                break

            self.visit(node.children[1])

        self._record_step(node, f"Ieșire din WHILE după {iteration - 1} iterații", None)

    def visit_FOR(self, node: Any) -> None:
        var_name = _attribute(node, 'iterator')
        if var_name is None:
            raise ValueError('FOR fără iterator în metadata')

        start_val = self.visit(node.children[0])
        stop_val = self.visit(node.children[1])
        step_val = self.visit(node.children[2])
        body = node.children[3]

        self.globals[var_name] = start_val
        self._record_step(node, f"Intrare în FOR: {var_name} de la {start_val} la {stop_val}, pas {step_val}", None)

        iteration = 0
        while True:
            curr_val = self.globals[var_name]
            iteration += 1

            if step_val > 0 and curr_val > stop_val:
                break
            if step_val < 0 and curr_val < stop_val:
                break

            self._record_step(node, f"FOR iterația {iteration}: {var_name} = {curr_val}", curr_val)
            self.visit(body)
            self.globals[var_name] += step_val

        self._record_step(node, f"Ieșire din FOR după {iteration} iterații", None)

    def visit_REPEAT_UNTIL(self, node: Any) -> None:
        iteration = 0
        self._record_step(node, "Intrare în REPEAT-UNTIL", None)

        while True:
            iteration += 1
            self._record_step(node, f"REPEAT iterația {iteration}", None)
            self.visit(node.children[0])

            cond = self.visit(node.children[1])
            self._record_step(node, f"UNTIL: condiție = {cond}", cond)

            if cond:
                break

        self._record_step(node, f"Ieșire din REPEAT după {iteration} iterații", None)

    def visit_DO_WHILE(self, node: Any) -> None:
        iteration = 0
        self._record_step(node, "Intrare în DO-WHILE", None)

        while True:
            iteration += 1
            self._record_step(node, f"DO-WHILE iterația {iteration}", None)
            self.visit(node.children[0])

            cond = self.visit(node.children[1])
            self._record_step(node, f"WHILE: condiție = {cond}", cond)

            if not cond:
                break

        self._record_step(node, f"Ieșire din DO-WHILE după {iteration} iterații", None)

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
            self._record_step(node, f"Citire: {var_name} ← {val} (input)", val)

    def visit_WRITE(self, node: Any) -> None:
        output_parts = []
        for expr in getattr(node, 'children', []):
            val = self.visit(expr)
            if isinstance(val, str):
                val = val.replace('\\n', '\n')
            output_parts.append(str(val))

        output = "".join(output_parts)

        # Write to both console and buffer
        print(output)
        self.output_buffer.write(output + '\n')
        self.output_history.append(output)

        self._record_step(node, f"Scriere: {repr(output)}", output)

    def generic_visit(self, node: Any) -> None:
        name = _node_type_name(node)
        raise Exception(f'Nu există metodă visit_{name}')



if __name__ == "__main__":
    from backend.src.pseudocode_to_cpp.compiler.parser import Parser
    from backend.src.pseudocode_to_cpp.compiler.lexer import lex

    code_sample = """
    x <- 5
    y <- 10
    suma <- x + y
    scrie "Suma este: ", suma

    pentru i <- 1, 3 executa
        scrie "Iterația: ", i
    sfarsit_pentru
    """

    # Create interpreter with debugging enabled
    interpreter = StepByStepInterpreter(enable_debug=True)

    try:
        tokens = list(lex(code_sample))
        parser = Parser(tokens)
        ast = parser.parse_program()
    except (SyntaxError, ValueError) as e:
        print(f"Eroare de parsare: {e}")
        raise SystemExit(-1)

    try:
        print("--- Început Execuție ---\n")
        interpreter.visit(ast)
        print("\n--- Final Execuție ---")
        print("\n" + "=" * 80)
        print("MEMORIE FINALĂ:", interpreter.globals)
        print("=" * 80)
        print("\n" + "=" * 80)
        print("OUTPUT FINAL:")
        print("=" * 80)
        print(interpreter.get_final_output())

        # Print step-by-step trace
        interpreter.print_execution_trace()

        # Export as JSON
        print("\n" + "=" * 80)
        print("EXPORT JSON:")
        print("=" * 80)
        print(interpreter.export_trace_json())

    except Exception as e:
        print(f"Eroare la execuție: {e}")
        raise