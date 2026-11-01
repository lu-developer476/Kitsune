import sys
from pathlib import Path

from .formatter import format_source
from .runner import run


def main():
    args = sys.argv[1:]
    if args and args[0] in {'format', 'fmt'}:
        args = args[1:]
        check = '--check' in args
        args = [item for item in args if item != '--check']
        if len(args) != 1:
            print('usage: kitsune format [--check] <file.kit>', file=sys.stderr)
            raise SystemExit(2)
        path = Path(args[0])
        original = path.read_text(encoding='utf-8')
        formatted = format_source(original)
        if check:
            if original != formatted:
                print(f'{path} needs formatting', file=sys.stderr)
                raise SystemExit(1)
            return
        if original != formatted:
            path.write_text(formatted, encoding='utf-8')
            print(f'formatted {path}')
        return
    if len(args) != 1:
        print('usage: kitsune <file.kit> | kitsune format [--check] <file.kit>', file=sys.stderr)
        raise SystemExit(2)
    path = Path(args[0])
    run(path.read_text(encoding='utf-8'), source_path=path)


if __name__ == '__main__':
    main()
