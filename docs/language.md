# Kitsune language reference

Kitsune (`.kit`) is designed for expressive scripting, automation and applied AI workflows.

## Syntax

- `let name = expression` declares a variable.
- `spell name(args) { ... }` declares a function.
- `echo expression` writes a value.
- `if condition { ... } else { ... }` branches.
- `while condition { ... }` and `for item in iterable { ... }` iterate.
- `break` and `continue` control the innermost loop.
- `import "path.kit" as alias` imports a project-local module.

Statements do not require semicolons. Strings use double quotes; comments begin with `#` or `//`.

## Numeric literals

Kitsune accepts integers, decimal literals, and scientific notation:

```kitsune
echo 42
echo 0.125
echo 1.25e-2
echo 2e3
```

A malformed exponent (for example, `3e+`) is reported as a lexical error with its source location.

## Built-ins

Collection and type helpers include `range`, `len`, `push`, `pop`, `first`, `last`, `join`, `split`, `keys`, `values`, `has`, `type`, and `str`.

## Strict JSON support

- `json_parse(text)` parses a JSON string into Kitsune values.
- `json_stringify(value)` serializes a Kitsune value to compact JSON, sorts object keys for stable output, and preserves Unicode.
- Parsing rejects `NaN`, infinities, duplicate object keys, and numbers that overflow the runtime's finite floating-point range.
- Serialization requires text object keys and JSON-compatible values; non-finite numbers and unsupported runtime values are rejected.

Example:

```kitsune
let data = json_parse("{\\"name\\":\\"Kitsu\\",\\"enabled\\":true}")
echo data.name
echo json_stringify(data)
```

## Runtime behavior

- `and` and `or` short-circuit and return boolean values.
- Runtime failures (invalid operations, indexing, and builtin calls) are reported as `RuntimeLangError`, not raw Python exceptions.
- Lexical and syntax errors carry source line and column information.
- Only Kitsune declaration words (`let`, `spell`, `echo`) are reserved by this frontend; Singular's `value`, `fn`, and `print` remain available as ordinary Kitsune identifiers.
- Imported modules resolve relative to their importer, stay inside the project root, use `.kit`, and are cached after a successful load.

## Official formatter

Format a source file in place with `kitsune format path/to/program.kit`; use `kitsune format --check path/to/program.kit` to verify formatting without changing the file. The formatter validates source before writing, preserves comments and string literals, uses four-space indentation, and produces stable, idempotent output.
