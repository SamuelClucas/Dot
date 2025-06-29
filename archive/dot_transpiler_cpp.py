# Dot to C++ Transpiler

import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional

# === Intermediate Representation (IR) Classes ===

@dataclass
class DotStruct:
    name: str
    fields: List[str] = field(default_factory=list)

@dataclass
class DotFunction:
    name: str
    args: List[str]
    body: List[str]
    in_set: Optional[str] = None

@dataclass
class DotVariable:
    name: str
    dtype: str
    is_pointer: bool
    value: Optional[str] = None

@dataclass
class DotProgram:
    structs: Dict[str, DotStruct] = field(default_factory=dict)
    functions: List[DotFunction] = field(default_factory=list)
    variables: List[DotVariable] = field(default_factory=list)
    lines: List[str] = field(default_factory=list)
    sets: List[str] = field(default_factory=list)

# === Parsing Logic ===

def preprocess_code(dot_code: str) -> List[str]:
    dot_code = dot_code.replace('\\\n', '\n')
    dot_code = dot_code.replace('\\', '\n')
    raw_lines = dot_code.strip().splitlines()
    separated = []
    for line in raw_lines:
        tokens = re.split(r'(;|\n|\{|\})', line)
        buffer = ''
        for token in tokens:
            token = token.strip()
            if not token or token == ';':
                continue
            if token in ('{', '}', '\n'):
                if buffer:
                    separated.append(buffer.strip())
                    buffer = ''
                separated.append(token)
            else:
                buffer += ' ' + token if buffer else token
        if buffer:
            separated.append(buffer.strip())
    return separated

def parse_dot_program(dot_code: str) -> DotProgram:
    program = DotProgram()
    lines = preprocess_code(dot_code)

    in_struct = False
    current_struct = None
    in_function = False
    current_func = None
    current_set = None

    for i, line in enumerate(lines):
        if line.startswith("struct_"):
            struct_name = re.findall(r"struct_(\w+)", line)[0]
            current_struct = DotStruct(name=struct_name)
            in_struct = True
            continue

        if in_struct:
            if line == ")":
                program.structs[current_struct.name] = current_struct
                in_struct = False
            else:
                match = re.match(r"(\w+)_\s*\*?\s*(\w+)", line)
                if match:
                    dtype, varname = match.groups()
                    current_struct.fields.append((dtype, varname))
                else:
                    continue
            continue

        if line.startswith("set_"):
            current_set = re.findall(r"set_\w+\s+(\w+)", line)[0]
            program.sets.append(current_set)
            continue

        if match := re.match(r"(\w+)\((.*?)\)", line):
            fname, args = match.groups()
            next_index = i + 1
            if next_index < len(lines) and lines[next_index] == "{":
                current_func = DotFunction(name=fname, args=args.split(','), body=[], in_set=current_set)
                in_function = True
                continue

        if in_function:
            if line == "}":
                program.functions.append(current_func)
                in_function = False
            else:
                current_func.body.append(line)
            continue

        program.lines.append(line)

    return program

# === Helpers ===

def dot_type_to_cpp(dtype: str) -> str:
    mapping = {'i': 'int', 'f': 'float', 'd': 'double', 's': 'string', 'c': 'char'}
    return mapping.get(dtype, dtype)

def translate_line(line: str) -> str:
    if match := re.match(r"(\w+)_\s*'?(\w+)\"?\s*=\s*(.+)", line):
        dtype, name, val = match.groups()
        if "'" in line:
            return f"{dot_type_to_cpp(dtype)}* {name} = new {dot_type_to_cpp(dtype)}({val});"
        return f"{dot_type_to_cpp(dtype)} {name} = {val};"
    if match := re.match(r"(\w+)~\s*'(\w+)", line):
        dtype, name = match.groups()
        return f"{dot_type_to_cpp(dtype)}* {name} = new {dot_type_to_cpp(dtype)};"
    if match := re.match(r"(\w+)\"(\w+)", line):
        obj, field = match.groups()
        return f"cout << *({obj}.{field}) << endl;"
    if match := re.match(r"(\w+)\"", line):
        var = match.group(1)
        return f"cout << *{var} << endl;"
    if match := re.match(r"'(\w+)$", line):
        return f"delete {match.group(1)};"
    if match := re.match(r"(\w+)\.(\w+)\"\s*=\s*(.+)", line):
        obj, field, val = match.groups()
        return f"*({obj}.{field}) = {val};"
    if match := re.match(r"(\w+)_\s*'(\w+)\((.*?)\)", line):
        typename_, varname, args = match.groups()
        args_list = [arg.replace("'", "&").strip() for arg in args.split(',') if arg.strip()]
        return f"{typename_} {varname}({', '.join(args_list)});"
    if match := re.match(r"(\w+)\.(\w+)\((.*?)\)", line):
        setname, fname, args = match.groups()
        cpp_args = [arg.replace("'", "&").strip() for arg in args.split(',') if arg.strip()]
        return f"{setname}::{fname}({', '.join(cpp_args)});"
    return f"// [UNTRANSLATED] {line}"

# === Code Generator ===

def emit_cpp(program: DotProgram) -> str:
    output = ["#include <iostream>", "#include <string>", "using namespace std;\n"]

    for s in program.structs.values():
        output.append(f"struct {s.name} {{")
        for dtype, name in s.fields:
            cpp_type = dot_type_to_cpp(dtype)
            output.append(f"    {cpp_type}* {name};")
        output.append(f"    {s.name}({', '.join([f'{dot_type_to_cpp(t)}* _{n}' for t,n in s.fields])}) : ")
        init_list = [f"{n}(_{n})" for _, n in s.fields]
        output.append("        " + ", ".join(init_list) + " {}")
        output.append(f"    ~{s.name}() {{}}")
        output.append("};\n")

    for setname in program.sets:
        output.append(f"namespace {setname} {{")
        for func in program.functions:
            if func.in_set == setname:
                args = []
                for arg in func.args:
                    if not arg.strip(): continue
                    match = re.match(r"(\w+)_\s*\*?(\w+)", arg.strip())
                    if match:
                        dtype, name = match.groups()
                        args.append(f"{dot_type_to_cpp(dtype)}* {name}")
                output.append(f"void {func.name}({', '.join(args)}) {{")
                for line in func.body:
                    output.append(f"    {translate_line(line)}")
                output.append("}\n")
        output.append("} // end namespace\n")

    for line in program.lines:
        output.append(translate_line(line))

    return "\n".join(output)

# === Entry Point (Example Input) ===
dot_code = """
struct_Vec2 (
i_ *x;
i_ *y;
)
i_ a" = 3;
i_ b" = 4;
Vec2_ 'mystruct('a, 'b);
mystruct"x
mystruct"y
'v\
set_Vec2_i math{
    f1(i_ *f) {
        f*
    }
    f2(Vec2_ *v) {
        v*
    }
}
math.f1('a);
math.f2('v);
"""

program = parse_dot_program(dot_code)
cpp_output = emit_cpp(program)
print(cpp_output)