import argparse
import base64
from pathlib import Path

import nbformat
import nbformat.v4

LOGO_PATH = "../LogoLine_horizon_C3S.png"


def convert_notebook(path: Path) -> None:
    notebook = nbformat.read(path, nbformat.NO_CONVERT)

    # Add logo
    notebook.cells.insert(0, nbformat.v4.new_markdown_cell(f"![logo]({LOGO_PATH})"))

    # Decode figure
    for cell in notebook.cells:
        attachments = cell.pop("attachments", {})
        for name, data in attachments.items():
            cell["source"] = cell["source"].replace(f"(attachment:{name})", f"({name})")
            for encoded in data.values():
                (path.parent / name).write_bytes(base64.b64decode(encoded))

    nbformat.write(notebook, path)


def main(paths: list[Path]) -> None:
    for path in paths:
        convert_notebook(path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", action="store", type=Path, nargs="*")
    args = parser.parse_args()
    main(args.paths)
