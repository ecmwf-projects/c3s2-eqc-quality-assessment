import argparse
import collections
import re
from pathlib import Path

import nbformat

REFERENCE_PATTERN = r"\[\[([^\]]+)\]\]\(([^)]+)\)"


def validate_references(path: Path) -> None:
    notebook = nbformat.read(path, nbformat.NO_CONVERT)

    references = collections.defaultdict(set)
    for cell in notebook.cells:
        if cell["cell_type"] != "markdown":
            continue

        matches = re.findall(REFERENCE_PATTERN, cell.get("source", ""))
        for label, reference in matches:
            references[label].add(reference)

    wrong_references = "\n".join(
        [f"{k}: {v}" for k, v in references.items() if len(v) != 1]
    )
    assert not wrong_references, (
        f"{path=!s}: Inconsistent references\n{wrong_references}"
    )


def main(paths: list[Path]) -> None:
    for path in paths:
        validate_references(path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", action="store", type=Path, nargs="*")
    args = parser.parse_args()
    main(args.paths)
