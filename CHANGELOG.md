# Changelog

## 1.8.1

- Separate Kitsune and Singular reserved-word sets.
- Normalize runtime failures as language-level errors.
- Add source locations to lexical and syntax errors.
- Implement short-circuit behavior for `and` and `or`.
- Reject invalid assignment targets consistently.
- Expand module regression coverage for nested imports, caching, cycles, and path confinement.
- Run CI on Python 3.11, 3.12, and 3.13.

## 1.8.0

- Initial independent package baseline with functions, collections, control flow, and project-local module imports.
