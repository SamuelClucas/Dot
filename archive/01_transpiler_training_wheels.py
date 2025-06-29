#!/usr/bin/env python3
# Updated transpile_line to support the new parameter rule:
# Function definitions use , for writable references, . for const
# Function calls use ; for writable refs, : for const
# Definitions must end their param list with , or . even for one param
# Dot to C++ Transpiler (MVP) - Proof of Concept

# === Assumptions ===
# - Only handles a subset: i_ declarations, integer arrays, set-defined functions, and pointer-style arithmetic.
# - Assumes valid Dot input.
# - Maps basic operations and memory rules.
# Dot to C++ Transpiler (Improved MVP)
# Dot to C++ Transpiler (Improved MVP)

# Dot to C++ Transpiler (Improved MVP with All Types)
# Dot to C++ Transpiler (Now with Struct Support + All Types)

import re

# Type mapping for Dot -> C++
dot_types = {
    'i': 'int',
    'f': 'float',
    'd': 'double',
    's': 'std::string',
    'c': 'char',
    'l': 'long',
    'll': 'long long',
    'sh': 'short'
}

in_struct = False
current_struct = ""
struct_fields = []

def transpile_dot_line(dot_line):
    global in_struct, current_struct, struct_fields
    dot_line = dot_line.strip()

    if not dot_line:
        return ""

    if re.match(r"^('\w+\\\s*)+$", dot_line):
        return ""

    if match := re.match(r"([a-z]+)_(\d*)\s+'?(\w+);?", dot_line):
        dtype, size, name = match.groups()
        ctype = dot_types.get(dtype, 'int')
        if size:
            return f"{ctype} {name}[{size}];"
        else:
            return f"{ctype}* {name} = new {ctype};"

    if match := re.match(r"(\w+)\"(\d*)\s*=\s*([\w\"+\-* /]+);", dot_line):
        var, index, expr = match.groups()
        expr = expr.replace('"', '*')
        if index:
            return f"{var}[{index}] = {expr};"
        else:
            return f"*{var} = {expr};"

    if match := re.match(r"(\w+)\s*=\s*([\w+\-*/]+),", dot_line):
        var, val = match.groups()
        return f"{var} = {val};"

    if match := re.match(r"set\s+(\w+)\((.*?)\)\s*{", dot_line):
        name, params = match.groups()
        cpp_params = []
        for p in params.split(','):
            p = p.strip()
            if not p:
                continue
            type_match = re.match(r"([a-z]+)_\s*'?([\w]+)([.,])", p)
            if not type_match:
                continue
            dtype, pname, modifier = type_match.groups()
            ctype = dot_types.get(dtype, 'int')
            if "'" in p:
                cpp_params.append(f"{ctype}* {pname}")
            else:
                cpp_params.append(f"{ctype} {pname}")
        return f"void {name}({', '.join(cpp_params)}) {{"

    if match := re.match(r"struct\s+(\w+)\((.*?)\)\s*{", dot_line):
        current_struct, params = match.groups()
        struct_fields = []
        in_struct = True
        for p in params.split(','):
            p = p.strip()
            if not p:
                continue
            type_match = re.match(r"([a-z]+)_\s*'?([\w]+),?", p)
            if type_match:
                dtype, name = type_match.groups()
                ctype = dot_types.get(dtype, 'int')
                struct_fields.append((ctype, name))
        return f"struct {current_struct} {{"

    if dot_line == "}" and in_struct:
        in_struct = False
        init_lines = [f"    {ctype}* {name};" for ctype, name in struct_fields]
        ctor_body = [f"        {name} = new {ctype};\n        *{name} = 0;" for ctype, name in struct_fields]
        dtor_body = [f"        delete {name};" for _, name in struct_fields]
        constructor = f"    {current_struct}() {{\n{chr(10).join(ctor_body)}\n    }}"
        destructor = f"    ~{current_struct}() {{\n{chr(10).join(dtor_body)}\n    }}"
        return "\n".join(init_lines + [constructor, destructor, "};"])

    if match := re.match(r"}\s*((?:'\w+\\\s*)+)", dot_line):
        return "}"

    if match := re.match(r"while\((.*?)\,\)", dot_line):
        cond = match.group(1).replace('"', '*')
        return f"while({cond}) {{"

    if match := re.match(r"if\((.*?)\)", dot_line):
        cond = match.group(1).replace('"', '*')
        return f"if({cond}) {{"

    if dot_line == "}":
        return "}"

    if match := re.match(r"(\w+)\"", dot_line):
        var = match.group(1)
        return f"std::cout << *{var} << std::endl;"

    if match := re.match(r"(\w+(?:\.\w+)*)\((.*?)\);", dot_line):
        fname, args = match.groups()
        fname = fname.replace('.', '_')
        cpp_args = [a.replace("'", "&").replace(':', '').strip() for a in args.split(';') if a.strip()]
        return f"{fname}({', '.join(cpp_args)});"

    return f"// [UNHANDLED] {dot_line}"


# === Full Dot Program ===
dot_program = r"""
struct Vec2(i_ 'x, i_ 'y,) {
    x" = 0;
    y" = 0;
} 'x\ 'y\

Vec2 'v;
v.x" = 3;
v.y" = 7;
v"
'v\
"""

cpp_lines = [transpile_dot_line(line) for line in dot_program.strip().split('\n')]
print("\n".join(cpp_lines))

