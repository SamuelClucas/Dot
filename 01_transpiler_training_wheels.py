#!/usr/bin/env python3
# Updated transpile_line to support the new parameter rule:
# Function definitions use , for writable references, . for const
# Function calls use ; for writable refs, : for const
# Definitions must end their param list with , or . even for one param
import re
from pathlib import Path
from glob import glob
from os import makedirs

# === Shared State ===
transpiled_lines = []
training_wheels = []
line_map = []

# === Patterns ===
STRING_DECL = re.compile(r"s_ ([a-zA-Z_]\w*)\" *= *(.*):")
PTR_DECL = re.compile(r"i_ *'([a-zA-Z_]\w*)")
HEAP_DECL = re.compile(r"i~ *'([a-zA-Z_]\w*)")
CONST_PTR = re.compile(r"i_ *([a-zA-Z_]\w*)\s*=.*?:")
EPHEMERAL = re.compile(r"i_ (?!').*[^,:]\s*$")
PRINT_EXPR = re.compile(r'p"(.+)"?')
DEREF_EXPR = re.compile(r"([a-zA-Z_]\w*)\"(\d*)")
FREE_PTR = re.compile(r"~?([a-zA-Z_]\w*)\\")
SET_DEF = re.compile(r"set ([a-zA-Z_]\w*)\(\)\s*{")
FUNC_DEF = re.compile(r"([a-zA-Z_]\w*)\((.*)\)\s*{")
CALL_EXPR = re.compile(r"([a-zA-Z_]\w*)\.([a-zA-Z_]\w*)\((.*)\)")


def transpile_line_refined(line, line_num):
    code = line.strip()
    if not code or code.startswith("//"):
        return line

    # Ephemeral misuse
    if EPHEMERAL.match(code):
        training_wheels.append(f"⚠️ Line {line_num+1}: ephemeral must end with `,`")
        return f"// {line}"

    # Const pointer
    if CONST_PTR.search(code):
        var = CONST_PTR.search(code).group(1)
        training_wheels.append(f"🔒 Const '{var}' declared on line {line_num+1}")
        return code.replace(f"i_ {var} =", f"const int {var} =").replace(":", "")

    # Heap allocation
    if HEAP_DECL.search(code):
        var = HEAP_DECL.search(code).group(1)
        training_wheels.append(f"💡 Heap pointer '{var}' declared on line {line_num+1}, remember to free with ~{var}\\")
        return f"int* {var} = (int*)malloc(sizeof(int));"

    # Heap or stack free
    if FREE_PTR.match(code):
        var = FREE_PTR.match(code).group(1)
        return f"free({var});"

    # Pointer declaration
    if PTR_DECL.search(code):
        var = PTR_DECL.search(code).group(1)
        return code.replace(f"i_ '{var}", f"int* {var}")

    # String declaration
    if STRING_DECL.match(code):
        var, val = STRING_DECL.match(code).groups()
        return f'std::string {var} = {val};'

    # Print command
    if PRINT_EXPR.match(code):
        expr = PRINT_EXPR.match(code).group(1)
        return f'std::cout << {expr} << std::endl;'

    # Dereference expression used alone (e.g. name")
    if DEREF_EXPR.match(code) and code.endswith('"'):
        var, index = DEREF_EXPR.match(code).groups()
        if index:
            return f'std::cout << {var}[{index}] << std::endl;'
        else:
            return f'std::cout << *{var} << std::endl;'

    # set block
    if SET_DEF.match(code):
        set_name = SET_DEF.match(code).group(1)
        return f'namespace {set_name} {{'

    # function definition
    if FUNC_DEF.match(code):
        fname, args = FUNC_DEF.match(code).groups()
        arglist = []
        if args.strip():
            for sep in [",", "."]:
                if sep in args:
                    parts = [a.strip() for a in args.split(sep) if a.strip()]
                    for part in parts:
                        if "s_" in part and "'" in part:
                            var = part.split("'")[1]
                            base = f"std::string* {var}"
                        elif "i_" in part and "'" in part:
                            var = part.split("'")[1]
                            base = f"int* {var}"
                        if sep == ".":
                            base = f"const {base}"
                        arglist.append(base)
        return f'void {fname}({", ".join(arglist)}) {{'

    # function call with ; and :
    if CALL_EXPR.match(code):
        namespace, func, args = CALL_EXPR.match(code).groups()
        arglist = []
        for a in re.split(r"[;:]", args):
            a = a.strip().replace("'", "")
            if a:
                arglist.append(a)
        return f"{namespace}::{func}({', '.join(arglist)});"

    return code

# Re-transpile using refined symbol rule
def transpile_dot_file_refined(dot_path):
    transpiled_lines.clear()
    training_wheels.clear()
    line_map.clear()

    inside_main = []
    outside_main = []

    with open(dot_path) as f:
        for line_num, line in enumerate(f):
            line_map.append(line)
            cpp = transpile_line_refined(line, line_num)
            if cpp:
                # Keep definitions outside of main
                if cpp.startswith("namespace") or cpp.startswith("void") or cpp.startswith("std::string") or cpp.startswith("#") or cpp.startswith("}") or cpp.startswith("free("):
                    outside_main.append(cpp)
                else:
                    inside_main.append(cpp)

    return "\n".join([
        "#include <iostream>",
        "#include <string>",
        "#include <cstdlib>",
        ""
    ] + outside_main + [
        "",
        "int main() {"
    ] + [f"    {l}" for l in inside_main] + [
        "    return 0;",
        "}"
    ])

# Run refined transpilation
dot_path = "src/hello_world.dot"
refined_cpp_output = transpile_dot_file_refined(dot_path)
refined_output_path = "build/hello_world_refined.cpp"

with open(refined_output_path, "w") as f:
    f.write(refined_cpp_output)

refined_output_path