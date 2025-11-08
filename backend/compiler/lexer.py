import re

# Folosim un dicționar pentru tokeni. Ordinea este importantă!
# Cheile sunt numele tokenilor, valorile sunt expresiile regulate.
TOKENS = {
    # Execution flow
    'CAT_TIMP': r'\bcat timp\b',
    'EXECUTA': r'\bexecuta\b',
    'SFARSIT_CAT': r'\bsfarsit_cat_timp\b',

    'DACA': r'\bdaca\b',
    'ATUNCI': r'\batunci\b',
    'ALTFEL': r'\baltfel\b',
    'SFARSIT_DACA': r'\bsfarsit_daca\b',

    'PENTRU': r'\bpentru\b',
    'SFARSIT_PENTRU': r"\bsfarsit_pentru\b",

    'REPETA': r'\brepeta\b',
    'PANA_CAND': r'\bpana cand\b',

    # Command keywords
    'CITESTE': r'\bciteste\b',
    'SCRIE': r'\bscrie\b',
    'SQRT': r'\bsqrt\b',

    # True False
    'TRUE': r"\badevarat\b",
    'FALSE': r"\bfals\b",

    'NOT': r'\bnot\b',
    'AND': r'\bsi\b',
    'OR': r'\bsau\b',

    # Operators
    'ASSIGN': r'<-|:=',  # Atribuirea cerută
    'POW': r'\^',
    'NEQ': r'≠|!=',
    'LTE': r'≤|<=',
    'GTE': r'≥|>=',
    'LT': r'<',
    'GT': r'>',
    'EQ': r'=',
    'PLUS': r'\+',
    'MINUS': r'-',
    'MUL': r'\*',
    'DIV': r'/',  # Împărțire reală
    'MOD': r'%',  # Rest

    'LBRACKET': r'\[',  # Pentru partea întreagă [a/b]
    'RBRACKET': r'\]',

    'LPAREN': r'\(',
    'RPAREN': r'\)',

    'COMMA': r',',
    'NUMBER': r'\d+(\.\d+)?',
    'ID': r'[a-zA-Z_][a-zA-Z0-9_]*',
    'STRING': r"'.*?'|\".*?\"",
    'NEWLINE': r'\n',
    'SKIP': r'[ \t]+',  # Spații și tab-uri
    'MISMATCH': r'.',  # Orice alt caracter (eroare)
}


def lex(code):
    """
    Transformă codul sursă într-un flux de tokeni.
    """
    # Construim regex-ul master concatenând toate perechile cheie-valoare din dict
    tok_regex = '|'.join('(?P<%s>%s)' % (name, regex) for name, regex in TOKENS.items())

    line_num = 1
    line_start = 0

    # re.finditer găsește toate potrivirile secvențial
    for mo in re.finditer(tok_regex, code, re.IGNORECASE):
        kind = mo.lastgroup
        value = mo.group()
        column = mo.start() - line_start

        if kind == 'NEWLINE':
            line_start = mo.end()
            line_num += 1
            continue
        elif kind == 'SKIP':
            continue
        elif kind == 'MISMATCH':
            # Putem ridica eroare aici sau returna un token de eroare pentru a continua parsarea
            raise SyntaxError(f'Caracter neașteptat {value!r} la linia {line_num}, coloana {column}')

        # Yield un dicționar pentru fiecare token găsit
        yield {
            'type': kind,
            'value': value,
            'line': line_num,
            'col': column
        }

    # Yield ultimul caracter
    yield {
        'type': 'EOF',
        'value': '',
        'line': line_num,
        'col': column
    }


# --- TEST LEXER ---
if __name__ == '__main__':
    cod_test = """
    citeste n
    s <- 0
    cat timp n != 0 executa
        s <- s + n % 10
        n <- [n / 10]
    sfarsit_cat_timp
    scrie "Suma este: ", s
    """

    try:
        for token in lex(cod_test):
            print(token)
    except SyntaxError as e:
        print(e)