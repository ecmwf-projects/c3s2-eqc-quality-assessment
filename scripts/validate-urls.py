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

CROSSREF_URL = "https://api.crossref.org/works/"
URL_PATTERN = r"https?://(?:[^\s()]+|\([^\s()]*\))+"  # Allow pairs of brackets in link


def validate_urls(path: Path, *, verbose: bool = False) -> None:
    notebook = nbformat.read(path, nbformat.NO_CONVERT)

    exceptions: dict[str, Exception] = {}
    for cell in notebook.cells:
        if cell["cell_type"] != "markdown":
            continue

        source = cell.get("source", "")
        for url in set(re.findall(URL_PATTERN, source)):
            if verbose:
                url_orig = url  # Copy so can be reused later
                print(url)

            url = url.replace("https://doi.org/", CROSSREF_URL)
            if verbose:
                if url != url_orig:  # If url has been changed
                    print("    ->", url)

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
                    print("    ->", response.status_code)

                if response.status_code == 429 or (
                    response.status_code == 403 and url.startswith(KNOWN_403_ISSUES)
                ):
                    continue
                response.raise_for_status()

            except requests.exceptions.SSLError as exc:
                if not url.startswith(KNOWN_SSL_ISSUES):
                    exceptions[url] = exc

            except Exception as exc:
                exceptions[url] = exc

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
