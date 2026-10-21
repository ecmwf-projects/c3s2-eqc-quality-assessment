"""Summarise pre-commit logs as markdown for the job summary and the pull request.

Usage: qa-summary.py LABEL=PATH [LABEL=PATH ...]

Prints one table with a row per hook and a column per log, followed by the end of the
output of every failed hook. The logs are controlled by the pull request author, so
everything taken from them is escaped or fenced and the output is capped in size.
"""

import html
import os
import re
import sys
from pathlib import Path

MAX_LINES, MAX_CHARS, MAX_BYTES = 40, 300, 60_000
ANSI = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]")
# Same lines as `(.+?)\.{3,}(\(no files to check\))?(Passed|Failed|Skipped)`, but the
# greedy name keeps matching linear on long runs of dots
STATUS = re.compile(
    r"(?P<name>.*[^.])\.{3,}(?:\(no files to check\))?(?P<status>Passed|Failed|Skipped)"
)
# The diff printed by --show-diff-on-failure follows these lines; it stays in the job log
END = {"pre-commit hook(s) made changes.", "All changes made by hooks:"}
HOOK_ID = re.compile(r"- hook id: (.+)")
MODIFIED = "- files were modified by this hook"
BOOKKEEPING = re.compile(rf"- (?:hook id: .+|exit code: \d+|duration: .*)|{MODIFIED}")
CELLS = {"Passed": "Passed", "Failed": "**Failed**", "Skipped": "Skipped"}
TRUNCATED = "\nOutput truncated, see the job log.\n\n"
FOOTER = (
    "Reproduce locally with `make qa`. Hooks that modify files have already fixed"
    " them: review and commit the changes.\n"
)
# Scheduled and manual runs check every file and leave nothing to commit
FOOTER_ALL_FILES = "Reproduce locally with `make qa-all`.\n"


def read(path: Path) -> str | None:
    try:
        text = path.read_bytes().decode(errors="replace")
    except OSError:
        return None
    return ANSI.sub("", text).replace("\r\n", "\n").replace("\r", "")


def parse(text: str) -> tuple[dict[str, str], dict[str, list[str]]]:
    """Return the status of every hook and the output of the failed ones."""
    statuses: dict[str, str] = {}
    outputs: dict[str, list[str]] = {}
    output = None
    # Known limitation: a hook can print a line that looks like a status or an end
    # line, which adds or hides rows here. It cannot change the result of the job.
    for line in text.split("\n"):
        if line in END:
            break
        if match := STATUS.fullmatch(line):
            name, status = match["name"], match["status"]
            if statuses.get(name) != "Failed":
                statuses[name] = status
            output = outputs.setdefault(name, []) if status == "Failed" else None
        elif output is not None:
            output.append(line)
    return statuses, outputs


def cell(text: str) -> str:
    return html.escape(text).replace("\\", "\\\\").replace("|", "\\|")


def excerpt(lines: list[str]) -> str:
    """Fence the last lines so that nothing in them can close the code block."""
    lines = "\n".join(lines).strip("\n").split("\n")
    shown = [line[:MAX_CHARS] for line in lines[-MAX_LINES:]]
    backticks = max(map(len, re.findall("`+", "\n".join(shown))), default=0)
    fence = "`" * max(3, backticks + 1)
    omitted = len(lines) - len(shown)
    note = f"{omitted} earlier lines omitted\n\n" if omitted else ""
    return f"{note}{fence}text\n" + "\n".join(shown) + f"\n{fence}\n"


def main(args: list[str]) -> None:
    logs = {}
    for arg in args:
        label, _, path = arg.partition("=")
        logs[label] = read(Path(path))
    parsed = {label: parse(text or "") for label, text in logs.items()}

    title = "QA checks"
    run = [
        os.environ.get(f"GITHUB_{key}")
        for key in ("SERVER_URL", "REPOSITORY", "RUN_ID")
    ]
    if all(run):
        title = "[{3}]({0}/{1}/actions/runs/{2})".format(*run, title)
    chunks = [f"### {title}\n\n"]

    names = dict.fromkeys(name for statuses, _ in parsed.values() for name in statuses)
    if names:
        chunks.append(f"| Check | {' | '.join(map(cell, parsed))} |\n")
        chunks.append(f"|{' --- |' * (len(parsed) + 1)}\n")
    for name in names:
        row = [CELLS.get(parsed[label][0].get(name, ""), "–") for label in parsed]
        chunks.append(f"| {cell(name)} | {' | '.join(row)} |\n")
    if names:
        chunks.append("\n")

    failed = False
    for name in names:
        for label, (_, outputs) in parsed.items():
            if (output := outputs.get(name)) is None:
                continue
            failed = True
            ids = [match[1] for line in output if (match := HOOK_ID.fullmatch(line))]
            summary = f"{name} ({ids[0]}) – {label}" if ids else f"{name} – {label}"
            note = "This hook modified files.\n\n" if MODIFIED in output else ""
            body = excerpt([line for line in output if not BOOKKEEPING.fullmatch(line)])
            # The blank lines make GitHub render the content as markdown again
            chunks.append(
                f"<details><summary>{html.escape(summary)}</summary>\n\n"
                f"{note}{body}\n</details>\n\n"
            )
    # pre-commit crashed or rejected its configuration
    for label, text in logs.items():
        if text and text.strip() and not parsed[label][0]:
            failed = True
            lines = text.split("\n")
            chunks.append(
                f"pre-commit reported no hook results for {cell(label)}:\n\n"
                f"{excerpt(lines)}\n"
            )
    pull_request = os.environ.get("GITHUB_EVENT_NAME", "pull_request") == "pull_request"
    failed_footer = FOOTER if pull_request else FOOTER_ALL_FILES
    footer = (
        failed_footer if failed else "All checks passed.\n" if names else "Not run.\n"
    )

    # Only whole chunks are written, so a fence or a character is never cut
    budget = MAX_BYTES - len(TRUNCATED.encode()) - len(footer.encode())
    out = b""
    for chunk in chunks:
        # A marker of pr-comment.sh in the body would let another comment overwrite it
        data = chunk.replace("<!--", "<!- -").encode()
        if len(out) + len(data) > budget:
            out += TRUNCATED.encode()
            break
        out += data
    sys.stdout.buffer.write(out + footer.encode())


if __name__ == "__main__":
    main(sys.argv[1:])
