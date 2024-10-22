import argparse
from pathlib import Path

import nbformat

STRING_MAPPER = {
    "/cdsapp#!/dataset/": "/datasets/",
    "## Use case:": "## 🌍 Use case:",
    "## Use Case:": "## 🌍 Use case:",
    "## 🌍 Use Case:": "## 🌍 Use case:",
    "## Quality assessment question": "## ❓ Quality assessment question",
    "## Quality Assessment Question": "## ❓ Quality assessment question",
    "## Quality assessment statement": "## 📢 Quality assessment statement",
    "## Quality Assessment Statement": "## 📢 Quality assessment statement",
    "## Methodology": "## 📋 Methodology",
    "## Analysis and results": "## 📈 Analysis and results",
    "## Analysis and Results": "## 📈 Analysis and results",
    "## 📈 Analysis and Results": "## 📈 Analysis and results",
    "## If you want to know more": "## ℹ️ If you want to know more",
}


def fix_legacy_urls(path: Path) -> None:
    notebook = nbformat.read(path, nbformat.NO_CONVERT)

    write = False
    for cell in notebook.cells:
        if cell["cell_type"] != "markdown":
            continue

        for old, new in STRING_MAPPER.items():
            if old in (source := cell.get("source", "")):
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
