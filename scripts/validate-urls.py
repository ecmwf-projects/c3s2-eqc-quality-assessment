import argparse
import re
from pathlib import Path

import nbformat
import requests

USER_AGENT = (
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36"
    " (KHTML, like Gecko)"
    " Chrome/131.0.0.0 Safari/537.36"
)

KNOWN_SSL_ISSUES = ("https://www.cnr.it/",)


def validate_urls(path: Path) -> None:
    notebook = nbformat.read(path, nbformat.NO_CONVERT)

    for cell in notebook.cells:
        if cell["cell_type"] != "markdown":
            continue

        source = cell.get("source", "")
        for url in set(re.findall(r"\(\s*(http[^)]*?)\s*\)", source)):
            url = url.replace("https://doi.org/", "https://api.crossref.org/works/")

            try:
                response = requests.head(url, allow_redirects=True)
                match response.status_code:
                    case 403:
                        response = requests.head(
                            url,
                            allow_redirects=True,
                            headers={"User-Agent": USER_AGENT},
                        )
                    case 404 | 405:
                        response = requests.get(url, allow_redirects=True)
                response.raise_for_status()
            except requests.exceptions.SSLError:
                if not url.startswith(KNOWN_SSL_ISSUES):
                    raise
            except Exception as exc:
                raise RuntimeError(f"{path=!s}: Invalid {url=}") from exc


def main(paths: list[Path]) -> None:
    for path in paths:
        validate_urls(path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", action="store", type=Path, nargs="*")
    args = parser.parse_args()
    main(args.paths)
