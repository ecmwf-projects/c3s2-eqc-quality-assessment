import argparse
import base64
import functools
import hashlib
import re
from pathlib import Path

import nbformat
import nbformat.v4

LOGO_NAME = "logoline_c3s.svg"
MANDATORY_TAGS: dict[str, set[str]] = {"code": {"hide-input"}}
README_PATH = Path("./README.md")
GLUE_PNG_MIME = "application/papermill.record/image/png"
GLUE_FIGURE_PATTERN = re.compile(
    r"^(\s*(?:`{3,}|:{3,})\{)glue:figure\}[ \t]+(\S+)", re.M
)
# MyST turns empty HTML anchors into links without a URL (nothing links to them),
# and <center> into a paragraph
EMPTY_ANCHOR_PATTERN = re.compile(r"<a\s+id=(['\"])[^'\"]*\1\s*>\s*</a>")
CENTER_PATTERN = re.compile(r"<center>(.*?)</center>", re.I | re.S)
CENTERED_SPAN = r'<span style="display: block; text-align: center">\1</span>'
# MyST ignores labels that do not match its target syntax
MYST_LABEL_PATTERN = re.compile(r"[a-zA-Z0-9|@<>*./_\-+:]{1,100}")


@functools.cache
def get_disclaimer(readme: Path) -> str:
    lines = readme.open()
    disclaimer = [":::{warning}"]
    for line in lines:
        if line.startswith("> [!WARNING]"):
            for line in lines:
                if line.startswith(">"):
                    disclaimer.append(line.removeprefix(">").strip())
                else:
                    break
    disclaimer.append(":::")
    return "\n".join(disclaimer)


def add_header(notebook: nbformat.NotebookNode, path: Path, root: Path) -> None:
    logo_path = "../" * len(path.parent.relative_to(root).parts) + LOGO_NAME
    header = [f"![logo]({logo_path})"]
    # MyST moves the title above the page, and only removes it if it comes first
    for index, cell in enumerate(notebook.cells):
        lines = cell["source"].splitlines() if cell["cell_type"] == "markdown" else []
        if title := next((line for line in lines if line.startswith("# ")), None):
            lines.remove(title)
            cell["source"] = "\n".join(lines)
            if not cell["source"].strip():
                del notebook.cells[index]
            header.insert(0, title)
            break
    notebook.cells.insert(0, nbformat.v4.new_markdown_cell("\n\n".join(header)))


def add_tags(cell: nbformat.NotebookNode) -> None:
    tags = set(cell["metadata"].get("tags", []))
    mandatory_tags = MANDATORY_TAGS.get(cell["cell_type"], set())
    if cell["cell_type"] == "code" and not cell["outputs"]:
        # MyST would show an empty dropdown
        tags.discard("hide-output")
    cell["metadata"]["tags"] = list(tags | mandatory_tags)


def check_file_name(name: str, path: Path) -> None:
    # File names come from the notebook, so keep the files inside its directory
    if name in {"", ".", ".."} or Path(name).name != name:
        raise ValueError(f"{path}: invalid file name {name!r}")


def write_file(content: bytes, target: Path, path: Path) -> None:
    if target.exists() and target.read_bytes() != content:
        raise ValueError(f"{path}: {target.name!r} would overwrite {target}")
    target.write_bytes(content)


def decode_attachments(cell: nbformat.NotebookNode, path: Path) -> None:
    attachments = cell.pop("attachments", {})
    for name, data in attachments.items():
        check_file_name(name, path)
        cell["source"] = cell["source"].replace(f"attachment:{name}", f"{name}")
        if not data:
            continue
        # An attachment can carry several MIME representations; the last one wins
        write_file(base64.b64decode(list(data.values())[-1]), path.parent / name, path)


def extract_glue_figures(notebook: nbformat.NotebookNode, path: Path) -> dict[str, str]:
    """Save the PNG figures glued with myst-nb, as MyST cannot read glued outputs."""
    figures = {}
    for cell in notebook.cells:
        if "outputs" not in cell:
            continue
        outputs = []
        for output in cell["outputs"]:
            name = output.get("metadata", {}).get("scrapbook", {}).get("name")
            if name is None:
                outputs.append(output)
            elif (data := output.get("data", {}).get(GLUE_PNG_MIME)) is not None:
                check_file_name(f"{name}.png", path)
                write_file(base64.b64decode(data), path.parent / f"{name}.png", path)
                figures[name] = f"{name}.png"
        cell["outputs"] = outputs
    return figures


