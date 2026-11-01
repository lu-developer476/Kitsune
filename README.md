# Kitsune / Kitsu

**Kitsune** (también llamado **Kitsu**) es un lenguaje expresivo y amistoso para automatización, scripting e inteligencia artificial aplicada.

## Características de v2.9.0

- Sintaxis propia: `let`, `spell`, `echo`, bloques sin punto y coma obligatorio.
- Funciones, closures, scopes léxicos, condicionales y bucles `while` / `for`.
- Literales numéricos enteros, decimales y notación científica.
- `break` y `continue` locales al bucle actual; `and` y `or` con cortocircuito.
- Arrays, mapas, acceso por índice y acceso por punto a claves textuales.
- Builtins de colecciones y tipos: `range`, `len`, `push`, `pop`, `first`, `last`, `join`, `split`, `keys`, `values`, `has`, `type`, `str`.
- JSON estricto: `json_parse` y `json_stringify`, salida compacta y ordenada, Unicode preservado y rechazo de entradas/valores no compatibles.
- CSV: `csv_parse`, `csv_stringify`, `csv_read`, `csv_read_many`, `csv_write`, `csv_filter`, `csv_select`, `csv_sort`, `csv_group_by` y `csv_distinct`.
- Imports `import "lib/math.kit" as math`, con caché, scopes aislados y protección contra rutas externas y ciclos.
- CLI `kitsune` y alias `kitsu`; formateador oficial con modo `--check`.
- Operaciones UTF-8 de archivos confinadas al directorio del proyecto.

## Requisitos e instalación

Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
python -m pip install -e ".[dev]"
```

## Ejecutar

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

Los imports se resuelven desde el archivo importador y quedan confinados al directorio raíz del proyecto:

```kitsune
import "lib/math.kit" as math
echo math.double(21)
```

Los nombres top-level que no empiezan con `_` se exponen en el alias. Cada módulo se ejecuta una vez por intérprete y conserva su entorno para closures.

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

`csv_group_by(rows, column)` devuelve un mapa de arrays de filas agrupadas por el texto de la celda; conserva el orden de aparición de grupos y filas. `csv_distinct(rows, columns)` conserva la primera fila de cada clave única, que puede ser compuesta. Ambos validan que las columnas existan y no modifican el array original. `csv_sort` ordena lexicográficamente, no numéricamente.

## Desarrollo

```bash
python -m pytest
kitsune format examples/hello.kit
kitsune format --check examples/hello.kit
```

GitHub Actions ejecuta la suite en Python 3.11, 3.12 y 3.13. Consulta [`docs/language.md`](docs/language.md) para la referencia completa.

Kitsune prioriza legibilidad, expresividad y ciclos rápidos de experimentación. Su roadmap puede incorporar automatización de tareas, APIs cómodas y herramientas para IA aplicada sin convertirse en una copia de Singular.
