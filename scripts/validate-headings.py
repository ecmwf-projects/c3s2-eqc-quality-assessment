import argparse
import re
from pathlib import Path

import nbformat

HEADINGS = (
    "## 🌍 Use case:",
    "## ❓ Quality assessment question",
    "## 📢 Quality assessment statement",
    "## 📋 Methodology",
    "## 📈 Analysis and results",
    "## ℹ️ If you want to know more",
)

ADMONITION_TITLE = "These are the key outcomes of this assessment"


def validate_headers(path: Path) -> None:
    notebook = nbformat.read(path, nbformat.NO_CONVERT)

    title_count = 0
    admonition_count = 0
    admonition_is_note = False
    headings_count = dict.fromkeys(HEADINGS, 0)

    anchors = set()
    references = set()
    is_analysis = False
    for cell in notebook.cells:
        if cell["cell_type"] != "markdown":
            continue

        source = cell.get("source", "")
        anchors.update(re.findall(r"\((.*?)\)=(?!`)", source))
        references.update(re.findall(r"\[\]\((.*?)\)", source))

        prev_line = ""
        for line in source.splitlines():
            line = line.strip()
            is_analysis = (
                not line == HEADINGS[-1] if is_analysis else line == HEADINGS[-2]
            )
            if is_analysis and line.startswith("### "):
                assert prev_line.endswith(")="), f"{path=!s}: Missing anchor for {line}"

            if line.startswith("# "):
                title_count += 1
            elif line == f"```{{admonition}} {ADMONITION_TITLE}":
                admonition_count += 1
            elif admonition_count and not admonition_is_note:
                admonition_is_note = line.startswith(":class: note")
                assert admonition_is_note, f"{path=!s}: The admonition is not a note"

            if line.startswith(("# ", "## ")):
                assert not line.lstrip("#").lstrip()[:1].isdigit(), (
                    f"{path=!s}: First two header levels cannot start with numbers"
                )

            if not path.name.startswith("template"):
                assert title_count, f"{path=!s}: The first line is not a title."

            for heading in headings_count:
                if line.startswith(heading):
                    headings_count[heading] += 1
                    break
            else:
                assert not line.startswith("## "), f"{path=!s}: Invalid H2 {line=}"

            prev_line = line

    assert title_count == 1, f"{path=!s}: Invalid {title_count=}"
    assert admonition_count == 1, f"{path=!s}: Invalid {admonition_count=}"
    assert anchors and anchors <= references, (
        f"{path=!s}: Missing section references {anchors - references}"
    )
    for heading, header_count in headings_count.items():
        assert header_count == 1, f"{path=!s}: Invalid {header_count=} of {heading=}"


def main(paths: list[Path]) -> None:
    for path in paths:
        validate_headers(path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", action="store", type=Path, nargs="*")
    args = parser.parse_args()
    main(args.paths)
