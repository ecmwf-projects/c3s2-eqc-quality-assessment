"""Remove the notebooks a pull request preview doesn't need.

Keeps the notebooks listed in $CHANGED_NOTEBOOKS (one per line), the templates and
every notebook they link to or cross-reference, so the preview only renders what the
pull request touches while all its references still resolve.
"""

import json
import os
import re
import subprocess
from pathlib import Path

LINK = re.compile(r"\]\((?!https?://)([^)\s#]+\.ipynb)")
ROLE = re.compile(r"\{(?:ref|numref)\}`([^`]*)`")


def read_sources(path: Path) -> str:
    cells = json.loads(path.read_text())["cells"]
    return "\n".join(
        "".join(cell["source"]) + json.dumps(cell["metadata"]) for cell in cells
    )


def role_target(content: str) -> str:
    match = re.search(r"<([^>]+)>\s*$", content)
    return (match.group(1) if match else content).strip()


def references(path: Path, sources: dict[Path, str]) -> set[Path]:
    found = set()
    for link in LINK.findall(sources[path]):
        target = Path(os.path.normpath(path.parent / link))
        if target in sources:
            found.add(target)
    # Labels can be defined in other notebooks; keep any notebook defining the label
    for content in ROLE.findall(sources[path]):
        label = role_target(content)
        found |= {
            other
            for other, text in sources.items()
            if other != path and label in ROLE.sub("", text)
        }
    return found


def main() -> None:
    listed = subprocess.run(
        ["git", "ls-files", "-z", "--", "*.ipynb"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    sources = {
        Path(name): read_sources(Path(name)) for name in listed.split("\0") if name
    }
    changed = os.environ.get("CHANGED_NOTEBOOKS", "").splitlines()
    keep = {Path(name) for name in changed if Path(name) in sources}
    queue = list(keep)
    while queue:
        for reference in references(queue.pop(), sources) - keep:
            keep.add(reference)
            queue.append(reference)

    for path in sources:
        if path not in keep and path.parts[0] != "templates":
            path.unlink()
    print("Kept notebooks:", *sorted(map(str, keep)), sep="\n  ")


if __name__ == "__main__":
    main()
