#!/bin/sh
set -e

# Checkout
git checkout gh-pages
git pull origin gh-pages

# Create a branch with no history
git checkout --orphan gh-pages-clean

# Commit and push
git add .
git commit -m "purge historical binary bloat from gh-pages"
git push origin gh-pages-clean:gh-pages --force

# Local cleanup
git checkout main
git branch -D gh-pages-clean
