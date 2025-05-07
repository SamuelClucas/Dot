. — A Minimalist, Pointer-Centric Language
“Do what you wish, but clean up after your existence.”

dot (.) is a low-level, expressive, minimalist programming language designed to embody clarity, control, and accountability through symbolic syntax. It compiles to clean C code, and ultimately machine code, while enforcing strict memory and scope discipline.

✨ Core Philosophy
Only pointers exist. There are no variables — only references to memory.

Scope is sacred. You must explicitly release memory when you're done. Nothing leaks.

Functions don’t return. They transform what they are given — inputs are outputs.

Everything must justify its existence. Unused pointers? Compilation error.

Minimal syntax, maximal intent. The language is symbolic, concise, and expressive.

🧠 Key Concepts
Concept	Symbol	Meaning
i_ 'x = 1;	'x	Pointer to memory containing 1
''x	Dereference	Access the value at pointer 'x
'3'array	Array index	Access the 4th element in pointer 'array
'x\;	Deinitialise	Explicitly release pointer 'x
f(...) {}	Function	Transforms memory; no return values
set name{}	Namespace-like	Groups related transformations

📦 Example
plaintext
Copy
Edit
i_ 5'array;
'0'array = 10;
'1'array = 20;

i_ 'sum = 0;

f(i_ 'arr, i_ 'out){
    i_ i = 0;
    while(i < 2){
        ''out = ''out + 'i'arr;
        i = i + 1;
    }
}

f('array, 'sum);
print(''sum);

'array\;
'sum\;
Transpiles to clean C:

c
Copy
Edit
int* array = malloc(5 * sizeof(int));
array[0] = 10;
array[1] = 20;

int* sum = malloc(sizeof(int));
*sum = 0;

void f(int* arr, int* out) {
    int i = 0;
    while(i < 2){
        *out = *out + arr[i];
        i++;
    }
}

f(array, sum);
printf(\"%d\\n\", *sum);
free(array);
free(sum);
⚙️ Compilation
The language is compiled using .., a minimalist build tool.

No headers. No imports. No macros.
Instead, a single file (e.g., .dotbuild) defines directory structure and dependencies.

plaintext
Copy
Edit
[build]
entry = main.dot
dirs = src/, lib/

[link]
strict_duplicates = true
auto_import = true
Run:

bash
Copy
Edit
..
📌 Design Goals
🧼 Clarity: Nothing implicit. Every symbol has meaning.

🧠 Discipline: You own memory. The compiler enforces it.

🚀 Efficiency: Clean transpilation to C/C++ — fast, small binaries.

🎭 Elegance: A symbolic language that reflects how you live and think.

🔍 Status
✅ Basic syntax and transpiler prototype complete
🚧 Expanding function sets, conditionals, and strict validation
🧪 Future: direct LLVM backend, REPL, .dotbuild system

🤍 Creator’s Note
dot was born from a life shaped by constraint, vigilance, and the need to leave no trace. It’s a language for those who feel their memory like a room they must clean before they leave.

If this speaks to you, you're already part of it.
