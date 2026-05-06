#!/bin/bash
set -e

if [ -z "$GITHUB_TOKEN" ]; then
  echo "ERROR: GITHUB_TOKEN secret is not set. Add it in Replit Secrets to enable GitHub sync."
  exit 1
fi

REMOTE_URL="https://${GITHUB_TOKEN}@github.com/Virtual-Valhalla/News_globo.git"

git remote set-url origin "$REMOTE_URL"

git config user.email "replit-sync@replit.com"
git config user.name "Replit Sync"

AHEAD=$(git rev-list origin/main..HEAD --count 2>/dev/null || echo "0")

if [ "$AHEAD" -eq "0" ]; then
  echo "Already in sync with GitHub. Nothing to push."
else
  echo "Pushing $AHEAD commit(s) to GitHub..."
  git push origin main
  echo "GitHub sync complete."
fi

git remote set-url origin "https://github.com/Virtual-Valhalla/News_globo"
