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
    "BOpen": "B-Open",
    "http://doi.org": "https://doi.org",
    "https://ads-beta.atmosphere.copernicus.eu": "https://ads.atmosphere.copernicus.eu",
    "http://ads-beta.atmosphere.copernicus.eu": "https://ads.atmosphere.copernicus.eu",
    "https://cds-beta.climate.copernicus.eu": "https://cds.climate.copernicus.eu",
    "http://cds-beta.climate.copernicus.eu": "https://cds.climate.copernicus.eu",
    "https://ewds-beta.climate.copernicus.eu": "https://ewds.climate.copernicus.eu",
    "http://ewds-beta.climate.copernicus.eu": "https://ewds.climate.copernicus.eu",
    "https://datastore.copernicus-climate.eu": "https://dast.copernicus-climate.eu",
    "http://datastore.copernicus-climate.eu": "https://dast.copernicus-climate.eu",
}

ADMONITION_TITLE = "These are the key outcomes of this assessment"

CLASS_NOTE = ":class: note"


def fix_template_divergences(path: Path) -> None:
    notebook = nbformat.read(path, nbformat.NO_CONVERT)

    write = False
    for cell in notebook.cells:
        if cell["cell_type"] != "markdown":
            continue

        if ")=\n\n" in (source := cell["source"]):
            cell["source"] = source.replace(")=\n\n", ")=\n")
            write = True

        for old, new in STRING_MAPPER.items():
            if old in (source := cell.get("source", "")):
                cell["source"] = source.replace(old, new)
                write = True

        sections = []
        for section in cell.get("source", "").split("## "):
            if section.startswith("📢 Quality assessment statement"):
                for line in section.splitlines():
                    if line.strip().startswith("```{admonition}"):
                        newline = (
                            f"```{{admonition}} {ADMONITION_TITLE}"
                            if ADMONITION_TITLE not in line
                            else line
                        )
                        if CLASS_NOTE not in section:
                            newline = "\n".join([newline, CLASS_NOTE])
                        if newline != line:
                            section = section.replace(line, newline)
                            write = True
                        break
            sections.append(section)
        cell["source"] = "## ".join(sections)

    if write:
        nbformat.write(notebook, path)


def main(paths: list[Path]) -> None:
    for path in paths:
        fix_template_divergences(path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", action="store", type=Path, nargs="*")
    args = parser.parse_args()
    main(args.paths)