def replace_glue_figures(
    cell: nbformat.NotebookNode, figures: dict[str, str], path: Path
) -> None:
    def replace(match: re.Match[str]) -> str:
        if match.group(2) not in figures:
            raise ValueError(f"{path}: no glued image named {match.group(2)!r}")
        return f"{match.group(1)}figure}} {figures[match.group(2)]}"

    if cell["cell_type"] == "markdown":
        cell["source"] = GLUE_FIGURE_PATTERN.sub(replace, cell["source"])


def replace_unsupported_html(cell: nbformat.NotebookNode) -> None:
    if cell["cell_type"] == "markdown":
        source = EMPTY_ANCHOR_PATTERN.sub("", cell["source"])
        cell["source"] = CENTER_PATTERN.sub(CENTERED_SPAN, source)


def make_cell_ids_unique(
    notebook: nbformat.NotebookNode, path: Path, root: Path
) -> None:
    # MyST uses cell IDs as identifiers, which must be unique across the book
    prefix = hashlib.sha1(str(path.relative_to(root)).encode()).hexdigest()[:8]
    for index, cell in enumerate(notebook.cells):
        if "id" in cell:
            cell["id"] = f"{prefix}-{index}"


def namespace_label(label: str, stem: str) -> str:
    # Labels are shared by the whole book; some notebooks already use namespaced labels
    label = label.removeprefix(f"{stem}:")
    namespaced = f"{stem}:{label}"
    if len(namespaced) > 100:
        namespaced = f"{hashlib.sha1(stem.encode()).hexdigest()[:8]}:{label}"
    if not MYST_LABEL_PATTERN.fullmatch(namespaced):
        raise ValueError(f"{stem}: invalid section label {label!r}")
    return namespaced


def add_disclaimer(notebook: nbformat.NotebookNode) -> None:
    disclaimer = get_disclaimer(README_PATH)
    cell = nbformat.v4.new_markdown_cell(disclaimer, metadata={"tags": ["disclaimer"]})
    notebook.cells.insert(0, cell)


def edit_section_references(notebook: nbformat.NotebookNode, path: Path) -> None:
    references = {}
    for cell in notebook.cells:
        if "source" not in cell:
            continue

        lines: list[str] = []
        for line in cell["source"].splitlines():
            if line.strip().startswith("(") and line.strip().endswith(")="):
                old_reference = line.strip()[1:-2]
                new_reference = namespace_label(old_reference, path.stem)
                references[old_reference] = new_reference
                line = line.replace(f"({old_reference})=", f"({new_reference})=")
            lines.append(line)
        cell["source"] = "\n".join(lines)

    for cell in notebook.cells:
        if "source" not in cell:
            continue

        for old_reference, new_reference in references.items():
            for link in (f"]({old_reference})", f"](#{old_reference})"):
                cell["source"] = cell["source"].replace(link, f"](#{new_reference})")


def convert_notebook(path: Path, root: Path, disclaimer: bool) -> None:
    notebook = nbformat.read(path, nbformat.NO_CONVERT)

    if disclaimer:
        add_disclaimer(notebook)
    add_header(notebook, path, root)
    glue_figures = extract_glue_figures(notebook, path)

    for cell in notebook.cells:
        add_tags(cell)
        decode_attachments(cell, path)
        replace_glue_figures(cell, glue_figures, path)
        replace_unsupported_html(cell)

    edit_section_references(notebook, path)
    make_cell_ids_unique(notebook, path, root)

    nbformat.write(notebook, path)


def main(path: Path, disclaimer: bool) -> None:
    for notebook_path in path.glob("**/*.ipynb"):
        convert_notebook(path=notebook_path, root=path, disclaimer=disclaimer)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--disclaimer", action=argparse.BooleanOptionalAction)
    args = parser.parse_args()
    main(path=args.path, disclaimer=args.disclaimer)
