# Kitsune / Kitsu

**Kitsune** (también llamado **Kitsu**) es un lenguaje expresivo y amistoso para automatización, scripting e inteligencia artificial aplicada.

Esta es la implementación independiente de Kitsune, separada del prototipo conjunto `Languages`. La versión inicial conserva el comportamiento de `Languages` v1.8.0 y su sistema de módulos `.kit`; la infraestructura de lexer, AST y runtime se mantiene dentro de este repositorio para permitir evolución y releases independientes.

## Características de v1.8.0

- Sintaxis propia: `let`, `spell`, `echo`, bloques sin punto y coma obligatorio.
- Funciones, closures, scopes léxicos, condicionales y bucles `while` / `for`.
- `break` y `continue` locales al bucle actual.
- Arrays, mapas, acceso por índice y acceso por punto a claves textuales.
- Builtins: `range`, `len`, `push`, `pop`, `first`, `last`, `join`, `split`, `keys`, `values`, `has`, `type`, `str`.
- Imports `import "lib/math.kit" as math`, con caché, scopes aislados y protección contra rutas externas y ciclos.
- CLI `kitsune` y alias `kitsu`.

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
# Alias corto
kitsu examples/hello.kit
```

```kitsune
spell greet(name) {
  echo "Hello, " + name
}

let agent = {"name": "Kitsu", "tags": ["automation", "ai"]}
greet(agent.name)
echo agent.tags[0]
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
```

GitHub Actions ejecuta la suite en Python 3.11, 3.12 y 3.13. Consulta [`docs/language.md`](docs/language.md) para la referencia del lenguaje.

## Filosofía

Kitsune prioriza legibilidad, expresividad y ciclos rápidos de experimentación. Su roadmap puede incorporar automatización de tareas, APIs cómodas y herramientas para IA aplicada sin convertirlo en una copia de Singular.