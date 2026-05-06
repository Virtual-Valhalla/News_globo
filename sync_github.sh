#!/bin/bash

REPO_URL="https://github.com/Virtual-Valhalla/News_globo.git"
BRANCH="main"
SYNC_INTERVAL=300

do_sync() {
  if [ -z "$GITHUB_TOKEN" ]; then
    echo "[github-sync] ERROR: GITHUB_TOKEN secret is not set. Skipping sync."
    return 1
  fi

  git config user.email "replit-sync@replit.com"
  git config user.name "Replit Sync"

  AHEAD=$(git rev-list "origin/${BRANCH}..HEAD" --count 2>/dev/null || echo "0")

  if [ "$AHEAD" -eq "0" ]; then
    echo "[github-sync] $(date '+%H:%M:%S') Already in sync. Nothing to push."
  else
    echo "[github-sync] $(date '+%H:%M:%S') Pushing ${AHEAD} commit(s) to GitHub..."
    AUTH_URL="https://x-token:${GITHUB_TOKEN}@github.com/Virtual-Valhalla/News_globo.git"
    if git push "$AUTH_URL" "${BRANCH}:${BRANCH}" 2>&1 | sed 's|x-token:[^@]*@|x-token:***@|g'; then
      echo "[github-sync] $(date '+%H:%M:%S') Push succeeded."
    else
      echo "[github-sync] $(date '+%H:%M:%S') Push failed. Will retry in ${SYNC_INTERVAL}s."
    fi
  fi
}

echo "[github-sync] Starting automatic GitHub sync daemon (interval: ${SYNC_INTERVAL}s)."
do_sync

while true; do
  sleep "$SYNC_INTERVAL"
  do_sync
done
