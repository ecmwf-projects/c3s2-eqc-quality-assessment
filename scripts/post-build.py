"""Redirect the Jupyter Book 1 page URLs to the pages built by Jupyter Book 2.

Jupyter Book 1 published `Path/To/notebook.html`, which the CDS and other sites link
to. MyST derives shorter, lowercase URLs from the file names instead.
"""

import argparse
import html
import json
import os
from pathlib import Path

REDIRECT = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Redirecting…</title>
<link rel="canonical" href="{url}">
<meta http-equiv="refresh" content="0; url={url}">
<script>location.replace({url_js} + location.search + location.hash)</script>
</head>
<body><a href="{url}">Redirecting…</a></body>
</html>
"""


def write_redirects(html_dir: Path) -> None:
    for page_path in html_dir.glob("*.json"):
        page = json.loads(page_path.read_text())
        if not isinstance(page, dict) or "location" not in page:
            continue
        old = html_dir / Path(page["location"].lstrip("/")).with_suffix(".html")
        new = html_dir / (
            "" if page["slug"] == "index" else page["slug"].replace(".", "/")
        )
        if old.exists():
            raise FileExistsError(f"{old} would overwrite a page")
        url = os.path.relpath(new, old.parent) + "/"
        old.parent.mkdir(parents=True, exist_ok=True)
        old.write_text(REDIRECT.format(url=html.escape(url), url_js=json.dumps(url)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("html_dir", type=Path)
    args = parser.parse_args()
    write_redirects(args.html_dir)
