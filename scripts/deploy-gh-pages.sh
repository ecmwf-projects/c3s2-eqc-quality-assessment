#!/usr/bin/env bash
# Publish a directory to a path on the gh-pages branch, retrying if the branch moves.
#
# Usage: deploy-gh-pages.sh CHECKOUT TARGET MESSAGE [SOURCE]
#   CHECKOUT  local checkout of the gh-pages branch
#   TARGET    path on the branch to replace ("." for the root, which keeps pr-preview/)
#   MESSAGE   commit message
#   SOURCE    directory to publish; omit to remove TARGET
set -euo pipefail

checkout=$1
target=$2
message=$3
src=${4:+$(realpath "$4")}

cd "$checkout"
for attempt in 1 2 3 4 5; do
    git fetch --depth 1 origin gh-pages
    git reset --hard FETCH_HEAD
    git clean -fdx

    if [[ $target == . ]]; then
        find . -mindepth 1 -maxdepth 1 ! -name .git ! -name pr-preview -exec rm -rf {} +
    else
        rm -rf "$target"
    fi
    if [[ -n $src ]]; then
        mkdir -p "$target"
        cp -r "$src/." "$target/"
    fi

    git add -A
    if git diff --cached --quiet; then
        echo "Nothing to deploy"
        exit 0
    fi
    git -c user.name="github-actions[bot]" \
        -c user.email="41898282+github-actions[bot]@users.noreply.github.com" \
        commit -q -m "$message"
    if git push origin HEAD:gh-pages; then
        exit 0
    fi
    sleep $((attempt * 10))
done

echo "Failed to push to gh-pages" >&2
exit 1
