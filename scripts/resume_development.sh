#!/usr/bin/env bash
# Recover main without discarding local changes.
set -euo pipefail
cd "${BASH_SOURCE[0]%/*}/.."
if test -n "$(git status --porcelain --untracked-files=normal)"; then
  echo 'Existing changes need to be preserved before automatic branch recovery.' >&2
  exit 1
fi
GIT_TERMINAL_PROMPT=0 git fetch --no-tags origin \
  refs/heads/main:refs/remotes/origin/main
if git show-ref --verify --quiet refs/heads/main; then
  git switch --quiet main
else
  git switch --quiet --track origin/main
fi
git merge --quiet --ff-only origin/main
if ! test -x .venv/bin/python; then
  bash scripts/cloud_setup.sh
else
  .venv/bin/python -m pip check
fi
git log -1 --format='%h %s'
