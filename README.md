# Kitsune / Kitsu

**Kitsune** (also known as **Kitsu**) is an expressive, approachable language for automation, scripting, and applied artificial intelligence.

## Features (v2.9.0)

- Its own syntax: `let`, `spell`, `echo`, with no mandatory semicolons.
- Functions, closures, lexical scopes, conditionals, and `while` / `for` loops.
- Integer, decimal, and scientific-notation numeric literals.
- `break` and `continue` scoped to the current loop; short-circuiting `and` and `or`.
- Arrays, maps, indexed access, and dot access to textual keys.
- Collection and type built-ins: `range`, `len`, `push`, `pop`, `first`, `last`, `join`, `split`, `keys`, `values`, `has`, `type`, `str`.
- Strict JSON support: `json_parse` and `json_stringify`, compact and ordered output, preserved Unicode, and rejection of unsupported inputs/values.
- CSV support: `csv_parse`, `csv_stringify`, `csv_read`, `csv_read_many`, `csv_write`, `csv_filter`, `csv_select`, `csv_sort`, `csv_group_by`, and `csv_distinct`.
- Imports such as `import "lib/math.kit" as math`, with caching, isolated scopes, and protection against external paths and cycles.
- `kitsune` CLI and `kitsu` alias; official formatter with `--check` mode.
- UTF-8 file operations confined to the project directory.

## Requirements and installation

Python 3.11 or newer.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
python -m pip install -e ".[dev]"
```

## Run

```bash
kitsune examples/hello.kit
kitsu examples/hello.kit
```

```kitsune
spell greet(name) {
  echo "Hello, " + name
}

let payload = json_parse("{\\"name\\":\\"Kitsu\\",\\"active\\":true}")
echo payload.name
echo json_stringify(payload)
```

## Modules

Imports are resolved relative to the importing file and remain confined to the project's root directory:

```kitsune
import "lib/math.kit" as math
echo math.double(21)
```

Top-level names that do not start with `_` are exposed through the alias. Each module is executed once per interpreter and retains its environment for closures.

## CSV

```kitsune
let rows = csv_read_many(["january.csv", "february.csv"])
let active = csv_filter(rows, "status", "active")
let ordered = csv_sort(active, "last_name")
let report = csv_select(ordered, ["last_name", "email"])
let by_team = csv_group_by(report, "last_name")
let unique = csv_distinct(report, ["last_name", "email"])
csv_write("report.csv", unique)
```

`csv_group_by(rows, column)` returns a map of arrays of rows grouped by the text in a cell; it preserves the order in which groups and rows appear. `csv_distinct(rows, columns)` keeps the first row for each unique key, which may be composite. Both validate that the columns exist and leave the original array unchanged. `csv_sort` sorts lexicographically, not numerically.

## Development

```bash
python -m pytest
kitsune format examples/hello.kit
kitsune format --check examples/hello.kit
```

GitHub Actions runs the test suite on Python 3.11, 3.12, and 3.13. See [`docs/language.md`](docs/language.md) for the complete language reference.

Kitsune prioritizes readability, expressiveness, and fast experimentation cycles. Its roadmap may include task automation, convenient APIs, and tools for applied AI without turning it into a copy of Singular.

---

# Kitsune / Kitsu

**Kitsune** (también llamado **Kitsu**) es un lenguaje expresivo y amigable para automatización, scripting e inteligencia artificial aplicada.

## Características (v2.9.0)

- Sintaxis propia: `let`, `spell`, `echo`, sin obligación de terminar las sentencias con punto y coma.
- Funciones, closures, ámbitos léxicos, condicionales y bucles `while` / `for`.
- Literales numéricos enteros, decimales y en notación científica.
- `break` y `continue` limitados al bucle actual; operadores `and` y `or` con evaluación de cortocircuito.
- Arrays, mapas, acceso por índice y acceso por punto a claves de texto.
- Funciones integradas para colecciones y tipos: `range`, `len`, `push`, `pop`, `first`, `last`, `join`, `split`, `keys`, `values`, `has`, `type`, `str`.
- Compatibilidad estricta con JSON: `json_parse` y `json_stringify`, salida compacta y ordenada, Unicode preservado y rechazo de entradas o valores no compatibles.
- Compatibilidad con CSV: `csv_parse`, `csv_stringify`, `csv_read`, `csv_read_many`, `csv_write`, `csv_filter`, `csv_select`, `csv_sort`, `csv_group_by` y `csv_distinct`.
- Imports como `import "lib/math.kit" as math`, con caché, ámbitos aislados y protección contra rutas externas y ciclos.
- CLI `kitsune` y alias `kitsu`; formateador oficial con modo `--check`.
- Operaciones UTF-8 sobre archivos confinadas al directorio del proyecto.

## Requisitos e instalación

Python 3.11 o superior.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
python -m pip install -e ".[dev]"
```

## Ejecución

```bash
kitsune examples/hello.kit
kitsu examples/hello.kit
```

```kitsune
spell greet(name) {
  echo "Hello, " + name
}

let payload = json_parse("{\\"name\\":\\"Kitsu\\",\\"active\\":true}")
echo payload.name
echo json_stringify(payload)
```

## Módulos

Los imports se resuelven en relación con el archivo que los importa y permanecen confinados al directorio raíz del proyecto:

```kitsune
import "lib/math.kit" as math
echo math.double(21)
```

Los nombres de nivel superior que no comienzan con `_` se exponen mediante el alias. Cada módulo se ejecuta una sola vez por intérprete y conserva su entorno para las closures.

## CSV

```kitsune
let rows = csv_read_many(["january.csv", "february.csv"])
let active = csv_filter(rows, "status", "active")
let ordered = csv_sort(active, "last_name")
let report = csv_select(ordered, ["last_name", "email"])
let by_team = csv_group_by(report, "last_name")
let unique = csv_distinct(report, ["last_name", "email"])
csv_write("report.csv", unique)
```

`csv_group_by(rows, column)` devuelve un mapa de arrays de filas agrupadas por el texto de una celda; conserva el orden de aparición de los grupos y las filas. `csv_distinct(rows, columns)` conserva la primera fila de cada clave única, que puede ser compuesta. Ambas funciones validan que las columnas existan y no modifican el array original. `csv_sort` ordena lexicográficamente, no numéricamente.

## Desarrollo

```bash
python -m pytest
kitsune format examples/hello.kit
kitsune format --check examples/hello.kit
```

GitHub Actions ejecuta la suite de pruebas en Python 3.11, 3.12 y 3.13. Consultá [`docs/language.md`](docs/language.md) para acceder a la referencia completa del lenguaje.

Kitsune prioriza la legibilidad, la expresividad y los ciclos rápidos de experimentación. Su roadmap puede incorporar automatización de tareas, APIs cómodas y herramientas para IA aplicada sin convertirse en una copia de Singular.
