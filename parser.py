
from lexer import Lexer
import ply.yacc as yacc


class Parser:
    def __init__(self):
        self.lexer_obj = None
        self.lexer = None
        self.symbol_table = {}  
        self.records = {}
        self.functions = {}
        self.in_type_def = False
        self.decl_type = None
        self.local_symbol_table = {}
        self.parser = yacc.yacc(
            module=self,
            debug=True,
            write_tables=True,
            outputdir="."
        )
    tokens = Lexer.tokens
    start = 'program'

    precedence = (
        ('left', 'OR'),
        ('left', 'AND'),
        ('right', 'NOT'),
        ('nonassoc', 'EQ', 'NEQ', 'GT', 'LT', 'GTE', 'LTE'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'MULT', 'DIV'),
        ('left', 'DOT'),
        ('nonassoc', 'ASSIGN'),
        ('nonassoc', 'ELSE'),    
        ('nonassoc', 'RECORD')
    )


    
    def p_program(self, p):
        '''program : optional_newlines top_level_list
                | empty'''
        p[0] = p[2] if len(p) == 3 else None


    def p_top_level_list(self, p):
        '''top_level_list : top_level optional_newlines top_level_list
                        | top_level optional_newlines'''
        if len(p) == 4:
            p[0] = [p[1]] + p[3]
        else:
            p[0] = [p[1]]


    def p_top_level(self, p):
        '''top_level : statement_with_newline
                    | func_def
                    | type_def'''
        p[0] = p[1]



                    
    # Lista de sentencias separadas por saltos de línea
    def p_statements(self, p):
        '''statements : statement_list'''
        p[0] = p[1]
        pass

    def p_statement_list(self, p):
        '''statement_list : statement_with_newline statement_list
                        | statement_with_newline'''
        if len(p) == 3:
            p[0] = ([p[1]] if p[1] is not None else []) + p[2]
        else:
            p[0] = [p[1]] if p[1] is not None else []


    def p_statement_with_newline(self, p):
        '''statement_with_newline : statement NEWLINE'''
        p[0] = p[1]


    # Sentencias posibles
    def p_statement(self, p):
        '''statement : declaration
                    | if_statement
                    | while_statement
                    | return_statement
                    | expression'''

            



    #Declaraciones

    def p_vector_declaration(self, p):
        '''declaration : type LBRACKET expression RBRACKET ID'''
        var_name = p[5]
        self.symbol_table[var_name] = {
            'type': p[1],
            'is_vector': True,
            'size': p[3]
        } 


    def p_declaration(self, p):
        '''declaration : type declaration_list'''
        tipo = p[1]
        self.decl_type = tipo  

        if isinstance(p[2], list):
            p[0] = [(tipo, var[0]) for var in p[2]]
        else:
            p[0] = [(tipo, p[2][0])]

        # PRIMERO registrar todas las variables, con control de re-declaración
        for var in p[2]:
            nombre = var[0]
            if nombre in self.symbol_table:
                print(f"Error: la variable '{nombre}' ya ha sido declarada")
            else:
                self.symbol_table[nombre] = {'type': tipo, 'is_vector': False}

        # SEGUNDO comprobar tipos de asignación si hay valor
        for var in p[2]:
            nombre = var[0]
            valor = var[1]
            if valor is not None:
                assigned_type = self.get_expression_type(valor)
                if tipo == 'float' and assigned_type == 'int':
                    continue  # permitido
                if assigned_type != tipo:
                    print(f"Error de tipos: no se puede asignar un '{assigned_type}' a un '{tipo}'")

        self.decl_type = None





    def p_declaration_list(self, p):
        '''declaration_list : declaration_item COMMA declaration_list
                            | declaration_item'''
        if len(p) == 4:
            p[0] = [p[1]] + p[3]
        else:
            p[0] = [p[1]]

    def p_declaration_item(self, p):
        '''declaration_item : ID
                            | ID ASSIGN expression'''
        if len(p) == 2:
            p[0] = (p[1], None)
        else:
            p[0] = (p[1], p[3])




    def p_declarations(self, p):
        '''declarations : declaration NEWLINE declarations
                        | declaration NEWLINE'''
        if len(p) == 4:
            p[0] = [p[1]] + p[3]
        else:
            p[0] = [p[1]] 
        pass

    def p_id_list(self, p):
        '''id_list : ID COMMA id_list
                | ID'''
        if len(p) == 4:
            p[0] = [p[1]] + p[3]
        else:
            p[0] = [p[1]]

    def p_record_instantiation(self, p):
        '''declaration : TYPENAME ID %prec RECORD'''
        tipo = p[1]
        nombre_var = p[2]
        if tipo not in self.lexer_obj.typedefs:
            print(f"Error: el tipo '{tipo}' no ha sido definido")
        else:
            self.symbol_table[nombre_var] = {
                'type': tipo,
                'is_record': True,
                'fields': {}
            }


  

    #Tipos

    def p_type(self, p):
        '''type : builtin_type
                | TYPENAME %prec RECORD'''
        p[0] = p[1]  



    def p_builtin_type(self, p):
        '''builtin_type : INT
                        | FLOAT
                        | CHAR
                        | BOOL'''
        p[0] = p[1]


    def p_type_def(self, p):
        '''type_def : TYPE TYPENAME COLON type_block
                    | TYPE ID COLON type_block'''
        typename = p[2]
        self.lexer_obj.typedefs.add(typename)

        campos = []
        for decl in p[4]:  
            if isinstance(decl, list):
                campos.extend(decl)
            elif isinstance(decl, tuple):
                campos.append(decl)

        self.records[typename] = campos
        p[0] = ('type_def', typename, campos)


    def p_type_block(self, p):
        '''type_block : LBRACE type_declaration_lines RBRACE'''
        p[0] = p[2]

    def p_type_declaration_line(self, p):
        '''type_declaration_line : declaration NEWLINE
                                | NEWLINE'''
        if len(p) == 3:
            p[0] = p[1] if isinstance(p[1], list) else [p[1]]
        else:
            p[0] = []



    def p_type_declaration_lines(self, p):
        '''type_declaration_lines : type_declaration_line type_declaration_lines
                                | type_declaration_line'''
        if len(p) == 3:
            p[0] = []
            if p[1]:
                p[0].extend(p[1])
            p[0].extend(p[2])
        else:
            p[0] = p[1] if p[1] else []


    def p_type_declaration_list(self, p):
        '''type_declaration_list : declaration
                                | declaration type_declaration_list'''
        pass


    #Expresiones 

    def p_expression(self, p):
        '''expression : expression PLUS expression
                    | expression MINUS expression
                    | expression MULT expression
                    | expression DIV expression
                    | expression EQ expression
                    | expression NEQ expression
                    | expression GT expression
                    | expression GTE expression
                    | expression LT expression
                    | expression LTE expression
                    | expression AND expression
                    | expression OR expression
                    | NOT expression
                    | MINUS expression %prec NOT
                    | expression LBRACKET expression RBRACKET
                    | expression DOT ID %prec DOT  
                    | primary'''


        
        if len(p) == 2:
            p[0] = p[1]

        elif len(p) == 3:
            if p[1] == '-':
                p[0] = ('negate', p[2])
            elif p[1] == 'not':
                p[0] = ('not', p[2])

        elif len(p) == 4:
            if p[2] == '.':
                p[0] = ('dot', p[1], p[3])
            else:
                p[0] = ('binary_op', p[2], p[1], p[3])

        elif len(p) == 5:
            p[0] = ('bracket', p[1], p[3])


    def p_primary(self, p):
        '''primary : ID
                | NUMBER
                | TRUE
                | FALSE
                | CHAR_LITERAL
                | func_call
                | LPAREN expression RPAREN'''
        if len(p) == 2:
            token = p.slice[1]
            name = token.value

            # Buscar en local primero
            if token.type == 'ID':
                if name not in self.local_symbol_table and name not in self.symbol_table:
                    print(f"Error semántico: variable '{name}' no declarada")

            # Literales
            if token.type == 'CHAR_LITERAL':
                p[0] = ('char', name)
            elif token.type == 'TRUE':
                p[0] = ('bool', True)
            elif token.type == 'FALSE':
                p[0] = ('bool', False)
            elif token.type == 'NUMBER':
                p[0] = name
            else:
                p[0] = name
        else:
            p[0] = p[2]
        
    def p_assignable(self, p):
        '''assignable : ID
                    | expression DOT ID
                    | expression LBRACKET expression RBRACKET'''
        if len(p) == 2:
            p[0] = p[1]
            if p[1] not in self.symbol_table:
              print(f"Error semántico: variable '{p[1]}' no declarada")
        elif p[2] == '.':
            p[0] = ('dot', p[1], p[3])
        else:
            p[0] = ('bracket', p[1], p[3])



    #Aisngaciones

    def p_statement_assignment(self, p):
        '''statement : assignable ASSIGN expression'''
        target = p[1]
        rhs = p[3]
        if isinstance(target, str) and target not in self.symbol_table:
            print(f"Error semántico: variable '{target}' no declarada")

        lhs_type = self.get_expression_type(target)
        rhs_type = self.get_expression_type(rhs)
        if not self.can_convert(rhs_type, lhs_type):
            print(f"Error de tipos: no se puede asignar un '{rhs_type}' a un '{lhs_type}'")

        p[0] = ('assign', target, rhs)


    def p_statement_assignment_chain(self, p):
        '''statement : assignable_chain ASSIGN expression'''

        # Extrae todas las variables en cadena
        for target in p[1]:
            if isinstance(target, str) and target not in self.symbol_table:
                print(f"Error semántico: variable '{target}' no declarada")

            lhs_type = self.get_expression_type(target)
            rhs_type = self.get_expression_type(p[3])
            if not self.can_convert(rhs_type, lhs_type):
                print(f"Error de tipos: no se puede asignar un '{rhs_type}' a un '{lhs_type}'")


        p[0] = ('assign_chain', p[1], p[3])

    def p_assignable_chain(self, p):
        '''assignable_chain : assignable ASSIGN assignable_chain
                            | assignable'''
        if len(p) == 4:
            p[0] = [p[1]] + p[3]  # izquierda primero
        else:
            p[0] = [p[1]]



    # Control de flujo
    def p_if_statement(self, p):
        '''if_statement : IF expression block
                        | IF expression block ELSE block'''
        if len(p) == 4:
            p[0] = ('if', p[2], p[3])
        else:
            p[0] = ('if_else', p[2], p[3], p[5])




    def p_while_statement(self, p):
        '''while_statement : WHILE expression block'''
        cond_type = self.get_expression_type(p[2])
        if cond_type != 'bool':
            print(f"Error de tipos: la condición del while debe ser 'bool', no '{cond_type}'")
        p[0] = ('while', p[2], p[3])


    # Funciones
    def p_func_def(self, p):
        '''func_def : DEF type ID LPAREN param_list RPAREN store_params prepare_func_scope COLON LBRACE NEWLINE statement_list RBRACE'''
        return_type = p[2]
        func_name = p[3]
        params = self._pending_params
        body = p[10]  # estaba en p[8] cuando era 'block'

        self.current_return_type = return_type
        self._pending_params = params

        input_types = []
        for param in params:
            if isinstance(param, tuple) and param[0] == 'param':
                input_types.append(param[1])

        key = (func_name, tuple(input_types))
        self.functions[key] = return_type
        self.records[func_name] = [('input', input_types), ('output', return_type)]

        self.local_symbol_table = {}
        self.symbol_table = self.old_symbol_table
        del self._pending_params
        del self.current_return_type
        p[0] = ('func_def', return_type, func_name, params, body)


    def p_param_list(self, p):
        '''param_list : param param_list_tail
                    | empty'''
        if len(p) == 3:
            p[0] = [p[1]] + p[2]
        else:
            p[0] = []
        
        self._last_params = p[0]  # <-- AÑADIR ESTA LÍNEA



    def p_param_list_tail(self, p):
        '''param_list_tail : COMMA param param_list_tail
                        | empty'''
        if len(p) == 4:
            p[0] = [p[2]] + p[3]
        else:
            p[0] = []
    def p_store_params(self, p):
        '''store_params :'''
        self._pending_params = self._last_params


    def p_param(self, p):
        '''param : type ID
                | ID'''
        if len(p) == 3:
            p[0] = ('param', p[1], p[2])

    def p_return_statement(self, p):
        '''return_statement : RETURN expression'''
        ret_type = self.get_expression_type(p[2])
        if hasattr(self, 'current_return_type'):
            if self.current_return_type != ret_type:
                print(f"Error de retorno: se esperaba '{self.current_return_type}' pero se devuelve '{ret_type}'")
        p[0] = ('return', p[2])

    

    # Llamadas a funciones

    def p_func_call(self, p):
        '''func_call : ID LPAREN arg_list RPAREN'''
        p[0] = ('func_call', p[1], p[3])

    def p_arg_list(self, p):
        '''arg_list : arg_list COMMA expression
                    | expression
                    | empty'''   
        if len(p) == 4:
            p[0] = p[1] + [p[3]] 
        elif len(p) == 2:
            if p[1] is None:
                p[0] = []
            else:
                p[0] = [p[1]]

    
    #Necesario 

    def p_empty(self, p):
        '''
        empty :
        '''
        p[0] = None

    def p_error(self, p):
        if p:
            print(f"Error de sintaxis en token '{p.value}', línea {p.lineno}")
        else:
            print("Error de sintaxis al final del archivo")

    def debug_with_file(self, path):
        with open(path, 'r') as file:
            code = file.read()
            print("Contenido del archivo:")
            print(code)
            result = self.parser.parse(code, lexer=self.lexer)
            print("Resultado del parser (AST):")
            print(result)
            return result





