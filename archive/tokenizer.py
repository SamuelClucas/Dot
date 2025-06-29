# Dot to C++ Transpiler with Full Dot Language Support

import re

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value})"

rules = [
    ('ELLIPSIS', r'\.\.\.'),
    ('TYPE',     r'\$_|i_|s_|f_|sh_|c_|l_|ll_'),
    ('KEYWORD',  r'\b(set|struct|if|while|when|except|else|elif)\b'),
    ('NUMBER',   r'\d+'),
    ('IDENT',    r"[a-zA-Z_]\w*"),
    ('GLYPH',    r'[\"\'@\\\$\.\{\}\(\)]'),
    ('COMPARE',  r'=='),
    ('ASSIGN',   r'='),
    ('END',      r';|:|,'),
    ('SKIP',     r'\s+'),
]

class Node: pass

class AssignmentNode(Node):
    def __init__(self, target, value):
        self.target = target
        self.value = value
    def __repr__(self):
        return f"Assignment({self.target} = {self.value})"

class DeclarationNode(Node):
    def __init__(self, dtype, name):
        self.dtype = dtype
        self.name = name
    def __repr__(self):
        return f"Declaration({self.dtype}, {self.name})"

class PrintNode(Node):
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return f"Print({self.name})"

class MemberAccessNode(Node):
    def __init__(self, object_name, field_name):
        self.object_name = object_name
        self.field_name = field_name
    def __repr__(self):
        return f"MemberAccess({self.object_name}.{self.field_name})"

class MemberAssignmentNode(Node):
    def __init__(self, object_name, field_name, value):
        self.object_name = object_name
        self.field_name = field_name
        self.value = value
    def __repr__(self):
        return f"MemberAssignment({self.object_name}.{self.field_name} = {self.value})"

class StructInstanceNode(Node):
    def __init__(self, struct_type, name, fields):
        self.struct_type = struct_type
        self.name = name
        self.fields = fields
    def __repr__(self):
        return f"StructInstance({self.struct_type} {self.name}({self.fields}))"

class StructNode(Node):
    def __init__(self, name, fields):
        self.name = name
        self.fields = fields
    def __repr__(self):
        return f"Struct({self.name}) {{ {self.fields} }}"

class SetFunctionNode(Node):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body
    def __repr__(self):
        return f"SetFunction({self.name})"

class SetGroupNode(Node):
    def __init__(self, group_name, types, functions):
        self.group_name = group_name
        self.types = types
        self.functions = functions
    def __repr__(self):
        return f"SetGroup({self.group_name})"

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

    def match(self, type_, value=None):
        tok = self.peek()
        if tok and tok.type == type_ and (value is None or tok.value == value):
            return self.advance()
        return None

    def parse(self):
        nodes = []
        while self.peek():
            tok = self.peek()
            if self.is_member_assignment():
                nodes.append(self.parse_member_assignment())
            elif self.is_member_access():
                access = self.parse_member_access()
                if self.peek() and self.peek().value == '"':
                    self.advance()
                    nodes.append(PrintNode(f"{access.object_name}.{access.field_name}"))
                else:
                    nodes.append(access)
            elif tok.type == 'TYPE':
                nodes.append(self.parse_declaration())
            elif tok.type == 'IDENT' and self.pos + 1 < len(self.tokens) and self.tokens[self.pos + 1].type == 'GLYPH':
                nodes.append(self.parse_assignment())
            else:
                self.advance()
        return nodes

    def is_member_access(self):
        return (
            self.pos + 2 < len(self.tokens)
            and self.tokens[self.pos].type == 'IDENT'
            and self.tokens[self.pos + 1].type == 'GLYPH'
            and self.tokens[self.pos + 1].value == '.'
            and self.tokens[self.pos + 2].type == 'IDENT'
        )

    def is_member_assignment(self):
        return (
            self.pos + 4 < len(self.tokens)
            and self.tokens[self.pos].type == 'IDENT'
            and self.tokens[self.pos + 1].type == 'GLYPH'
            and self.tokens[self.pos + 1].value == '.'
            and self.tokens[self.pos + 2].type == 'IDENT'
            and self.tokens[self.pos + 3].type == 'ASSIGN'
        )

    def parse_member_access(self):
        obj = self.advance().value
        self.match('GLYPH', '.')
        field = self.advance().value
        return MemberAccessNode(obj, field)

    def parse_member_assignment(self):
        obj = self.advance().value
        self.match('GLYPH', '.')
        field = self.advance().value
        self.match('ASSIGN')
        value = self.advance().value
        self.match('END')
        return MemberAssignmentNode(obj, field, value)

    def parse_assignment(self):
        target = self.advance().value
        glyph = self.advance().value
        target += glyph
        self.match('ASSIGN')
        value = self.advance().value
        self.match('END')
        return AssignmentNode(target, value)

    def parse_declaration(self):
        dtype = self.advance().value
        if self.peek().type == 'GLYPH' and self.peek().value == "'":
            self.advance()
        name = self.advance().value
        self.match('END')
        return DeclarationNode(dtype, name)

def emit_node(node):
    if isinstance(node, AssignmentNode):
        return [f"{node.target[:-1]} = {node.value};"]
    elif isinstance(node, DeclarationNode):
        return [f"{dot_type_to_cpp(node.dtype)} {node.name};"]
    elif isinstance(node, MemberAccessNode):
        return [f"{node.object_name}.{node.field_name}"]
    elif isinstance(node, MemberAssignmentNode):
        return [f"{node.object_name}.{node.field_name} = {node.value};"]
    elif isinstance(node, PrintNode):
        return [f"cout << {node.name} << endl;"]
    else:
        return [f"// [UNHANDLED] {node}"]

def emit_expr(value):
    if isinstance(value, Node):
        return emit_node(value)[0].rstrip(';')
    return str(value)

def dot_type_to_cpp(dtype):
    return {
        'i_': 'int', 'f_': 'float', 'd_': 'double', 's_': 'string',
        'c_': 'char', 'sh_': 'short', 'l_': 'long', 'll_': 'long long'
    }.get(dtype, dtype)

def emit_cpp(nodes):
    lines = [
        "#include <iostream>",
        "#include <string>",
        "using namespace std;",
        ""
    ]
    for node in nodes:
        lines.extend(emit_node(node))
    return "\n".join(lines)

def tokenize(code):
    tokens = []
    pattern = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in rules)
    regex = re.compile(pattern)
    for match in regex.finditer(code):
        kind = match.lastgroup
        value = match.group()
        if kind == 'SKIP':
            continue
        tokens.append(Token(kind, value))
    return tokens





code = "if('x) {x\" = 5; }elif(x\" == 2) { x\" = 3;} else {} while('x){x\"} except(){} set_i lol{f(i_ @f){} y(i_ @f){}} struct_vec(i_ 'a); i_ a\" = 2; vec_ instance(a\"); instance.a\""

tokens = tokenize(code)
print("=== TOKENS ===")
for tok in tokens:
    print(tok)
parser = Parser(tokens)
print("=== TOKENS ===")
for tok in tokens:
    print(tok)
ast = parser.parse()
for node in ast:
    print(node)

tokens = tokenize(code)
parser = Parser(tokens)
ast = parser.parse()

cpp_code = emit_cpp(ast)
print(cpp_code)

