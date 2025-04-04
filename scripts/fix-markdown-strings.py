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

QA_STATEMENT_FORMAT = {
    "l0": "## 📢 Quality assessment statement",
    "l2": f"```{{admonition}} {ADMONITION_TITLE}",
    "l3": ":class: note",
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

        if QA_STATEMENT_FORMAT["l0"] in (source := cell.get("source", "")):
            line_list = []
            line_cnt = 0
            is_cell_changed = False
            for line in source.splitlines():
                line_list.append(line.strip())
                if QA_STATEMENT_FORMAT["l0"] in line:
                    qa_state_line = line_cnt
                line_cnt += 1
            if line_list[qa_state_line + 1]:
                qa_state_line -= 1
            if ADMONITION_TITLE not in line_list[qa_state_line + 2]:
                line_list[qa_state_line + 2] = QA_STATEMENT_FORMAT["l2"]
                is_cell_changed = True
            if QA_STATEMENT_FORMAT["l3"] not in line_list[qa_state_line + 3]:
                line_list.insert(qa_state_line + 3, QA_STATEMENT_FORMAT["l3"])
                is_cell_changed = True
            if is_cell_changed:
                cell["source"] = "\n".join(line_list)
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
