"""Open or update the issue that lists the broken links found by the link check.

Usage: report-broken-links.py LYCHEE_JSON

Reads the JSON report of lychee, as run by the weekly link check, and lists each broken
link once per file. If the bot's issue from a previous run is still open, only the links
missing from it are appended, so edits and ticked items are kept.
Fails when the report lists no broken links, or has entries it can't parse, such as
files that lychee couldn't read, as the link check then failed for another reason or
would drop some broken links.
Needs GH_TOKEN and GITHUB_REPOSITORY in the environment.
"""

import json
import os
import re
import subprocess
import sys

BOT = "github-actions[bot]"
MARKER = "<!-- report-broken-links -->"
TITLE = "Broken links in notebooks"
URL = re.compile(r"https?://[^\s`<>]+")
FILE = re.compile(r"[\w./-]+\.(?:ipynb|md)")


def broken_links(report: str) -> tuple[dict[str, str], int]:
    """Map each entry to the error of its link, and count the unparsed entries."""
    with open(report) as file:
        results = json.load(file)
    links: list[tuple[str, str]] = []
    messages: dict[str, str] = {}
    errors = 0
    for path, items in [*results["error_map"].items(), *results["timeout_map"].items()]:
        for item in items:
            url, status = item.get("url", ""), item.get("status", {})
            if not URL.fullmatch(url) or not FILE.fullmatch(path):
                print(f"Can't parse broken link of {path}: {item}", file=sys.stderr)
                errors += 1
                continue
            links.append((url, path))
            # Later files with the same link only get "Error (cached)"
            if not status.get("text", "").endswith("(cached)"):
                message = status.get("details") or status.get("text", "")
                messages.setdefault(url, " ".join(message.split()))
    entries = {
        f"{url} in `{path}`": messages.get(url, "Error").replace("`", "'")[:300]
        for url, path in sorted(links)
    }
    return entries, errors


def gh(*args: str) -> str:
    return subprocess.run(
        ["gh", "api", *args], check=True, capture_output=True, text=True
    ).stdout


def main() -> None:
    entries, errors = broken_links(sys.argv[1])
    repo = os.environ["GITHUB_REPOSITORY"]
    issues = [
        json.loads(line)
        for line in gh(
            "--paginate", f"repos/{repo}/issues?state=open", "--jq", ".[]"
        ).splitlines()
    ]
    issue = next(
        (
            issue
            for issue in issues
            if "pull_request" not in issue
            and issue["user"]["login"] == BOT
            and MARKER in (issue["body"] or "")
        ),
        None,
    )
    body = issue["body"] if issue else ""
    new = [
        f"- [ ] {entry}: `{error}`"
        for entry, error in sorted(entries.items())
        if entry not in body
    ]

    if not new:
        print("No new broken links")
    elif issue:
        body = body.rstrip() + "\n" + "\n".join(new) + "\n"
        gh(
            "-X",
            "PATCH",
            f"repos/{repo}/issues/{issue['number']}",
            "-f",
            f"body={body}",
        )
        print(f"Added {len(new)} broken links to {issue['html_url']}")
    else:
        workflow = (
            f"{os.environ['GITHUB_SERVER_URL']}/{repo}/actions/workflows/weekly.yml"
        )
        body = "\n".join(
            [
                MARKER,
                "The [weekly checks](" + workflow + ") found these broken links,"
                " and add any new ones here while this issue is open.",
                "Fix them, or ignore links that only fail in CI with"
                " `exclude` in `lychee.toml`.",
                "",
                *new,
                "",
            ]
        )
        url = gh(f"repos/{repo}/issues", "-f", f"title={TITLE}", "-f", f"body={body}")
        print(f"Reported {len(new)} broken links in {json.loads(url)['html_url']}")

    if not entries or errors:
        sys.exit(
            f"The link check failed with {errors} errors and {len(entries)} broken links"
        )


if __name__ == "__main__":
    main()
