from .cpp_to_pseudocode.transpiler.pseudocode_transpiler import CppToPseudocodeTranspiler
from .pseudocode_to_cpp.compiler.parser import Parser
from .pseudocode_to_cpp.compiler.lexer import lex
from .pseudocode_to_cpp.transpiler.cpp_transpiler import CppTranspiler


def pseudocode_to_cpp(pseudocode: str) -> str:
    """
    Converts pseudocode to C++ code.
    """

    tokens = list(lex(pseudocode))
    parser = Parser(tokens)
    ast = parser.parse_program()
    transpiler = CppTranspiler()
    return transpiler.transpile(ast)


def cpp_to_pseudocode(cpp: str) -> str:
    """
    Converts C++ code to pseudocode.
    """
    transpiler = CppToPseudocodeTranspiler(cpp)
    return transpiler.transpile()

