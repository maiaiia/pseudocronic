PSEUDOCODE_RULES = """
Regulile pseudocodului românesc (conform pbinfo.ro):

STRUCTURI DE CONTROL:
1. Structura alternativă:
    daca <conditie> atunci
        <instructiuni1>
    altfel
        <instructiuni2>
    sfarsit_daca

2. Structura repetitivă PENTRU:
   pentru <variabila> ← <expr_init>, <expr_final>, <pas> executa
        <instructiuni>
   sfarsit_pentru

3. Structura CÂT TIMP:
   cat timp <conditie> executa
         <instructiuni>
   sfarsit_cat_timp

4. Structura EXECUTĂ ... CÂT TIMP:
   executa
        <instructiuni>
   cat timp <conditie> (apoi sfarsit_executa)

5. Structura REPETĂ ... PÂNĂ CÂND:
   repeta
        <instructiuni>
   pana cand <conditie> (apoi sfarsit_repeta)

OPERATORI:
- Atribuire: ←
- Relational: =, ≠, <, ≤, >, ≥
- Aritmetici: +, -, *, /, %, [a/b] pentru partea întreagă
- Logici: NOT, ȘI, SAU

INSTRUCȚIUNI:
- Citire: citeste <variabile>
- Afișare: scrie <expresii>

IMPORTANTE:
- Fiecare structură se termină cu sfarsit_<nume_structura>, mai puțin structurile repetitive cu numar necunoscut de pasi 
cu condiție la final
- Numele variabilelor: litere, cifre, underscore, nu încep cu cifră
- Constantele șir: între apostrof ' sau ghilimele "

Pentru mai multe detalii referențiază următoarele site-uri:
https://www.pbinfo.ro/articole/23972/limbajul-pseudocod

"""


def get_correction_prompt(code: str, provide_explanation: bool) -> list:
    system_message = f"""Ești un expert în pseudocod românesc pentru bacalaureat.

{PSEUDOCODE_RULES}

Sarcina ta:
1. Analizează codul pseudocod furnizat
2. Identifică toate erorile conform regulilor de mai sus
3. Corectează codul
4. {'Explică fiecare corecție făcută' if provide_explanation else 'Nu include explicații'}

Returnează răspunsul în formatul JSON:
{{
    "corrected_code": "codul corect",
    "has_errors": true/false,
    "errors_found": ["eroare1", "eroare2"],
    "explanation": "explicație detaliată" sau null
}}
"""

    user_message = f"Corectează următorul pseudocod:\n\n{code}"

    return [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message}
    ]