# Changelog

## 2.9.0

- Add `csv_group_by(rows, column)` to group rows by a text-normalized cell value while preserving encounter order.
- Add `csv_distinct(rows, columns)` to keep the first row for each unique single or composite key.
- Validate requested columns and reject duplicate distinct-key columns.
- Add regression coverage for grouping order, stable distinct selection, composite keys, and invalid inputs.

## 2.8.0

- Add CSV file workflows and row transformations: `csv_read`, `csv_read_many`, `csv_write`, `csv_filter`, `csv_select`, and `csv_sort`.
- Keep CSV batch schemas consistent and confine file access to the project directory.
- Add tests for CSV transformation and file workflows.

## 2.6.0

- Add UTF-8 `read_text` and `write_text` built-ins for project-local automation.
- Reject absolute paths, project-root escapes, and symlink escapes; require a file-backed program.
- Add regression tests for normal file operations and path confinement.

## 2.5.2

- Add decimal and scientific-notation numeric literals.
- Reject incomplete exponents with a source-located lexical error.
- Add regression tests for fractional values and exponent parsing.

## 2.5.1

- Enforce strict JSON parsing: reject `NaN`, infinities, duplicate object keys, and numeric overflow.
- Enforce JSON-compatible values on serialization, including text-only object keys.
- Expand regression coverage for malformed and ambiguous JSON inputs.

## 2.5.0

- Add built-in JSON parsing and deterministic compact JSON serialization.
- Sort serialized object keys, preserve Unicode, and reject non-finite JSON numbers.
- Add regression tests for stable output, round-tripping null, and invalid JSON diagnostics.

## 1.9.0

- Add the official `kitsune format` formatter and `--check` mode.
- Preserve comments and string literals while normalizing spacing and indentation.
- Validate source before formatting and guarantee idempotent output.

## 1.8.1

- Separate Kitsune and Singular reserved-word sets.
- Normalize runtime failures as language-level errors.
- Add source locations to lexical and syntax errors.
- Implement short-circuit behavior for `and` and `or`.
- Expand module regression coverage for nested imports, caching, cycles, and path confinement.
- Run CI on Python 3.11, 3.12, and 3.13.

## 1.8.0

- Initial independent package baseline with functions, collections, control flow, and project-local module imports.
