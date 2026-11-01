import sys
from pathlib import Path
from .runner import run

def main():
    if len(sys.argv) != 2:
        print('usage: kitsune <file.kit>')
        raise SystemExit(2)
    path=Path(sys.argv[1])
    run(path.read_text(encoding='utf-8'), source_path=path)

if __name__ == '__main__':
    main()
