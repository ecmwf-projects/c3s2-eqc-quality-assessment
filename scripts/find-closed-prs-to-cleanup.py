#!/usr/bin/env python3
import argparse

from github import Github

REPO_NAME = "ecmwf-projects/c3s2-eqc-quality-assessment"


def main(token: str | None = None) -> None:
    gh = Github(login_or_token=token)
    repo = gh.get_repo(REPO_NAME)

    prs_to_cleanup = []
    for content in repo.get_contents("pr-preview", ref="gh-pages"):
        if content.type != "dir" or not content.name.startswith("pr-"):
            continue
        pr = repo.get_pull(int(content.name.replace("pr-", "")))
        if pr.state == "closed":
            prs_to_cleanup.append(content.name)

    if prs_to_cleanup:
        print(f"PRs to cleanup: {' '.join(prs_to_cleanup)}")
    else:
        print("No PR to cleanup.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find closed PRs to clean up.")
    parser.add_argument("--token", help="GitHub personal access token")
    args = parser.parse_args()
    main(args.token)
