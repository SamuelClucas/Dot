# Token class: basic tokenizer for the Dot language using class-based tokens.
# This example is an extensible foundation for Dot's lexer system.

import re
from typing import List

class Token:
    def __init__(self, type_: str, value: str, line: int, col: int):
        self.type = type_
        self.value = value
        self.line = line
        self.col = col

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)}, {self.line}:{self.col})"

# Token specifications for the Dot language
token_specification = [
    ('COMMENT',      r'//.*'),                 # Single-line comment
    ('WHITESPACE',   r'[ \t]+'),               # Whitespace
    ('NEWLINE',      r'\n'),                   # Line endings
    ('TYPE',         r'(i_|f_|d_|s_|c_|l_|ll_|sh_)'),  # Dot types
    ('SET_TYPE',     r'set_type'),             # set_type keyword
    ('SET',          r'set'),                  # set keyword
    ('STRUCT',       r'struct'),               # struct keyword
    ('FUNC_ARROW',   r'->'),                   # Function arrow (if used later)
    ('STRING',       r'"[^"]*"'),              # String literal
    ('NUMBER',       r'\d+'),                  # Integer literal
    ('IDENT',        r'[A-Za-z_]\w*'),         # Identifiers
    ('DEREF',        r'\'\''),                 # Double dereference
    ('DECL_ASSIGN',  r'"'),                    # Declaration + assign
    ('RELEASE',      r'\\'),                   # Release pointer
    ('POINTER',      r'\''),                   # Single pointer
    ('ASSIGN',       r'='),                    # Assignment operator
    ('OP',           r'[+\-*/%]'),             # Arithmetic operators
    ('SEMICOLON',    r';'),                    # Statement terminator
    ('LBRACE',       r'\{'),                   # Left brace
    ('RBRACE',       r'\}'),                   # Right brace
    ('LPAREN',       r'\('),                   # Left parenthesis
    ('RPAREN',       r'\)'),                   # Right parenthesis
    ('COMMA',        r','),                    # Comma
    ('UNKNOWN',      r'.'),                    # Any other character
]

# Compile the token regexes
token_regex = '|'.join(f'(?P<{name}>{regex})' for name, regex in token_specification)
compiled_re = re.compile(token_regex)

def tokenize(code: str) -> List[Token]:
    tokens = []
    line_num = 1
    line_start = 0
    for mo in compiled_re.finditer(code):
        kind = mo.lastgroup
        value = mo.group()
        column = mo.start() - line_start

        if kind == 'NEWLINE':
            line_num += 1
            line_start = mo.end()
        elif kind == 'WHITESPACE' or kind == 'COMMENT':
            continue  # Skip whitespace and comments
        else:
            tokens.append(Token(kind, value, line_num, column))
    return tokens

# Test snippet
test_code = '''
set_type math {
    add(i_ 'a, i_ 'b,) {
        'a = 'a + 'b;
    }
}
'''

tokens = tokenize(test_code)
tokens[:25]  # Show a sample of the first 25 tokens for inspection

