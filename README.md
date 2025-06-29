# `.`  
### A Minimalist, Pointer-Centric Language

> “Do what you wish, but clean up after your existence.”

**Dot** is a low-level, expressive, minimalist programming language designed to embody **clarity**, **control**, and **accountability** through symbolic syntax. It transpiles to clean C/C++ (and ultimately machine code) while enforcing strict memory and scope discipline.

---

## Ethos

- **Only pointers exist** — there are no variables, only references to memory.
- **Scope is sacred** — memory must be explicitly released. No garbage to cleanup.
- **Functions don’t return** — they transform memory. Inputs are outputs.
- **Unused pointers?** Compilation error. Everything must justify its existence.
- **Minimal syntax, maximal intent** — terse but expressive, highly symbolic.

---

## Key Concepts

| Dot Syntax       | Concept                                 | Meaning                                  |
|------------------|-----------------------------------------|------------------------------------------|
| `i_ 'x = 1;`     | Pointer declaration                     | `'x` points to memory holding `1`        |
| `x"`            | Dereference                      | Access value at pointer `'x`             |
| `array"3`       | Array access                            | Access 4th element in pointer `'array`   |
| `'x\`           | Explicit free                           | Release pointer `'x`                     |
| `f(@p) {}`       | Function declaration                    | Functions don’t return, only transform   |
| `set_type name {}` | Namespace-like structure               | Group related functions by type          |

---

## Example

```dot
i_5 'array; // array of 5 ints
array"0 = 10;
array"2 = 20;

i_ 'sum = 0;

f(i_ @arr, i_ @out){
    i_ i = 0,
    while(i < 2){
        out@ = out@ + arr@i;
        i = i + 1,
    }
}

f('array, 'sum);
sum" // minimalist print statement

'array\
'sum\
```

Transpiles to:
```c
int* array = malloc(5 * sizeof(int));
array[0] = 10;
array[1] = 20;

int* sum = malloc(sizeof(int));
*sum = 0;

void f(i_ @arr, i_ @out) {
    int i = 0;
    while(i < 2){
        out@ = out@ + arr@i;
        i++;
    }
}

f(array, sum);
printf("%d\n", *sum);
free(array);
free(sum);
```

## Compilation

Dot is compiled using .., a minimalist build tool.

No headers. No macros. No includes.

Project structure is declared using a .dotbuild file:

[build]
entry = main.dot
dirs = src/, lib/

[link]
strict_duplicates = true
auto_import = true

## Design Goals

- Clarity: Every symbol has explicit meaning.

- Discipline: You own memory. The compiler enforces it.

- Efficiency: Fast, lean, transpiled C/C++ code.

- Scope autonomy: You wield control. Scope doesn’t own you.

## Project Structure

<pre lang="md"><code>```bash . ├── archive/ # Older transpiler experiments │ ├── 01_transpiler_training_wheels.py # First transpiler MVP │ ├── dot_transpiler_cpp.py # Partial prototype with C++ syntax │ ├── dotc.py # Draft CLI entry point │ └── tokenizer.py # Legacy lexer with regex ├── dotLang.pdf # Design document: syntax, philosophy, examples ├── examples/ # Demonstrations and syntax showcases │ ├── hello_world.dot # Minimal example program │ ├── legacy.md # Notes from early iterations │ └── sample.rtf # Archived scratchpad / sketches ├── LICENSE ├── README.md # You're here └── src/ # Core compiler modules ├── dotc.py # [DOING] Main CLI compiler stub ├── emitter.py # [TODO] C/C++ code generation backend ├── ir.py # [TODO] Intermediate Representation layer ├── lexer.py # Token class system-based lexer └── parser.py # [TODO] AST parser ``` </code></pre>

## Status

 Token-based lexer implemented (src/lexer.py)

 Parser under construction (src/parser.py)

 IR and emitter: future work

 .dotbuild support planned

 REPL & interactive debugger (future)

 LLVM backend (experimental target)


