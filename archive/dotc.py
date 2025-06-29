# dotc.py — Dot Language Compiler (Tokenizer → AST → C++ Emitter)

import re

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value
    def __repr__(self):
        return f"Token({self.type}, {self.value})"

rules = [
    ('TYPE',     r'\$_|i~|i_\d*|f_|s_|c_|sh_|l_|ll_'),
    ('KEYWORD',  r'\b(set|struct|if|elif|else|while|when|except)\b'),
    ('NUMBER',   r'\d+(\.\d+)?'),
    ('IDENT',    r'[a-zA-Z_]\w*'),
    ('GLYPH',    r'[\"\'@\\\$\.\{\}\(\)]'),
    ('COMPARE',  r'==|!=|<=|>=|<|>'),
    ('ASSIGN',   r'='),
    ('END',      r';|:|,'),
    ('SKIP',     r'\s+'),
]

def tokenize(code):
    tokens = []
    pattern = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in rules)
    regex = re.compile(pattern)
    for match in regex.finditer(code):
        kind = match.lastgroup
        value = match.group()
        if kind != 'SKIP':
            tokens.append(Token(kind, value))
    return tokens

# Parser stub with AST support
class Node: pass
class Assignment(Node):
    def __init__(self, target, value): self.target, self.value = target, value
class Declaration(Node):
    def __init__(self, dtype, name): self.dtype, self.name = dtype, name
class PrintStmt(Node):
    def __init__(self, parts): self.parts = parts
class FunctionCall(Node):
    def __init__(self, target, args): self.target, self.args = target, args
class StructInstance(Node):
    def __init__(self, struct_type, name, values): self.struct_type, self.name, self.values = struct_type, name, values
class ControlFlow(Node):
    def __init__(self, kind, condition, body): self.kind, self.condition, self.body = kind, condition, body
class StructDef(Node):
    def __init__(self, name, fields): self.name, self.fields = name, fields
class SetFunction(Node):
    def __init__(self, name, params, body): self.name, self.params, self.body = name, params, body
class SetGroup(Node):
    def __init__(self, name, functions): self.name, self.functions = name, functions

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def advance(self):
        tok = self.peek()
        self.pos += 1
        return tok

    def parse(self):
        return []  # Minimal stub for now

def parse(tokens):
    parser = Parser(tokens)
    return type('AST', (), {'body': parser.parse()})()

# === Expression Rewriter ===
def rewrite_expr(expr, pseudo_vars=None):
    if pseudo_vars is None:
        pseudo_vars = set()

    tokens = re.findall(r'\w+@\([^)]*\)|\w+@\w+|\w+@|\w+"?\w*|\^|\*|/|\+|\-|\(|\)', expr)

    def to_cpp(token):
        if '@' in token:
            if token.endswith('@'):
                return token[:-1]
            base, idx = token.split('@', 1)
            if idx.startswith('(') and idx.endswith(')'):
                return f"{base}[{idx[1:-1]}]"
            return f"{base}[{idx}]"
        if '"' in token:
            var, index = token.split('"')
            if var in pseudo_vars:
                raise Exception(f"Illegal: pseudo '{var}' cannot be dereferenced with \". Use {var}@ instead.")
            return f"{var}[{index}]"
        return token

    precedence = {'^': 3, '*': 2, '/': 2, '+': 1, '-': 1}

    def parse_expression(tokens):
        def parse_primary(i):
            token = tokens[i]
            if token == '(': expr, i = parse_subexpr(i + 1); return f"({expr})", i + 1
            return to_cpp(token), i + 1

        def parse_subexpr(i, min_prec=0):
            lhs, i = parse_primary(i)
            while i < len(tokens):
                op = tokens[i]
                if op not in precedence or precedence[op] < min_prec:
                    break
                prec = precedence[op] + 1
                rhs, i = parse_subexpr(i + 1, prec)
                lhs = f"pow({lhs}, {rhs})" if op == '^' else f"{lhs} {op} {rhs}"
            return lhs, i

        result, _ = parse_subexpr(0)
        return result

    return parse_expression(tokens)[0]

# === Remaining compiler logic already defined in ast.body walker ===
# (emit_cpp, dot_type_to_cpp, etc. as already in the file)