#ENTREGA FINAL Y CORRECCIONES DE P2:

    def p_block(self, p):
        '''block : COLON optional_newlines statement_list
                | COLON LBRACE NEWLINE statement_list RBRACE NEWLINE'''
        if p[1] == ':':
            p[0] = p[3]  # statement_list está en p[3]
        else:
            p[0] = p[2]  # statement_list está en p[2]


    def export_symbol_table(self, output_path):
        with open(output_path, 'w') as f:
            for name, info in self.symbol_table.items():
                f.write(f"{info['type']} {name}\n")

    def export_record_table(self, output_path):
        with open(output_path, 'w') as f:
            for typename, fields in self.records.items():
                if all(isinstance(field, tuple) for field in fields):
                    if fields and fields[0][0] == 'input':
                        # Función
                        campos = f"input: {', '.join(fields[0][1])}, output: {fields[1][1]}"
                    else:
                        # Registro
                        campos = ', '.join([f"{field_type}:{name}" for field_type, name in fields])
                    f.write(f"{typename} {campos}\n")


    def export_symbol_table(self, output_path):
        with open(output_path, 'w') as f:
            for name, info in self.symbol_table.items():
                f.write(f"{info['type']} {name}\n")

    def get_expression_type(self, expr):
        try:
            if isinstance(expr, str) and expr.isdigit():
                return 'int'
        except:
            pass

        if isinstance(expr, (int, float)):
            return 'int' if isinstance(expr, int) else 'float'

        if isinstance(expr, tuple):
            tag = expr[0]

            if tag == 'char':
                return 'char'
            if tag == 'bool':
                return 'bool'
            if tag == 'negate' or tag == 'not':
                return self.get_expression_type(expr[1])
            if tag == 'binary_op':
                _, op, left, right = expr
                lt = self.get_expression_type(left)
                rt = self.get_expression_type(right)
                if op in ('+', '-', '*', '/'):
                    return 'float' if 'float' in (lt, rt) else 'int'
                if op in ('==', '!=', '<', '<=', '>', '>='):
                    return 'bool'
                if op in ('and', 'or'):
                    return 'bool'
            if tag == 'dot':
                base, field = expr[1], expr[2]

                # Resuelve el tipo del objeto base recursivamente
                base_type = self.get_expression_type(base)

                if base_type in self.records:
                    for t, name in self.records[base_type]:
                        if name == field:
                            return t
                return 'unknown'


            if tag == 'bracket':
                container = expr[1]
                container_type = self.get_expression_type(container)
                if container_type:
                    return container_type  # simplificación
            if tag == 'func_call':
                name, args = expr[1], expr[2]
                arg_types = tuple(self.get_expression_type(a) for a in args)
                key = (name, arg_types)
                return self.functions.get(key, 'unknown')

        if isinstance(expr, str):
            if expr in self.local_symbol_table:
                return self.local_symbol_table[expr]['type']
            elif expr in self.symbol_table:
                return self.symbol_table[expr]['type']
            elif expr in ('true', 'false'):
                return 'bool'
            return 'unknown'


        return 'unknown'


    def p_prepare_func_scope(self, p):
        '''prepare_func_scope :'''
        # Evitar fallo si _pending_params no está definido por error previo
        if not hasattr(self, '_pending_params'):
            print("Error: _pending_params no definido (error de sintaxis previo)")
            self._pending_params = []

        self.old_symbol_table = self.symbol_table.copy()
        self.symbol_table = self.old_symbol_table

        self.local_symbol_table = {}
        for param in self._pending_params:
            if isinstance(param, tuple) and param[0] == 'param':
                _, tipo, nombre = param
                self.local_symbol_table[nombre] = {'type': tipo, 'is_vector': False}

    def p_optional_newlines(self, p):
        '''optional_newlines : optional_newlines NEWLINE
                            | empty'''
        pass

    def can_convert(self, from_type, to_type):
        if from_type == to_type:
            return True
        if to_type == 'char' and from_type in ('int', 'float'):
            return True
        if to_type == 'int' and from_type == 'float':
            return True
        return False  

    def export_symbol_table(self, output_path):
        campos_en_records = set()
        for nombre_tipo, campos in self.records.items():
            # Solo incluir si son registros de verdad, no funciones
            if campos and isinstance(campos[0], tuple) and campos[0][0] != 'input':
                for tipo, nombre in campos:
                    campos_en_records.add(nombre)

        with open(output_path, 'w') as f:
            for name, info in self.symbol_table.items():
                if name not in campos_en_records:
                    f.write(f"{info['type']} {name}\n")
