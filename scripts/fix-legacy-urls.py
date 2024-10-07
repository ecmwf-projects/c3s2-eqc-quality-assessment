import argparse
from pathlib import Path

import nbformat

STRING_MAPPER = {"/cdsapp#!/dataset/": "/datasets/"}


def fix_legacy_urls(path: Path) -> None:
    notebook = nbformat.read(path, nbformat.NO_CONVERT)

    write = False
    for cell in notebook.cells:
        if "source" not in cell:
            continue

        for old, new in STRING_MAPPER.items():
            if old in (source := cell["source"]):
                cell["source"] = source.replace(old, new)
                write = True

    if write:
        nbformat.write(notebook, path)


def main(paths: list[Path]) -> None:
    for path in paths:
        fix_legacy_urls(path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", action="store", type=Path, nargs="*")
    args = parser.parse_args()
    main(args.paths)
