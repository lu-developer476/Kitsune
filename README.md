# Kitsune / Kitsu

**Kitsune** (también llamado **Kitsu**) es un lenguaje expresivo y amistoso para automatización, scripting e inteligencia artificial aplicada.

## Características de v2.5.2

- Sintaxis propia: `let`, `spell`, `echo`, bloques sin punto y coma obligatorio.
- Funciones, closures, scopes léxicos, condicionales y bucles `while` / `for`.
- Literales numéricos enteros, decimales y notación científica (`1.25e-2`).
- `break` y `continue` locales al bucle actual; `and` y `or` con cortocircuito.
- Arrays, mapas, acceso por índice y acceso por punto a claves textuales.
- Builtins de colecciones y tipos: `range`, `len`, `push`, `pop`, `first`, `last`, `join`, `split`, `keys`, `values`, `has`, `type`, `str`.
- JSON integrado: `json_parse(text)` y `json_stringify(value)`; salida compacta y ordenada, Unicode preservado, rechazo de claves no textuales, duplicadas, valores no compatibles, números no finitos y entradas no estándar.
- Imports `import "lib/math.kit" as math`, con caché, scopes aislados y protección contra rutas externas y ciclos.
- CLI `kitsune` y alias `kitsu`; formateador oficial con modo `--check`.
- Errores de léxico/sintaxis con ubicación y errores de ejecución normalizados.

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

## Desarrollo

```bash
python -m pytest
kitsune format examples/hello.kit
kitsune format --check examples/hello.kit
```

GitHub Actions ejecuta la suite en Python 3.11, 3.12 y 3.13. Consulta [`docs/language.md`](docs/language.md) para la referencia del lenguaje.

Kitsune prioriza legibilidad, expresividad y ciclos rápidos de experimentación. Su roadmap puede incorporar automatización de tareas, APIs cómodas y herramientas para IA aplicada sin convertirse en una copia de Singular.
