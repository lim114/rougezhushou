#!/usr/bin/env bash
# Recover the current development branch without discarding local changes.
set -euo pipefail
cd "$(dirname "$0")/.."
if test -n "$(git status --porcelain --untracked-files=normal)"; then
  echo 'Existing changes need to be preserved before automatic branch recovery.' >&2
  exit 1
fi
GIT_TERMINAL_PROMPT=0 git fetch --no-tags origin \
  refs/heads/codex/p2-development:refs/remotes/origin/codex/p2-development
if git show-ref --verify --quiet refs/heads/codex/p2-development; then
  git switch --quiet codex/p2-development
else
  git switch --quiet --track origin/codex/p2-development
fi
git merge --quiet --ff-only origin/codex/p2-development
if ! test -x .venv/bin/python; then
  bash scripts/cloud_setup.sh
else
  .venv/bin/python -m pip check
fi
git log -1 --format='%h %s'
