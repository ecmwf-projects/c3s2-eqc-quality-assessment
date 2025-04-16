import argparse
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
    ref_count = 0
    anchor_count = 0
    admonition_is_note = False
    headings_count = dict.fromkeys(HEADINGS, 0)
    for cell in notebook.cells:
        if cell["cell_type"] != "markdown":
            continue

        methodology_count = 0
        for line in cell.get("source", "").splitlines():
            line = line.strip()

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

            if "## 📋 Methodology" in line:
                methodology_count += 1
            if methodology_count:
                if "[](" in line:
                    ref_count += 1
                if ")=" in line:
                    anchor_count += 1

            if not path.name.startswith("template"):
                assert title_count, f"{path=!s}: The first line is not a title."

            for heading in headings_count:
                if line.startswith(heading):
                    headings_count[heading] += 1
                    break
            else:
                assert not line.startswith("## "), f"{path=!s}: Invalid H2 {line=}"

    assert title_count == 1, f"{path=!s}: Invalid {title_count=}"
    assert admonition_count == 1, f"{path=!s}: Invalid {admonition_count=}"
    assert ref_count, f"{path=!s}: No links to relevant sections"
    assert ref_count == anchor_count, (
        f"{path=!s}: Section reference mismatch {ref_count=}, {anchor_count=}"
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
