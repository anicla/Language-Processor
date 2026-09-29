import sys
import os
from lexer import Lexer
from parser import Parser
import re
import io
import contextlib


def main():
    if len(sys.argv) < 2:
        print("Uso: python main.py archivo.vip")
        return

    input_path = sys.argv[1]

    if not os.path.exists(input_path):
        print(f"Archivo '{input_path}' no encontrado.")
        return

    with open(input_path, 'r', encoding='utf-8') as f:
        code = f.read()

    lexer = Lexer()
    lexer2 = Lexer()
    base_name = os.path.splitext(input_path)[0]
    output_token_path = base_name + ".token"

    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        lexer2.process_file(input_path, output_token_path)

    print(" Generating LALR tables")
    parser = Parser()
    parser.lexer_obj = lexer
    parser.lexer = lexer.lexer

    try: 
        for match in re.finditer(r'\btype\s+([A-Za-z_][A-Za-z_0-9]*)\b', code):
            typename = match.group(1)
            lexer.typedefs.add(typename)

        parser.parser.parse(code, lexer=lexer.lexer)
        parser.export_symbol_table(base_name + ".symbol")
        parser.export_record_table(base_name + ".record")

        print(" ...")
    except Exception as e:
        print(" Error durante el análisis sintáctico:", e)

if __name__ == "__main__":
    main()
