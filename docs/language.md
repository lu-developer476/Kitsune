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
