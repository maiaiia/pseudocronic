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
- Atribuire: <-
- Relational: =, ≠, <, ≤, >, ≥
- Aritmetici: +, -, *, /, %, [a/b] pentru partea întreagă
- Logici: not, si, sau

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
CAND SCRII COD, SA NU FOLOSESTI DIACRITICILE

"""


def get_correction_prompt(code: str) -> list:
    system_message = f"""Ești un expert în pseudocod românesc pentru bacalaureat.

{PSEUDOCODE_RULES}

Sarcina ta:
1. Analizează codul pseudocod furnizat
2. Identifică toate erorile conform regulilor de mai sus
3. Corectează codul
4. {'Explică fiecare corecție făcută' }

Returnează răspunsul în formatul JSON:
{{
    "corrected_code": "codul corect",
    "has_errors": true/false,
    "errors_found": ["eroare1", "eroare2"],
    "explanation": "explicație detaliată" sau null
}}

EXEMPLE (input, output):

citeste n
s <- 0
pentru i <- 1, n executa
	s <- s + i
sfarsit_pentru
scrie [s/n]

{{
	"corrected_code": ""
	"has_errors": false,
	"errors_found": []
	"explanation": "Codul dat este corect. Variabila n se citeste, iar apoi, in functie de aceasta, se va calcula suma primelor n numere intregi. Pe ecran va fi afisata valoarea truncata a mediei aritmetice"
}}

---

citeste n
s <- 0
pentru i <- 1, n executa
	s <- s + i
scrie [s/n]

{{
	"corrected_code": "citeste n\ns <- 0\npentru i <- 1, n executa\n\ts <- s + i\nsfarsit_pentru\nscrie [s/n]"
	"has_errors": true,
	"errors_found": ["Structura de control "pentru" nu a fost inchisa"]
	"explanation": "Codul dat nu este corect din punct de vedere sintactic. Lipseste incheierea structurii de control 'pentru'"
}}

---

a <- 5
b <- 10
s <- a + b
scrie s


{{
    "corrected_code": "",
    "has_errors": false,
    "errors_found": [],
    "explanation": "Cod corect. Realizează o simplă adunare și afișează rezultatul."
}}


-----

citeste x
daca x % 2 = 0 atunci
scrie "Par"
sfarsit_daca

{
    "corrected_code": "",
    "has_errors": false,
    "errors_found": [],
    "explanation": "Cod corect. Verifică dacă un număr este par și afișează un mesaj corespunzător."
}

-----

citeste n
i <- 1
cat timp i <= n executa
scrie i
i <- i + 1

{
    "corrected_code": "citeste n\ni <- 1\ncat timp i <= n executa\n\tscrie i\n\ti <- i + 1\nsfarsit_cat_timp",
    "has_errors": true,
    "errors_found": ["Structura 'cat timp' nu a fost inchisa cu 'sfarsit_cat_timp'"],
    "explanation": "Lipsește eticheta de închidere pentru bucla `cat timp`."
}


-----

citeste n
s <- 0
pentru i <- 1, n executa
citeste x
daca x \> 0 atunci
s <- s + x
altfel
s <- s - x
sfarsit_daca
sfarsit_pentru
scrie s


{
    "corrected_code": "",
    "has_errors": false,
    "errors_found": [],
    "explanation": "Cod corect. Calculează o sumă condiționată de semnul numerelor citite."
}


-----

citeste n
daca n < 0 atunci
scrie "Negativ"
altfel daca n = 0 atunci
scrie "Zero"
altfel
scrie "Pozitiv"
sfarsit_daca


{
    "corrected_code": "citeste n\ndaca n < 0 atunci\n\tscrie \"Negativ\"\naltfel\n\tdaca n = 0 atunci\n\t\tscrie \"Zero\"\n\taltfel\n\t\tscrie \"Pozitiv\"\n\tsfarsit_daca\nsfarsit_daca",
    "has_errors": true,
    "errors_found": ["Structura 'daca' imbricata incorect sau lipsesc 'sfarsit_daca' multipli"],
    "explanation": "În pseudocodul standard, `altfel daca` nu este o construcție atomică. Necesită imbricare explicită și închideri multiple cu `sfarsit_daca`."
}


-----

citeste n
prim <- 1
daca n < 2 atunci
prim <- 0
altfel
pentru i <- 2, [n/2] executa
daca n % i = 0 atunci
prim <- 0
sfarsit_daca
sfarsit_pentru
sfarsit_daca
daca prim = 1 atunci
scrie "ESTE PRIM"
altfel
scrie "NU ESTE PRIM"
sfarsit_daca


