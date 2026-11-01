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

## Runtime behavior

- `and` and `or` short-circuit and return boolean values.
- Runtime failures (invalid operations, indexing, and builtin calls) are reported as `RuntimeLangError`, not raw Python exceptions.
- Lexical and syntax errors carry source line and column information.
- Only Kitsune declaration words (`let`, `spell`, `echo`) are reserved by this frontend; Singular's `value`, `fn`, and `print` remain available as ordinary Kitsune identifiers.
- Imported modules resolve relative to their importer, stay inside the project root, use `.kit`, and are cached after a successful load.

## Official formatter

Format a source file in place:

```bash
kitsune format path/to/program.kit
```

Check formatting without changing the file (suitable for CI):

```bash
kitsune format --check path/to/program.kit
```

The formatter validates the program before writing, preserves comments and string literals, uses four-space indentation, and produces stable, idempotent output.
