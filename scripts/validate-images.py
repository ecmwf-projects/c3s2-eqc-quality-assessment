# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "nbformat",
#     "requests",
# ]
# ///

"""Check that the external images of notebooks are still served as images.

An image that moved upstream can redirect to an HTML page instead of failing, which the
link check accepts. Failed requests are left to the link check.
"""

import argparse
import collections
import html
import re
import sys
from pathlib import Path

import nbformat
import requests

IMAGE_PATTERNS = (
    # ![alt](url)
    re.compile(r"!\[(?:[^\[\]]|\[[^\[\]]*\])*\]\(\s*<?(https?://[^\s<>)]+)"),
    # <img src="url">
    re.compile(r"<img\b[^>]*?\bsrc\s*=\s*[\"'](https?://[^\"']+)[\"']", re.IGNORECASE),
    # ```{image} url and ```{figure} url
    re.compile(
        r"^ {0,3}(?:`{3,}|~{3,}|:{3,})\s*\{(?:image|figure)\}\s+(https?://\S+)",
        re.MULTILINE,
    ),
)
# Browsers also render images served as generic binary data
BINARY_TYPES = {"application/octet-stream", "binary/octet-stream"}


def find_images_in_notebook(path: Path) -> set[str]:
    notebook = nbformat.read(path, nbformat.NO_CONVERT)
    return {
        html.unescape(url)
        for cell in notebook.cells
        if cell["cell_type"] == "markdown"
        for pattern in IMAGE_PATTERNS
        for url in pattern.findall(cell.get("source", ""))
    }


def check_image(url: str) -> str | None:
    try:
        response = requests.get(url, timeout=60, stream=True)
        response.close()
    except requests.RequestException:
        return None
    if not response.ok:
        return None

    content_type = response.headers.get("Content-Type", "")
    media_type = content_type.split(";", 1)[0].strip().lower()
    if media_type.startswith("image/") or media_type in BINARY_TYPES:
        return None
    error = f"Not an image: {media_type or 'no Content-Type'}"
    if response.history:
        error += f" (redirected to {response.url})"
    return error


def main(paths: list[Path]) -> None:
    images_mapper = collections.defaultdict(list)
    for path in paths:
        for url in find_images_in_notebook(path):
            images_mapper[url].append(str(path))

    broken_images = {
        url: error
        for url in sorted(images_mapper)
        if (error := check_image(url)) is not None
    }

    if broken_images:
        print("\n--- Image Verification Failed ---", file=sys.stderr)
        for url, error in broken_images.items():
            sources = "\n  - ".join(sorted(images_mapper[url]))
            print(
                f"\nImage: {url}\nError: {error}\nFound in:\n  - {sources}",
                file=sys.stderr,
            )
        sys.exit(1)

    print(f"\nAll {len(images_mapper)} external images verified successfully!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", action="store", type=Path, nargs="*")
    args = parser.parse_args()
    main(args.paths)