{
    "corrected_code": "",
    "has_errors": false,
    "errors_found": [],
    "explanation": "Cod corect. Verifică primalitatea unui număr folosind un algoritm clasic."
}


-----

citeste a, b
cat timp a \!= b executa
daca a \> b atunci
a <- a - b
altfel
b <- b - a
sfarsit_daca
sfarsit_cat_timp
scrie a


{
    "corrected_code": "",
    "has_errors": false,
    "errors_found": [],
    "explanation": "Cod corect. Implementează algoritmul lui Euclid prin scăderi repetate pentru CMMDC."
}


-----

k <- 0
pentru i <- 1, 10 executa
pentru j <- 1, 10 executa
k <- k + 1
sfarsit_pentru


{
    "corrected_code": "k <- 0\npentru i <- 1, 10 executa\n\tpentru j <- 1, 10 executa\n\t\tk <- k + 1\n\tsfarsit_pentru\nsfarsit_pentru",
    "has_errors": true,
    "errors_found": ["Lipseste un 'sfarsit_pentru' pentru bucla exterioara"],
    "explanation": "Buclele imbricate necesită fiecare propria etichetă de închidere."
}

other examples:

**Exemplu 1 (Simplu, Corect):**
`Input:`

```pseudocod
citeste n
daca n % 2 = 0 atunci
    scrie "Numar par"
altfel
    scrie "Numar impar"
sfarsit_daca
```

`Output:`

```json
{
    "corrected_code": "",
    "has_errors": false,
    "errors_found": [],
    "explanation": "Codul este corect sintactic. Verifică paritatea unui număr citit."
}
```

**Exemplu 2 (Eroare Sintaxă - Lipsă `executa`):**
`Input:`

```pseudocod
citeste n
s <- 0
pentru i <- 1, n
    s <- s + i
sfarsit_pentru
scrie s
```

`Output:`

```json
{
    "corrected_code": "citeste n\ns <- 0\npentru i <- 1, n executa\n    s <- s + i\nsfarsit_pentru\nscrie s",
    "has_errors": true,
    "errors_found": ["Lipseste cuvantul cheie 'executa' in structura 'pentru'"],
    "explanation": "Structura `pentru` necesită specificarea explicită a cuvântului cheie `executa` înainte de blocul de instrucțiuni."
}
```

**Exemplu 3 (Complex, Corect - Imbricare):**
`Input:`

```pseudocod
citeste n
m <- n
ogl <- 0
cat timp m > 0 executa
    cifra <- m % 10
    ogl <- ogl * 10 + cifra
    m <- [m / 10]
sfarsit_cat_timp
daca ogl = n atunci
    scrie "Palindrom"
altfel
    scrie "Nu e palindrom"
sfarsit_daca
```

`Output:`

```json
{
    "corrected_code": "",
    "has_errors": false,
    "errors_found": [],
    "explanation": "Cod corect. Calculează oglinditul unui număr folosind o buclă `cat timp` și verifică dacă este palindrom folosind o structură `daca`."
}
```

**Exemplu 4 (Eroare Sintaxă - Structură neînchisă):**
`Input:`

```pseudocod
citeste x
cat timp x > 5 executa
    x <- x - 1
    daca x = 7 atunci
        scrie "Sapte"
sfarsit_cat_timp
```

`Output:`

```json
{
    "corrected_code": "citeste x\ncat timp x > 5 executa\n    x <- x - 1\n    daca x = 7 atunci\n        scrie \"Sapte\"\n    sfarsit_daca\nsfarsit_cat_timp",
    "has_errors": true,
    "errors_found": ["Structura 'daca' din interiorul buclei nu este inchisa cu 'sfarsit_daca'"],
    "explanation": "Orice structură `daca` trebuie închisă explicit. În acest caz, `sfarsit_cat_timp` apare înainte ca `daca` să fie închis."
}
```

**Exemplu 5 (Eroare Semantică/Sintaxă - `repeta` cu închidere greșită):**
`Input:`

```pseudocod
repeta
    i <- i + 1
    scrie i
sfarsit_repeta
```

`Output:`

```json
{
    "corrected_code": "repeta\n    i <- i + 1\n    scrie i\npana cand i >= 10",
    "has_errors": true,
    "errors_found": ["Structura 'repeta' se incheie cu 'pana cand <conditie>', nu cu 'sfarsit_repeta'"],
    "explanation": "Structurile repetitive cu test final nu folosesc etichete de tip `sfarsit_...`, ci se termină direct cu condiția (`pana cand` sau `cat timp`)."
}
"""

    user_message = f"Corectează următorul pseudocod:\n\n{code}"

    return [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message}
    ]