#!/usr/bin/env bash
# Root must freeze261 production and activate the fresh bundle before execution.
set -euo pipefail
validation_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
validation_bundle="$validation_root/work/261-validation/legacy-window-bundle"
validation_launcher="$validation_root/work/wine-persistence-audit/runtime11/run-python11-devel.sh"
validation_out="${1:?Provide a fresh absolute evidence directory outside the repository}"
cd "$validation_root"
.venv/bin/python - "$validation_bundle" "$validation_out" <<'PY'
import hashlib,json,sys
from pathlib import Path
bundle=Path(sys.argv[1]);out=Path(sys.argv[2]);root=Path.cwd()
if not out.is_absolute() or out.resolve().is_relative_to(root) or out.exists():
    raise ValueError('Evidence output must be fresh, absolute and outside the repository')
activation=json.loads((bundle/'activation261.json').read_bytes())
if activation['status']!='CURRENT_SOURCE_BOUND_NOT_EXECUTED' or activation['binding_ready'] is not True:
    raise ValueError('Root-frozen current261 source must be activated first')
for relative,expected in activation['activated_sha256'].items():
    if hashlib.sha256((bundle/relative).read_bytes()).hexdigest()!=expected:
        raise ValueError('Activated executed-tool drift: '+relative)
out.mkdir(parents=True,exist_ok=False)
PY
if ! test -x "$validation_launcher"; then
  echo 'The supported Wine11 compatibility Python launcher is unavailable.' >&2
  exit 2
fi
validation_zroot="Z:${validation_root//\//\\}"
validation_zbundle="Z:${validation_bundle//\//\\}"
validation_zout="Z:${validation_out//\//\\}"
set +e
# The shared lock is acquired before the1200s supervisor starts. The child uses
# the Wine11 launcher directly; calling wine_python.sh under this same lock
# would attempt to acquire it twice. No lock wait counts as window runtime.
flock /tmp/rouge-wine-python.lock \
  .venv/bin/python "$validation_bundle/supervisor125.py" \
  --status "$validation_out/supervisor.json" -- \
  bash "$validation_launcher" "$validation_zbundle\\launcher125.py" \
  --root "$validation_zroot" --guard "$validation_zbundle\\current-source-guard.json" \
  --out "$validation_zout" > "$validation_out/supervisor-launch.log" 2>&1
validation_exit=$?
set -e
printf '%s\n' "$validation_exit" > "$validation_out/process.exit"
exit "$validation_exit"
