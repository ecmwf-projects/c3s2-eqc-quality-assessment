# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "nbformat",
#     "requests",
#     "requests-cache",
# ]
# ///

import argparse
import collections
import re
import sys
from pathlib import Path

import nbformat
import requests
import requests_cache

# Matches https://doi.org/ URLs while including balanced inner parentheses
# and trimming trailing punctuation or outer wrapping parens.
DOI_PATTERN = r"https://doi\.org/(?:[^\s()]+|\([^\s()]*\))+(?<=[^\s.,?!:;\)])"


def find_dois_in_notebook(path: Path, verbose: bool) -> set[str]:
    if verbose:
        print(f"Scanning {path}...")

    notebook = nbformat.read(path, nbformat.NO_CONVERT)
    markdown_cells = [
        cell for cell in notebook.cells if cell["cell_type"] == "markdown"
    ]
    return {
        url
        for cell in markdown_cells
        for url in re.findall(DOI_PATTERN, cell.get("source", ""))
    }


def find_broken_dois(dois: list[str], verbose: bool) -> dict[str, str]:
    broken_dois = {}
    for doi in dois:
        if verbose:
            print(f"Verifying DOI: {doi} ...", end=" ", flush=True)

        status_code = None
        try:
            response = requests.get(
                doi,
                headers={"Accept": "text/x-bibliography"},
                allow_redirects=True,
            )
            status_code = response.status_code
            response.raise_for_status()
        except Exception as e:
            broken_dois[doi] = str(e)

        if verbose:
            print(f"[{status_code}]")
    return broken_dois


def main(paths: list[Path], expire_after: int, verbose: bool) -> None:
    requests_cache.install_cache(".validate-dois", expire_after=expire_after)

    dois_mapper = collections.defaultdict(list)
    for path in paths:
        for doi in find_dois_in_notebook(path, verbose):
            dois_mapper[doi].append(str(path))

    broken_dois = find_broken_dois(sorted(dois_mapper), verbose)

    if broken_dois:
        print("\n--- DOI Verification Failed ---", file=sys.stderr)
        for doi, error in broken_dois.items():
            sources = "\n  - ".join(sorted(dois_mapper[doi]))
            print(
                f"\nDOI: {doi}\nError: {error}\nFound in:\n  - {sources}",
                file=sys.stderr,
            )
        sys.exit(1)

    print("\nAll DOIs verified successfully!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", action="store", type=Path, nargs="*")
    parser.add_argument(
        "--expire-after",
        type=int,
        default=86400,
        help="Cache expiration time in seconds (default: 86400).",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Increase output verbosity."
    )
    args = parser.parse_args()
    main(args.paths, args.expire_after, args.verbose)
