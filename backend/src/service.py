from backend.src.pseudocode_to_cpp.compiler.ast_node import ASTNodeType, ASTNode
from backend.src.pseudocode_to_cpp.compiler.parser import Parser
from backend.src.pseudocode_to_cpp.compiler.lexer import lex
from backend.src.pseudocode_to_cpp.transpiler.cpp_transpiler import CppTranspiler


def pseudocode_to_cpp(pseudocode: str) -> str:
    """
    Converts pseudocode to C++ code.
"""

    tokens = list(lex(pseudocode))
    parser = Parser(tokens)
    ast = parser.parse_program()
    transpiler = CppTranspiler()
    return transpiler.transpile(ast)
