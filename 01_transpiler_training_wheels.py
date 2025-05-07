#!/usr/bin/env python3
import re

# Minimal example: transpile your language to C with training wheels (graceful mode)

def transpile(source, graceful=True):
    lines = source.strip().split('\n')
    output = ["#include <stdio.h>", "#include <stdlib.h>", ""]
    functions = []
    main_body = []
    declared_ptrs = {}  # name: line_number
    assigned_ptrs = set()
    freed_ptrs = set()
    auto_frees = []
    index_assignments = {}  # for arrays: name -> set(indexes)
    index_expectations = {}  # for arrays: name -> total_size

    for lineno, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue

        # Enforce semicolon rule for finality
        if not (stripped.endswith(';') or stripped.endswith('{') or stripped.endswith('}') or stripped.endswith('\\')):
            print(f"❌ Syntax warning on line {lineno + 1}: missing semicolon or improper line ending")
            print(f"   → {stripped}")

        # Array declaration: i_5 'g
        if match := re.match(r"i_(\d+)\s*'(\w+)$", stripped):
            size, name = match.groups()
            declared_ptrs[name] = lineno + 1
            index_expectations[name] = int(size)
            index_assignments[name] = set()
            continue

        # Scalar declaration (optional size 1): i_ 'f
        if match := re.match(r"i_(1)?\s*'(\w+)$", stripped):
            _, name = match.groups()
            declared_ptrs[name] = lineno + 1
            continue

        # Assign to scalar pointer: x" = val;
        if match := re.match(r"(\w+)\"\s*=\s*(.+);", stripped):
            name, value = match.groups()
            assigned_ptrs.add(name)
            main_body.append(f"*{name} = {value};")
            continue

        # Assign to array index: x"i = val;
        if match := re.match(r"(\w+)\"(\d+)\s*=\s*(.+);", stripped):
            name, index, value = match.groups()
            index_assignments.setdefault(name, set()).add(int(index))
            main_body.append(f"{name}[{index}] = {value};")
            continue

        # Print scalar: x";
        if match := re.match(r"(\w+)\";$", stripped):
            name = match.group(1)
            main_body.append(f"printf(\"%d\\n\", *{name});")
            continue

        # Print array index: x"n;
        if match := re.match(r"(\w+)\"(\d+);$", stripped):
            name, index = match.groups()
            main_body.append(f"printf(\"%d\\n\", {name}[{index}]);")
            continue

        # Deinitialisation: 'x\
        if match := re.match(r"'(\w+)\\\\", stripped):
            name = match.group(1)
            freed_ptrs.add(name)
            main_body.append(f"free({name});")
            continue

        # Function declaration: f(...) {
        if match := re.match(r"f\((.*?)\)\s*{", stripped):
            params = match.group(1).split(',')
            cparams = []
            for p in params:
                p = p.strip()
                if "'" in p:
                    cparams.append(f"int* {p.split("'")[1]}")
                else:
                    cparams.append(f"int {p.split('_')[1]}")
            functions.append(f"void f({', '.join(cparams)}) {{")
            continue

        if stripped == "}":
            functions.append("}")
            continue

        # Function call: f('a, 'b);
        if match := re.match(r"f\((.*?)\);", stripped):
            args = match.group(1).replace("'", "").split(',')
            args = [arg.strip() for arg in args]
            main_body.append(f"f({', '.join(args)});")
            continue

        main_body.append(f"// Unrecognized or raw: {stripped}")

    if graceful:
        for ptr, line in declared_ptrs.items():
            if ptr not in freed_ptrs:
                main_body.append(f"free({ptr}); // training wheels")
                auto_frees.append((ptr, line))

        for name, total in index_expectations.items():
            assigned = index_assignments.get(name, set())
            if len(assigned) < total:
                print(f"⚠️ Partial array '{name}' not fully assigned")
                missing = set(range(total)) - assigned
                print(f"   - Missing indices: {sorted(missing)}")

    final_output = output + functions + ["", "int main() {"] + main_body + ["    return 0;", "}"]

    if graceful and auto_frees:
        print("\n⚠️ Training wheels added (auto-deinitialised pointers):")
        for ptr, line in auto_frees:
            print(f"   - Line {line}: '{ptr}\\")
        print("\n🧠 Tip: Add these manually in your .dot file to remove warnings.")

    return '\n'.join(final_output)

# Sample test
source_code = """
i_ 'f
f" = 4;
i_5 'g
g"3 = 3;
i_4 'h;
for (i_ i = 0; i < 4; i++) {
    h"i = i + 1;
}
'h\\
"""

print(transpile(source_code))