def emit_cpp(ast):
    global array_sizes
    array_sizes = {}  # Track declared arrays and their sizes
    lines = ["#include <iostream>", "#include <cmath>", "using namespace std;"]
    main_lines = []

    for node in ast.body:
        if isinstance(node, Declaration):
            if node.dtype.startswith('i_') and node.dtype[2:].isdigit():
                size = int(node.dtype[2:])
                array_sizes[node.name] = size
                main_lines.append(f"    int {node.name}[{size}];")
            elif node.dtype == 'i~':
                main_lines.append(f"    int* {node.name} = new int;")
            else:
                main_lines.append(f"    {dot_type_to_cpp(node.dtype)} {node.name} = {node.value};")

        elif isinstance(node, Dealloc):
            if node.var.startswith('~'):
                main_lines.append(f"    delete {node.var[1:]};")
            else:
                main_lines.append(f"    // {node.var} released (stack)")

        elif isinstance(node, PrintStmt):
            parts = ' << '.join(f'"{p}"' if not p.isidentifier() else p for p in node.parts)
            main_lines.append(f"    cout << {parts} << endl;")

        elif isinstance(node, FunctionCall):
            args = ', '.join(rewrite_expr(arg) for arg in node.args)
            main_lines.append(f"    {node.target}({args});")

        elif isinstance(node, StructInstance):
            args = ', '.join(rewrite_expr(arg) for arg in node.values)
            main_lines.append(f"    {node.struct_type} {node.name} = {{{args}}};")

        elif isinstance(node, ControlFlow):
            condition = rewrite_expr(node.condition)
            main_lines.append(f"    {node.kind} ({condition}) {{")
            for stmt in node.body:
                if isinstance(stmt, str):
                    main_lines.append(f"        {stmt};")
                elif isinstance(stmt, FunctionCall):
                    args = ', '.join(rewrite_expr(arg) for arg in stmt.args)
                    main_lines.append(f"        {stmt.target}({args});")
                elif isinstance(stmt, Assignment):
                    lhs = rewrite_expr(stmt.target)
                    rhs = rewrite_expr(stmt.value)
                    main_lines.append(f"        {lhs} = {rhs};")
                elif isinstance(stmt, PrintStmt):
                    parts = ' << '.join(f'"{p}"' if not p.isidentifier() else p for p in stmt.parts)
                    main_lines.append(f"        cout << {parts} << endl;")
            main_lines.append("    }")

        elif isinstance(node, StructDef):
            fields = '\n'.join(f"    {dot_type_to_cpp(dtype)} {name};" for dtype, name in node.fields)
            lines.append(f"struct {node.name} {{\n{fields}\n}};")

        elif isinstance(node, SetGroup):
            lines.append(f"namespace {node.name} {{")

            if '_' in node.name:
                base, dim = node.name.split('_', 1)
                for fn in node.functions:
                    for t, _ in fn.params:
                        if dim.isdigit():
                            expected_type = f"{base}_{dim}"
                            if t != expected_type:
                                raise Exception(f"Function param type '{t}' does not match set constraint '{expected_type}'")
                        elif dim == '':
                            if not t.startswith(base + '_'):
                                raise Exception(f"Function param type '{t}' not allowed in loosely-typed set_{base}_")

            for fn in node.functions:
                pseudo_vars = set()
                used_pseudos = set()
                params = []
                for t, n in fn.params:
                    name = n.strip('@')
                    if '@' in n:
                        pseudo_vars.add(name)
                    if t.startswith('i_') and t[2:].isdigit():
                        size = int(t[2:])
                        params.append(f"int (&{name})[{size}]")
                    else:
                        params.append(f"{dot_type_to_cpp(t)}& {name}")
                params = ', '.join(params)

                lines.append(f"    void {fn.name}({params}) {{")
                for stmt in fn.body:
                    if isinstance(stmt, PrintStmt):
                        parts = ' << '.join(f'"{p}"' if not p.isidentifier() else p for p in stmt.parts)
                        lines.append(f"        cout << {parts} << endl;")
                    elif isinstance(stmt, FunctionCall):
                        args = ', '.join(rewrite_expr(arg, pseudo_vars) for arg in stmt.args)
                        lines.append(f"        {stmt.target}({args});")
                    elif isinstance(stmt, Assignment):
                        lhs = rewrite_expr(stmt.target, pseudo_vars)
                        rhs = rewrite_expr(stmt.value, pseudo_vars)
                        lines.append(f"        {lhs} = {rhs};")
                        # mark pseudo as used
                        for pv in pseudo_vars:
                            if pv in stmt.target or pv in stmt.value:
                                used_pseudos.add(pv)
                unused = pseudo_vars - used_pseudos
                for pv in unused:
                    lines.append(f"        // Warning: pseudo '{pv}' was passed but never used")
                lines.append("    }")
            lines.append("}")

    lines.append("int main() {")
    lines.extend(main_lines)
    lines.append("    return 0;\n}")
    return '\n'.join(lines)

class StructInstance:
    def __init__(self, struct_type, name, values):
        self.struct_type = struct_type
        self.name = name
        self.values = values

def dot_type_to_cpp(dtype):
    return {
        'i_': 'int', 'f_': 'float', 's_': 'string', 'c_': 'char',
        'sh_': 'short', 'l_': 'long', 'll_': 'long long'
    }.get(dtype, dtype)

# === CLI Entry Point ===
def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: dotc <input.dot> [-o output.cpp]")
        return

    with open(sys.argv[1], 'r') as f:
        code = f.read()

    tokens = tokenize(code)
    ast = parse(tokens)
    cpp = emit_cpp(ast)

    output = sys.argv[3] if len(sys.argv) == 4 and sys.argv[2] == "-o" else "out.cpp"
    with open(output, 'w') as f:
        f.write(cpp)
    print(f"Compiled to {output}")

if __name__ == '__main__':
    main()
