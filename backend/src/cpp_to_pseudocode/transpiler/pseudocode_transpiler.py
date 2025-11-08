import sys
import re

class CppToPseudocodeTranspiler:
    def __init__(self, cpp_code):
        self.cpp_code = cpp_code
        self.lines = cpp_code.split('\n')
        self.output = []
        self.indent_level = 0
        self.in_main = False
        self.brace_stack = []
        self.in_do_while = False

    def transpile(self):
        """Main transpilation function"""
        for line in self.lines:
            line = line.strip()

            # Skip empty lines, includes, using namespace
            if not line or line.startswith('#') or 'using namespace' in line:
                continue

            # Skip comments
            if line.startswith('//'):
                continue

            # Detect main function
            if 'int main' in line or 'void main' in line:
                self.in_main = True
                continue

            # Skip return 0
            if line.startswith('return'):
                continue

            # Handle closing brace with potential while (for do-while)
            if '}' in line and 'while' in line:
                # This is the end of do-while: } while (condition);
                self.handle_do_while_end(line)
                continue

            # Handle opening brace
            if line == '{':
                self.brace_stack.append('block')
                continue

            # Handle closing brace
            if line == '}':
                if self.brace_stack:
                    block_type = self.brace_stack.pop()
                    if block_type == 'for':
                        self.indent_level -= 1
                        self.add_line('sfarsit_pentru')
                    elif block_type == 'while':
                        self.indent_level -= 1
                        self.add_line('sfarsit_cat_timp')
                    elif block_type == 'if':
                        self.indent_level -= 1
                        self.add_line('sfarsit_daca')
                    elif block_type == 'do':
                        # Don't close here, wait for while
                        self.in_do_while = True
                continue

            # If not in main yet, check for global variables
            if not self.in_main:
                self.handle_global_declaration(line)
                continue

            # In main: skip variable declarations without initialization
            if self.is_declaration_only(line):
                continue

            # Process the line
            self.process_line(line)

        return '\n'.join(self.output)

    def add_line(self, text):
        """Add line with proper indentation"""
        self.output.append('    ' * self.indent_level + text)

    def handle_global_declaration(self, line):
        """Handle global variable declarations"""
        # Match: type varname = value;
        match = re.match(r'(int|double|float|bool|string)\s+(\w+)\s*=\s*(.+?);', line)
        if match:
            var_type, var_name, value = match.groups()
            value = self.translate_value(value)
            self.add_line(f'{var_name} <- {value}')
            return

        # Match: type varname; (no initialization)
        match = re.match(r'(int|double|float|bool|string)\s+(\w+)\s*;', line)
        if match:
            var_type, var_name = match.groups()
            default_val = self.get_default_value(var_type)
            self.add_line(f'{var_name} <- {default_val}')

    def is_declaration_only(self, line):
        """Check if line is just a variable declaration without initialization"""
        # Match: type var1, var2, var3;
        if re.match(r'(int|double|float|bool|string|char)\s+\w+(\s*,\s*\w+)*\s*;', line):
            return True
        return False

    def get_default_value(self, var_type):
        """Get default value for a type"""
        defaults = {
            'int': '0',
            'double': '0',
            'float': '0',
            'bool': 'fals',
            'string': '""',
        }
        return defaults.get(var_type, '0')

    def process_line(self, line):
        """Process a single line of C++ code"""
        # Handle for loop
        if line.startswith('for'):
            self.handle_for_loop(line)
            return

        # Handle while loop (but not if we just closed a do-while)
        if line.startswith('while') and not self.in_do_while:
            self.handle_while_loop(line)
            return

        # Handle do-while
        if line.startswith('do'):
            self.handle_do_while(line)
            return

        # Handle if statement
        if line.startswith('if'):
            self.handle_if_statement(line)
            return

        # Handle else
        if line.startswith('else'):
            self.indent_level -= 1
            self.add_line('altfel')
            self.indent_level += 1
            self.brace_stack.append('if')
            return

        # Handle cin
        if 'cin' in line:
            self.handle_cin(line)
            return

        # Handle cout
        if 'cout' in line:
            self.handle_cout(line)
            return

        # Handle assignment or declaration with initialization
        if '=' in line and not any(op in line for op in ['==', '!=', '<=', '>=']):
            self.handle_assignment(line)
            return

        # Handle increment/decrement
        if '++' in line or '--' in line:
            self.handle_increment_decrement(line)
            return

    def handle_for_loop(self, line):
        """Handle for loop: for (i = 1; i <= n; i++)"""
        # Extract parts: for (init; condition; increment)
        match = re.search(r'for\s*\(\s*(.+?)\s*;\s*(.+?)\s*;\s*(.+?)\s*\)', line)
        if not match:
            return

        init, condition, increment = match.groups()

        # Parse init: i = 1 or int i = 1
        init = re.sub(r'(int|double|float)\s+', '', init)
        var_match = re.search(r'(\w+)\s*=\s*(.+)', init)
        if not var_match:
            return
        var_name, start_val = var_match.groups()
        start_val = self.translate_expression(start_val)

        # Parse condition: i <= n or i < n
        cond_match = re.search(r'(\w+)\s*([<>=!]+)\s*(.+)', condition)
        if not cond_match:
            return
        _, op, end_val = cond_match.groups()
        end_val = self.translate_expression(end_val)

        # Parse increment: i++ or i += 1
        step = '1'
        if '--' in increment:
            step = '-1'
        elif '+=' in increment:
            step_match = re.search(r'\+=\s*(.+)', increment)
            if step_match:
                step = self.translate_expression(step_match.group(1))

        # Generate pseudocode
        if step == '1':
            self.add_line(f'pentru {var_name} <- {start_val}, {end_val} executa')
        else:
            self.add_line(f'pentru {var_name} <- {start_val}, {end_val}, {step} executa')

        self.indent_level += 1
        self.brace_stack.append('for')

    def handle_while_loop(self, line):
        """Handle while loop"""
        # Extract condition: while (condition)
        match = re.search(r'while\s*\((.+?)\)', line)
        if not match:
            return

        condition = match.group(1)
        condition = self.translate_expression(condition)

        self.add_line(f'cat timp {condition} executa')
        self.indent_level += 1
        self.brace_stack.append('while')

    def handle_do_while(self, line):
        """Handle do-while loop"""
        self.add_line('executa')
        self.indent_level += 1
        self.brace_stack.append('do')

    def handle_do_while_end(self, line):
        """Handle } while (condition); for do-while"""
        # Extract condition from } while (condition);
        match = re.search(r'while\s*\((.+?)\)', line)
        if match:
            condition = match.group(1)
            condition = self.translate_expression(condition)

            self.indent_level -= 1
            self.add_line(f'cat timp {condition}')
            self.in_do_while = False

    def handle_if_statement(self, line):
        """Handle if statement"""
        # Extract condition: if (condition)
        match = re.search(r'if\s*\((.+?)\)', line)
        if not match:
            return

        condition = match.group(1)
        condition = self.translate_expression(condition)

        self.add_line(f'daca {condition} atunci')
        self.indent_level += 1
        self.brace_stack.append('if')

    def handle_cin(self, line):
        """Handle cin >> x >> y;"""
        # Extract variables after >>
        parts = re.split(r'>>', line)
        variables = []
        for part in parts[1:]:  # Skip 'cin'
            var = re.search(r'(\w+)', part)
            if var:
                variables.append(var.group(1))

        if variables:
            self.add_line(f"citeste {', '.join(variables)}")

    def handle_cout(self, line):
        """Handle cout << x << "text" << endl;"""
        # Split by <<
        parts = re.split(r'<<', line)
        expressions = []

        for part in parts[1:]:  # Skip 'cout'
            part = part.strip()

            # Skip endl
            if 'endl' in part:
                continue  # Don't add newline

            # Remove semicolon
            part = part.rstrip(';').strip()

            if not part:
                continue

            # Translate the expression
            expr = self.translate_expression(part)
            expressions.append(expr)

        if expressions:
            self.add_line(f"scrie {', '.join(expressions)}")

    def handle_assignment(self, line):
        """Handle variable assignment"""
        line = line.rstrip(';').strip()

        # Remove type declaration if present
        line = re.sub(r'^(int|double|float|bool|string|char)\s+', '', line)

        # Split on first =
        if '=' not in line:
            return

        parts = line.split('=', 1)
        var_name = parts[0].strip()
        value = parts[1].strip()

        # Translate the value
        value = self.translate_expression(value)

        self.add_line(f'{var_name} <- {value}')

    def handle_increment_decrement(self, line):
        """Handle i++ or i--"""
        line = line.rstrip(';').strip()

        if '++' in line:
            var = line.replace('++', '').strip()
            self.add_line(f'{var} <- {var} + 1')
        elif '--' in line:
            var = line.replace('--', '').strip()
            self.add_line(f'{var} <- {var} - 1')

    def clean_parentheses(self, expr):
        """Remove unnecessary outer parentheses from expressions"""
        expr = expr.strip()

        # Remove multiple layers of outer parentheses
        while expr.startswith('((') and expr.endswith('))'):
            # Check if these are truly outer parentheses
            depth = 0
            can_remove = True
            for i, char in enumerate(expr[1:-1], 1):
                if char == '(':
                    depth += 1
                elif char == ')':
                    depth -= 1
                    if depth < 0 and i < len(expr) - 1:
                        can_remove = False
                        break

            if can_remove and depth == 0:
                expr = expr[1:-1].strip()
            else:
                break

        # Remove single outer parentheses if they're not needed
        if expr.startswith('(') and expr.endswith(')'):
            depth = 0
            can_remove = True
            for i, char in enumerate(expr[1:-1], 1):
                if char == '(':
                    depth += 1
                elif char == ')':
                    depth -= 1
                    if depth < 0:
                        can_remove = False
                        break

            if can_remove and depth == 0:
                expr = expr[1:-1].strip()

        return expr

    def translate_expression(self, expr):
        """Translate a C++ expression to pseudocode"""
        expr = expr.strip()

        # Handle type casts: (double)x / y becomes x / y
        expr = re.sub(r'\(\s*(int|double|float)\s*\)', '', expr)

        # Clean unnecessary parentheses
        expr = self.clean_parentheses(expr)

        # Handle integer division: x / y becomes [x / y] if no cast present
        # Check if this is integer division (no decimals involved)
        if '/' in expr:
            # Check if we need integer division brackets
            # Don't add if already has brackets or if it's a simple division
            if not expr.startswith('[') and '.' not in expr:
                # Find division operations and wrap them
                # Simple heuristic: if it's a standalone division, wrap it
                if expr.count('/') == 1 and not any(func in expr for func in ['sqrt', 'pow']):
                    parts = expr.split('/')
                    if len(parts) == 2:
                        left = parts[0].strip()
                        right = parts[1].strip()
                        # Only wrap if not already in parentheses
                        if not (left.startswith('(') or right.endswith(')')):
                            expr = f'[{left} / {right}]'

        # Translate boolean values
        expr = re.sub(r'\btrue\b', 'adevarat', expr)
        expr = re.sub(r'\bfalse\b', 'fals', expr)

        # Translate operators
        expr = expr.replace('==', '=')
        expr = expr.replace('!=', '=/=')
        expr = expr.replace('&&', ' si ')
        expr = expr.replace('||', ' sau ')

        # Handle function calls like sqrt, pow
        expr = re.sub(r'\bpow\s*\(\s*(.+?)\s*,\s*(.+?)\s*\)', r'\1 ^ \2', expr)

        return expr

    def translate_value(self, value):
        """Translate a value"""
        value = value.strip()
        value = re.sub(r'\btrue\b', 'adevarat', value)
        value = re.sub(r'\bfalse\b', 'fals', value)
        return value

def main():


    cpp_code = """
#include <iostream>
#include <cmath>

using namespace std;

int main() {
    double a, s;
    int b, d, e, f;

    if (((1 != 1) && true)) {
        cout << "B";
    }
    do {
        a = sqrt(pow(2, 2));
    } while (((a == 6) && (a == 3)));
    a = 10;
    b = 20;
    cin >> d >> e >> f;
    while ((a == 3)) {
        s = (a + (b / 3));
    }
    return 0;
}
        """

    try:
        transpiler = CppToPseudocodeTranspiler(cpp_code)
        pseudocode = transpiler.transpile()

        print(pseudocode)

    except Exception as e:
        print(f"\n Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()