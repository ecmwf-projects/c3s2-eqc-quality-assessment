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
    "## Quality Assessment question": "## ❓ Quality assessment question",
    "## ❓ Quality Assessment Question": "## ❓ Quality assessment question",
    "## Quality assessment statement": "## 📢 Quality assessment statement",
    "## Quality Assessment Statement": "## 📢 Quality assessment statement",
    "## 📢 Quality Assessment Statement": "## 📢 Quality assessment statement",
    "## Methodology": "## 📋 Methodology",
    "## Analysis and results": "## 📈 Analysis and results",
    "## Analysis and Results": "## 📈 Analysis and results",
    "## 📈 Analysis and Results": "## 📈 Analysis and results",
    "## If you want to know more": "## ℹ️ If you want to know more",
}

ADMONITION_TITLE = "These are the key outcomes of this assessment"


def fix_legacy_urls(path: Path) -> None:
    notebook = nbformat.read(path, nbformat.NO_CONVERT)

    write = False
    admonition_count = 0
    admonition_is_note = False
    for cell in notebook.cells:
        if cell["cell_type"] != "markdown":
            continue

        for old, new in STRING_MAPPER.items():
            if old in (source := cell.get("source", "")):
                cell["source"] = source.replace(old, new)
                write = True

        for line in (source := cell.get("source", "")).splitlines():
            line = line.strip()
            if line == f"```{{admonition}} {ADMONITION_TITLE}":
                admonition_count += 1
            elif admonition_count and not admonition_is_note:
                admonition_is_note = line.startswith(":class: note")
                if not admonition_is_note:
                    cell["source"] = source.replace(line, ":class: note\n" + line)
                    admonition_count = 0
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
