import re
from dataclasses import dataclass
from typing import Any, Dict, Generator, List, Tuple

# Use an explicit ordered list of token name / regex pairs. Order matters: longer/more specific
# tokens should appear before more general ones.
TOKEN_SPECS: List[Tuple[str, str]] = [
    # Execution flow
    ("CAT_TIMP", r"\bcat timp\b"),
    ("EXECUTA", r"\bexecuta\b"),
    ("SFARSIT_CAT", r"\bsfarsit_cat_timp\b"),

    ("DACA", r"\bdaca\b"),
    ("ATUNCI", r"\batunci\b"),
    ("ALTFEL", r"\baltfel\b"),
    ("SFARSIT_DACA", r"\bsfarsit_daca\b"),

    ("PENTRU", r"\bpentru\b"),
    ("SFARSIT_PENTRU", r"\bsfarsit_pentru\b"),

    ("REPETA", r"\brepeta\b"),
    ("PANA_CAND", r"\bpana cand\b"),

    # Command keywords
    ("CITESTE", r"\bciteste\b"),
    ("SCRIE", r"\bscrie\b"),
    ("SQRT", r"\bsqrt\b"),

    # True / False
    ("TRUE", r"\badevarat\b"),
    ("FALSE", r"\bfals\b"),

    ("NOT", r"\bnot\b"),
    ("AND", r"\bsi\b"),
    ("OR", r"\bsau\b"),

    # Operators (order matters: multi-char first)
    ("ASSIGN", r"<-|:="),
    ("NEQ", r"≠|!="),
    ("LTE", r"≤|<="),
    ("GTE", r"≥|>="),
    ("POW", r"\^"),
    ("LT", r"<"),
    ("GT", r">"),
    ("EQ", r"="),
    ("PLUS", r"\+"),
    ("MINUS", r"-"),
    ("MUL", r"\*"),
    ("DIV", r"/"),
    ("MOD", r"%"),

    ("LBRACKET", r"\["),
    ("RBRACKET", r"\]"),

    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),

    ("COMMA", r","),
    # Numbers: integer or decimal
    ("NUMBER", r"\d+(?:\.\d+)?"),
    # Identifiers
    ("ID", r"[a-zA-Z_][a-zA-Z0-9_]*"),
    # Strings: support escaped quotes inside
    ("STRING", r"'(?:\\.|[^\\'])*'|\"(?:\\.|[^\\\"])*\""),
    ("NEWLINE", r"\n"),
    ("SKIP", r"[ \t]+"),
    ("MISMATCH", r"."),
]

# Precompile the master regex once at import time for performance
_MASTER_PATTERN = re.compile(
    "|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPECS),
    flags=re.IGNORECASE | re.UNICODE,
)


@dataclass
class Token:
    """Simple token representation returned by the lexer."""

    token_type: str
    lexeme: str
    line: int
    col: int

    def to_dict(self) -> Dict[str, Any]:
        return {"type": self.token_type, "value": self.lexeme, "line": self.line, "col": self.col}


def lex(source: str) -> Generator[Dict[str, Any], None, None]:
    """Transformă codul sursă într-un flux de tokeni (yield dicts for compatibility).

    Yields dictionaries with keys: type, value, line, col
    """
    line_number: int = 1
    line_start_idx: int = 0

    last_col: int = 0

    for match in _MASTER_PATTERN.finditer(source):
        token_type = match.lastgroup
        lexeme = match.group()
        col_offset = match.start() - line_start_idx

        # Update for bookkeeping
        if token_type == "NEWLINE":
            line_start_idx = match.end()
            line_number += 1
            last_col = 0
            continue
        if token_type == "SKIP":
            # spaces and tabs
            continue
        if token_type == "MISMATCH":
            raise SyntaxError(
                f"Caracter neașteptat {lexeme!r} la linia {line_number}, coloana {col_offset}"
            )

        last_col = col_offset

        tok = Token(token_type=token_type, lexeme=lexeme, line=line_number, col=col_offset)
        yield tok.to_dict()

    # Emit EOF token. Use last_col (0 if no tokens were emitted)
    yield Token(token_type="EOF", lexeme="", line=line_number, col=last_col).to_dict()


tokenize = lex

# --- TEST LEXER ---
if __name__ == "__main__":
    sample_code = """
    citeste n
    s <- 0
    cat timp n != 0 executa
        s <- s + n % 10
        n <- [n / 10]
    sfarsit_cat_timp
    scrie "Suma este: ", s
    """

    try:
        for t in lex(sample_code):
            print(t)
    except SyntaxError as err:
        print(err)
