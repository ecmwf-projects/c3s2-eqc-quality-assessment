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


def validate_headers(path: Path) -> None:
    notebook = nbformat.read(path, nbformat.NO_CONVERT)

    title_count = 0
    headings_count = dict.fromkeys(HEADINGS, 0)
    for cell in notebook.cells:
        if cell["cell_type"] != "markdown":
            continue

        for line in cell.get("source", "").splitlines():
            line = line.strip()

            if line.startswith("# "):
                title_count += 1
                continue
            assert title_count or path.name.startswith(
                "template"
            ), f"{path=!s}: The first line is not a title."

            for heading in headings_count:
                if line.startswith(heading):
                    headings_count[heading] += 1
                    break
            else:
                assert not line.startswith("## "), f"{path=!s}: Invalid H2 {line=}"

    assert title_count == 1, f"{path=!s}: Invalid {title_count=}"
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
