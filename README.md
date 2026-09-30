# Language Processor

Procesador de lenguaje desarrollado en Python utilizando PLY (Python Lex-Yacc).

El proyecto implementa las principales etapas de análisis de un lenguaje de programación: análisis léxico, análisis sintáctico y comprobaciones semánticas. El procesador reconoce diferentes construcciones del lenguaje y genera información sobre los tokens, símbolos y tipos definidos durante el análisis.

## Funcionalidades

El procesador incluye:

- Análisis léxico mediante PLY Lex.
- Análisis sintáctico mediante PLY Yacc y una gramática LALR.
- Reconocimiento de tipos `int`, `float`, `char` y `bool`.
- Declaración y asignación de variables.
- Expresiones aritméticas, relacionales y lógicas.
- Vectores.
- Estructuras de control `if/else` y `while`.
- Definición y llamada de funciones.
- Definición de nuevos tipos y registros.
- Comprobación de tipos.
- Detección de variables no declaradas.
- Control de redeclaraciones.
- Comprobación de tipos de retorno.
- Gestión de tablas de símbolos y registros.
- Detección de errores léxicos, sintácticos y semánticos.

## Estructura

```text
Language-Processor/
│
├── lexer.py
├── parser.py
├── main.py
│
├── examples/
│   ├── example1.vip
│   ├── example2.vip
│   ├── ...
│   └── example25.vip
│
├── requirements.txt
└── README.md
```

### `lexer.py`

Implementa el analizador léxico. Define los tokens, palabras reservadas, operadores y literales reconocidos por el lenguaje, además del tratamiento de comentarios y errores léxicos.

### `parser.py`

Implementa la gramática y el analizador sintáctico mediante PLY Yacc. También contiene las principales comprobaciones semánticas, gestión de tipos y generación de las tablas de símbolos y registros.

### `main.py`

Punto de entrada del programa. Lee el archivo fuente, ejecuta el análisis y genera los archivos de salida correspondientes.

### `examples/`

Contiene diferentes programas de prueba utilizados para comprobar el funcionamiento del procesador y las distintas construcciones soportadas por el lenguaje.

## Ejecución

Instalar las dependencias:

```bash
pip install -r requirements.txt
```

Ejecutar el procesador indicando como argumento un archivo `.vip`:

```bash
python main.py examples/example1.vip
```

Durante la ejecución se realizan los análisis léxico, sintáctico y semántico.

El programa puede generar los siguientes archivos:

```text
.token
.symbol
.record
```

Estos contienen, respectivamente, los tokens reconocidos, la tabla de símbolos y la información de los tipos o registros procesados.

## Tecnologías

- Python
- PLY (Python Lex-Yacc)
- LALR parsing

## Autor

Ana Claver Miranda  
Ingeniería Informática  
Universidad Carlos III de Madrid (UC3M)
