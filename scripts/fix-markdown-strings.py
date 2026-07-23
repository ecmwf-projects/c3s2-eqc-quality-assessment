import argparse
import re
from pathlib import Path

import nbformat

STRING_MAPPER = {
    # Template
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
    # CADS
    "/cdsapp#!/dataset/": "/datasets/",
    "http://cds.climate.copernicus.eu": "https://cds.climate.copernicus.eu",
    "https://ads-beta.atmosphere.copernicus.eu": "https://ads.atmosphere.copernicus.eu",
    "http://ads-beta.atmosphere.copernicus.eu": "https://ads.atmosphere.copernicus.eu",
    "https://cds-beta.climate.copernicus.eu": "https://cds.climate.copernicus.eu",
    "http://cds-beta.climate.copernicus.eu": "https://cds.climate.copernicus.eu",
    "https://ewds-beta.climate.copernicus.eu": "https://ewds.climate.copernicus.eu",
    "http://ewds-beta.climate.copernicus.eu": "https://ewds.climate.copernicus.eu",
    "https://datastore.copernicus-climate.eu": "https://dast.copernicus-climate.eu",
    "http://datastore.copernicus-climate.eu": "https://dast.copernicus-climate.eu",
    "https://dast.data.compute.cci2.ecmwf.int": "https://dast.copernicus-climate.eu",
    "http://dast.data.compute.cci2.ecmwf.int": "https://dast.copernicus-climate.eu",
    # DOIs
    "/agupubs.onlinelibrary.wiley.com/doi/": "/doi.org/",
    "/aslopubs.onlinelibrary.wiley.com/doi/pdf/": "/doi.org/",
    "/rmets.onlinelibrary.wiley.com/doi/full/": "/doi.org/",
    "/rmets.onlinelibrary.wiley.com/doi/": "/doi.org/",
    "/dx.doi.org/": "/doi.org/",
    "/link.springer.com/article/": "/doi.org/",
    "/iopscience.iop.org/article/": "/doi.org/",
    "www.science.org/doi/": "doi.org/",
    "www.nature.com/articles/": "doi.org/10.1038/",
    "http://doi.org": "https://doi.org",
    # URLs
    (
        "https://ec.europa.eu/eurostat/web/gisco/geodata/reference-data"
        "/administrative-units-statistical-units/nuts"
    ): "https://ec.europa.eu/eurostat/web/nuts",
}

ADMONITION_TITLE = "These are the key outcomes of this assessment"

CLASS_NOTE = ":class: note"
URL_PATTERN = r"https?://[^\s)]+"
COPERNICUS_ARTICLE_PATTERN = re.compile(
    r"https?://([a-z]+)\.copernicus\.org/articles/"
    r"(\d+)/(\d+)/(\d+)/"
    r"(?:[^)\s/]+)?"
)


def copernicus_to_doi(text: str) -> tuple[str, bool]:
    """Convert copernicus.org URLs to DOI."""
    # subn: Make changes, return number of changes
    new_text, n = COPERNICUS_ARTICLE_PATTERN.subn(
        lambda m: (
            f"https://doi.org/10.5194/"
            f"{m.group(1)}-{m.group(2)}-{m.group(3)}-{m.group(4)}"
        ),
        text,
    )
    return new_text, n > 0


def fix_template_divergences(path: Path) -> None:
    notebook = nbformat.read(path, nbformat.NO_CONVERT)

    write = False
    for cell in notebook.cells:
        if cell["cell_type"] != "markdown":
            continue

        for url in set(re.findall(URL_PATTERN, cell["source"])):
            if url.endswith("."):
                cell["source"] = cell["source"].replace(url, url.rstrip("."))
                write = True

        if ")=\n\n" in (source := cell["source"]):
            cell["source"] = source.replace(")=\n\n", ")=\n")
            write = True

        for old, new in STRING_MAPPER.items():
            if old in (source := cell.get("source", "")):
                cell["source"] = source.replace(old, new)
                write = True

        cell["source"], copernicus_changed = copernicus_to_doi(cell["source"])
        if copernicus_changed:
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
