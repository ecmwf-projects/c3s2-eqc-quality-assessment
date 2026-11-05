#!/usr/bin/env python3
"""Print the Markdown of a notebook, for lychee to find its links.

lychee runs this on each file (see `preprocess` in lychee.toml) and scans the output of
notebooks as plain text, as it can't parse them. Code blocks, code spans and HTML
comments are dropped, as they aren't rendered as links, and character references and
backslash escapes are decoded, as plain text extraction would keep them in the URLs.
Markdown files are printed unchanged, as lychee parses them itself.
"""

import html
import json
import re
import sys

FENCE = re.compile(r" {0,3}(`{3,}|~{3,})(.*)")
COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
# Not the content of MyST roles, such as {ref}`label`
CODE_SPAN = re.compile(r"(?<![`}])(`+)(?!`).+?(?<!`)\1(?!`)")
REFERENCE = re.compile(
    r"&(?:#[0-9]{1,7}|#[xX][0-9a-fA-F]{1,6}|[A-Za-z][A-Za-z0-9]{1,31});"
)
ESCAPE = re.compile(r"\\([!-/:-@\[-`{-~])")


def read_markdown(path: str) -> str:
    with open(path, encoding="utf-8") as file:
        cells = json.load(file)["cells"]
    return "\n\n".join(
        "".join(cell["source"]) for cell in cells if cell["cell_type"] == "markdown"
    )


def closes(match: re.Match[str], fence: str) -> bool:
    return (
        match[1][0] == fence[0] and len(match[1]) >= len(fence) and not match[2].strip()
    )


def drop_code_blocks(markdown: str) -> str:
    """Drop fenced code blocks, but keep MyST directives such as ```{note}."""
    lines = []
    directives: list[str] = []
    code_block: str | None = None
    for line in markdown.splitlines():
        match = FENCE.fullmatch(line)
        if code_block is not None:
            if match and closes(match, code_block):
                code_block = None
            continue
        if match:
            if match[2].strip().startswith("{"):
                directives.append(match[1])
            elif directives and closes(match, directives[-1]):
                directives.pop()
            else:
                code_block = match[1]
                continue
        lines.append(line)
    return "\n".join(lines)


def main(path: str) -> None:
    if not path.endswith(".ipynb"):
        with open(path, encoding="utf-8") as file:
            print(file.read(), end="")
        return
    text = COMMENT.sub(" ", drop_code_blocks(read_markdown(path)))
    text = CODE_SPAN.sub(" ", text)
    text = REFERENCE.sub(lambda match: html.unescape(match[0]), text)
    print(ESCAPE.sub(r"\1", text))


if __name__ == "__main__":
    main(sys.argv[1])
