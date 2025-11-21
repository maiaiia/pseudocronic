# PseudoCronic

Back in high school, we **hated** learning pseudocode. Program after program, each one with 2-3 nested loops and the same tired conditions over and over, and everything written on paper. Hours wasted tracking every variable through every iteration, only to find out your mistake was writing 2+2=5 during the 4th iteration of the second while loop because you were too tired from the manual labor. Meanwhile, you're not even learning the actual logic behind the algorithm - the tediousness makes you miss the point entirely.

Well, we can’t really change the whole Romanian educational system. But we can do a little something to try and make it better.

Which is why for the 2025 edition of SmartHack, a 24 hour hackathon that challenged us to find a way to improve an education-related issue, we decided to implement ✨PseudoCronic ✨

## What is it?
PseudoCronic is a tool that makes learning and working with pseudocode actually bearable. Whether you’re a bored student or a class teacher looking for better ways to explain algorithms, this is the tool for you.


## Features 
- **Translate Pseudocode to C++** - Stop manually converting things line by line
- **Step by Step Execution of Pseudocode** - See what your pseudocode actually does and compare that with your solutions
- **Image to Text** - Take a photo of handwritten pseudocode and we’ll parse it for you*
- **Fix Code Errors** - AI-powered error detection and fixes (but we’ll cover syntax-related errors only, so **you** actually have to put in the effort of making your code work as intended)*
- Generate Sample Problems - You’ll probably never run out of problems to do, but, you know, just in case!
- Join Room for Real-Time Collaboration - Work on problems with your classmates 


*API calls cost money, so the image extraction and error fixing features are rate-limited. Use them wisely! (think of it as encouraging you to learn rather than just spamming the “fix my code“ button)* 

## How we built it

### Pseudocode to cpp:
We decided to perform the code translation **algorithmically**, inspired by the way real-life compilers work.

- Parser + Lexer - convert pseudocode to AST tree
- Interpreter - Used to check the correctness of the code
- Transpiler - Transpile to C++

### Cpp to pseudocode:
We took advantage of how nice and well structured c++ is and only implemented a simple transpiler. Turns out going backwards is easier (but when you do it at 3am it actually isn’t)

AI powered features
- Extract text from a picture (tried to use an OCR but turns out out handwriting is too bad, so this one’s done by an LLM :( — we’re working on getting rid of the API calls in the future)
- Highlight syntax errors and fix them
-  Generate practice problems

## Tech Stack 
### Frontend 

### Backend 

### AI 

-----------
## Pseudocode Syntax

### Data Types
- bool 
- int
- float / double
- string
 
### Operations
#### Logical Operations

| Symbol | Operation        |
|:------:|------------------|
|  `=`   | equality         |
|  `!=`  | inequality       |
|  `<`   | less than        |
|  `<=`  | less or equal    |
|  `>`   | greater than     |
|  `>=`  | greater or equal |

#### Arithmetic Operations

|     Symbol     | Operation        |
|:--------------:|------------------|
|      `+`       | addition         |
|      `-`       | subtraction      |
|      `*`       | multiplication   |
|      `\`       | float division   |
| `[\]` or `DIV` | integer division |
| `%` or `MOD`   | modulo           |
|    `sqrt()`    | square root      |


### Loop 

#### pentru, executa 
(classic for loop)
```
 -pentru <variabila> <- <expresie initiala>, <expresie finala>, [pas] executa
|   <instructiuni>
 - stop pentru
```

#### cat timp, executa
(classic while loop)
```
 -cattimp <conditie> executa
|   <instructiuni>
 - stop cattimp
```

#### executa, cat timp

(do...while loop)
```
 -executa 
|   <instructiuni>
 - cattimp <conditie>
```

#### repeta, pana cand 

(repeat...until)
```
 - repeta
|   <instructiuni>
 - pana cand <conditie>
```

### Built-in Operations

#### Reading
`citeste <lista variabile>`

#### Printing 
`scrie <lista expresii>` 

#### Assignment
`<variabila> <- <expresie>`



