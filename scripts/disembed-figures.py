import argparse
import base64
from pathlib import Path

import nbformat


def main(paths: list[Path]) -> None:
    for path in paths:
        write = False
        notebook = nbformat.read(path, nbformat.NO_CONVERT)

        for cell in notebook.cells:
            attachments = cell.pop("attachments", {})
            for name, data in attachments.items():
                write = True
                cell["source"] = cell["source"].replace(
                    f"(attachment:{name})", f"({name})"
                )
                for encoded in data.values():
                    (path.parent / name).write_bytes(base64.b64decode(encoded))

        if write:
            nbformat.write(notebook, path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", action="store", type=Path, nargs="*")
    args = parser.parse_args()
    main(args.paths)
