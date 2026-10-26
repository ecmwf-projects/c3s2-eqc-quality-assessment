#!/bin/sh
# Replace the gh-pages history with a single commit containing its current content.
# Works on the remote branch directly, so nothing in the local checkout gets committed.
set -e

git fetch origin +gh-pages:refs/remotes/origin/gh-pages
commit=$(git commit-tree "refs/remotes/origin/gh-pages^{tree}" -m "purge historical binary bloat from gh-pages")
git push --force-with-lease=gh-pages:refs/remotes/origin/gh-pages origin "$commit:refs/heads/gh-pages"
