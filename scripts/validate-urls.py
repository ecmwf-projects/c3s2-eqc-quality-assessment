import argparse
import re
from pathlib import Path

import nbformat
import requests
import truststore

truststore.inject_into_ssl()

USER_AGENT = (
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36"
    " (KHTML, like Gecko)"
    " Chrome/131.0.0.0 Safari/537.36"
)

KNOWN_SSL_ISSUES = (
    "https://apps.climate.copernicus.eu",
    "https://pulse.climate.copernicus.eu",
    "https://thermaltrace.climate.copernicus.eu",
    "https://www.cnr.it",
    "https://hermes.acri.fr",
    "https://alt-perubolivia.org",
    "https://web.unisa.it",
)

KNOWN_403_ISSUES = (
    "https://www.iea.org",
    "https://web.unisa.it",
)

ARROW = "    ->"
CROSSREF_URL = "https://api.crossref.org/works/"
URL_PATTERN = r"https?://(?:[^\s()]+|\([^\s()]*\))+"  # Allow pairs of brackets in link


def find_urls(notebook: nbformat.NotebookNode) -> list[str]:
    """Find all unique URLs in the given notebook."""
    markdown_cells = [
        cell for cell in notebook.cells if cell["cell_type"] == "markdown"
    ]
    unique_urls = {
        url
        for cell in markdown_cells
        for url in re.findall(URL_PATTERN, cell.get("source", ""))
    }
    return sorted(unique_urls)


def validate_url(url: str, *, verbose: bool = False) -> Exception | None:
    """Validate a single URL, checking for HTTP status and SSL errors."""
    result: Exception | requests.exceptions.SSLError | None
    if verbose:
        url_orig = url  # Copy so can be reused later
        print(url)

    url = url.replace("https://doi.org/", CROSSREF_URL)
    if verbose:
        if url != url_orig:  # If url has been changed
            print(ARROW, url)

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
                if url.startswith(CROSSREF_URL):
                    url = url.rstrip("/") + "/agency"
                response = requests.get(url, allow_redirects=True)

        if verbose:
            print(ARROW, response.status_code)

        if response.status_code == 429 or (
            response.status_code == 403 and url.startswith(KNOWN_403_ISSUES)
        ):
            if verbose:
                print(
                    ARROW,
                    "Too many requests (429) or known forbidden (403) page, allowing exception.",
                )

        # Raise Exception corresponding to HTTP status
        response.raise_for_status()

    except requests.exceptions.SSLError as exc:
        result = exc
        if verbose:
            print(ARROW, "SSLError")

        if url.startswith(KNOWN_SSL_ISSUES):
            result = None
            if verbose:
                print(ARROW, "Known SSL issue, allowing exception.")

    except Exception as exc:
        result = exc
        if verbose:
            print(ARROW, exc)

    else:
        result = None

    finally:
        return result


def validate_urls(path: Path, *, verbose: bool = False) -> None:
    notebook = nbformat.read(path, nbformat.NO_CONVERT)

    # Process all unique URLs, remove Nones
    exceptions = {
        url: validate_url(url, verbose=verbose) for url in find_urls(notebook)
    }
    exceptions = {url: exc for url, exc in exceptions.items() if exc}

    if exceptions:
        raise RuntimeError(
            "\n\n".join(
                [f"Invalid URLs in {path=!s}"]
                + [f"{url=}\n{exc!s}" for url, exc in exceptions.items()]
            )
        )
    else:  # No exceptions
        if verbose:
            print("--- No errors found ✓ ---")


def main(paths: list[Path], verbose: bool = False) -> None:
    for path in paths:
        if verbose:
            print("\n---", path, "---")
        validate_urls(path, verbose=verbose)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", action="store", type=Path, nargs="*")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Print URLs as they are checked."
    )
    args = parser.parse_args()
    main(args.paths, verbose=args.verbose)
