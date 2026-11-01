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

Collection and type helpers include `range`, `len`, `push`, `pop`, `first`, `last`, `join`, `split`, `keys`, `values`, `has`, `type`, and `str`. File automation adds `read_text(path)` and `write_text(path, content)` for UTF-8 text. These require a file-backed program, accept project-relative paths only, and reject absolute paths and paths (including symlinks) that escape the project directory. `write_text` returns the number of characters written.

## CSV data processing

- `csv_parse(text)` reads CSV text and returns an array of maps, using the first row as column names. All parsed cell values are text.
- `csv_stringify(rows)` writes an array of maps to CSV. Column names are sorted lexicographically for stable output; missing cells and `nil` become empty fields, and booleans use lowercase text.
- CSV parsing rejects empty or duplicate headers and rows with a different number of fields. Serialization accepts only text, numbers, booleans, and `nil`; nested collections and non-finite numbers are rejected.
- Output uses UTF-8-compatible Unicode and LF line endings. An empty input array serializes to empty text.

Example:

```kitsune
let rows = csv_parse(read_text("input.csv"))
echo json_stringify(rows)
write_text("output.csv", csv_stringify(rows))
```

CSV files can also be processed directly and in batches:

```kitsune
let rows = csv_read_many(["january.csv", "february.csv"])
let adults = csv_filter(rows, "status", "active")
let ordered = csv_sort(adults, "last_name")
let report = csv_select(ordered, ["last_name", "email"])
csv_write("active-users.csv", report)
```

- `csv_read(path)` reads and parses one project-local CSV file.
- `csv_read_many(paths)` combines multiple files in the supplied order; every non-empty file must have the same set of column names.
- `csv_write(path, rows)` serializes and writes rows using the same project-path restrictions as `write_text`.
- `csv_filter(rows, column, value)` keeps rows whose cell text matches the supplied scalar value.
- `csv_select(rows, columns)` creates new maps containing only the requested columns, in the requested order.
- `csv_sort(rows, column)` returns a stable, lexicographically sorted copy. It does not mutate the input.

All file operations remain confined to the directory containing the running program.

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
