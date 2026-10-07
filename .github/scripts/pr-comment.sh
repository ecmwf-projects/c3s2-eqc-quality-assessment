#!/usr/bin/env bash
# Manage the bot's comments on a pull request.
#
# Usage: pr-comment.sh upsert TAG BODY   create the comment tagged TAG, or update it in place
#        pr-comment.sh update TAG BODY   update the comment tagged TAG if there is one
#
# Comments are found by a hidden marker containing TAG. It matches the marker used by
# thollander/actions-comment-pull-request, so comments posted by that action are reused.
# Needs GH_TOKEN, GITHUB_REPOSITORY and PR in the environment.
set -euo pipefail

comments="repos/$GITHUB_REPOSITORY/issues/$PR/comments"

# Print the IDs of the bot's comments that contain $1
find_comments() {
    gh api --paginate "$comments" | jq -rs --arg marker "$1" \
        'add | .[] | select(.user.login == "github-actions[bot]" and (.body | contains($marker))) | .id'
}

case $1 in
upsert | update)
    marker="<!-- thollander/actions-comment-pull-request \"$2\" -->"
    body="$3"$'\n'"$marker"
    id=$(find_comments "$marker" | sed -n 1p)
    if [[ -n $id ]]; then
        gh api -X PATCH "repos/$GITHUB_REPOSITORY/issues/comments/$id" -f body="$body" >/dev/null
    elif [[ $1 == upsert ]]; then
        gh api "$comments" -f body="$body" >/dev/null
    fi
    ;;
*)
    echo "Unknown command: $1" >&2
    exit 1
    ;;
esac
