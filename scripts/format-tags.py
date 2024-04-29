import nbformat
from pathlib import Path
import argparse

MANDATORY_TAGS: dict[str, set[str]] = {"code": {"hide-input"}}


def main(paths: list[Path]) -> None:
    for path in paths:
        write = False
        notebook = nbformat.read(path, nbformat.NO_CONVERT)

        for cell in notebook.cells:
            tags = set(cell["metadata"].get("tags", []))
            mandatory_tags = MANDATORY_TAGS.get(cell["cell_type"], set())
            if not mandatory_tags <= tags:
                write = True
                cell["metadata"]["tags"] = list(tags | mandatory_tags)

        if write:
            nbformat.write(notebook, path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", action="store", type=Path, nargs="*")
    args = parser.parse_args()
    main(args.paths)
