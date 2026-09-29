import ply.lex as lex

class Lexer:

    reserved = {
        'true': 'TRUE',
        'false': 'FALSE',
        'int': 'INT',
        'float': 'FLOAT',
        'char': 'CHAR',
        'bool': 'BOOL',
        'def': 'DEF',
        'return': 'RETURN',
        'type': 'TYPE',
        'if': 'IF',
        'else': 'ELSE',
        'and': 'AND',
        'or': 'OR',
        'not': 'NOT',
        'while': 'WHILE'
    }

    tokens = (
        'ID', 'TYPENAME', 'CHAR_LITERAL', 'NUMBER',
        'EQ', 'GT', 'LT', 'GTE', 'LTE', 'ASSIGN', 'NEQ',
        'PLUS', 'MINUS', 'MULT', 'DIV',
        'LPAREN', 'RPAREN', 'LBRACKET', 'RBRACKET', 'LBRACE', 'RBRACE', 'COMMA', 'COLON',
        'NEWLINE', 'DOT'
    ) + tuple(reserved.values())

    
    t_EQ = r'=='
    t_NEQ = r'!='
    t_GT = r'>'
    t_LT = r'<'
    t_GTE = r'>='
    t_LTE = r'<='
    t_ASSIGN = r'='
    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_MULT = r'\*'
    t_DIV = r'/'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'
    t_LBRACE = r'\{'
    t_RBRACE = r'\}'
    t_COMMA = r','
    t_COLON = r':'
    t_DOT = r'\.'

    t_ignore = ' \t'

    def __init__(self, typedefs=None):
        self.typedefs = typedefs if typedefs is not None else set()
        self.lexer = lex.lex(module=self)
        self.typedefs = set()


    def t_STRING_COMMENT(self, t):
        r"'''(.|\n)*?'''"
        t.lexer.lineno += t.value.count('\n')
        return None  

    def t_LINE_COMMENT(self, t):
        r"\#[^\n]*"
        pass

    def t_NUMBER(self, t):
        r'0[bB][01]+|0[oO][0-9]+|0[xX][0-9A-F]+|0[0-9]+|\d+\.\d+([eE][-+]?\d+)?|\d+[eE][-+]?\d+|[1-9]\d*|0'

        value = t.value

        try:
            if value.startswith(('0b', '0B')):
                t.value = int(value, 2)
            elif value.startswith(('0o', '0O')):
                digits = value[2:]
                for d in digits:
                    if d not in '01234567':
                        raise ValueError(f"número octal inválido: '{value}'")
                t.value = int(value, 8)
            elif value.startswith(('0x', '0X')):
                t.value = int(value, 16)
            elif '.' in value or 'e' in value.lower():
                t.value = float(value)
            else:
                t.value = int(value)
        except ValueError as e:
            print(f"Error léxico en línea {t.lineno}: {e}")
            t.lexer.skip(len(value))
            return None

        return t

    def t_CHAR_LITERAL(self, t):
        r"'([^\\'\n]|\\[nrt0'\"\\])'"
        contenido = t.value[1:-1]  # quita las comillas
        t.value = contenido
        return t


    def t_NEWLINE(self, t):
        r'(\r\n|\r|\n)+'
        t.lexer.lineno += t.value.count('\n') + t.value.count('\r')
        if t.lexer.lexpos >= len(t.lexer.lexdata):
            return None

        next_char = self.lexer.lexdata[t.lexer.lexpos]
        if next_char not in '\n\r#':
            return t

    
    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        if t.value in self.reserved:
            t.type = self.reserved[t.value]
        elif t.value in self.typedefs:
            t.type = 'TYPENAME'
        else:
            t.type = 'ID'
        return t


    
    def t_error(self, t):
        print(f"Error léxico: carácter inesperado '{t.value[0]}' en línea {t.lineno}")
        t.lexer.skip(1)


    def process_file(self, path, output_path=None):
        with open(path, 'r') as file:
            self.lexer.input(file.read())
            if output_path:
                with open(output_path, 'w') as out:
                    for tok in self.lexer:
                        out.write(f"{tok.type} {tok.value}\n")
            else:
                for tok in self.lexer:
                    print(tok)
