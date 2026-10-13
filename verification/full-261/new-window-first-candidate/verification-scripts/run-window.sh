#!/usr/bin/env bash
# Execute only after Root declares the maintained source frozen.
set -euo pipefail
window_audit_root='/workspace/rougezhushou'
window_audit_bundle="$window_audit_root/work/full261-current-window"
window_audit_phase="${1:-frozen-final}"
window_audit_output="$window_audit_bundle/$window_audit_phase"
window_audit_launcher="$window_audit_root/work/wine-persistence-audit/runtime11/run-python11-devel.sh"
if test -e "$window_audit_output/window.json"; then
  echo 'This evidence phase already exists; choose a new phase and preserve it.' >&2
  exit 2
fi
mkdir -p "$window_audit_output"
cd "$window_audit_root"
window_audit_head="$(git rev-parse HEAD)"
set +e
ROUGE_WINE_PYTHON_LAUNCHER="$window_audit_launcher" PYTHONFAULTHANDLER=1 \
  bash scripts/wine_python.sh work/full261-current-window/window.py \
  --output "work/full261-current-window/$window_audit_phase" --revision "$window_audit_head" \
  > "$window_audit_output/process.log" 2>&1
window_audit_exit=$?
set -e
.venv/bin/python - "$window_audit_output" "$window_audit_exit" "$window_audit_head" <<'PY'
import hashlib,json,sys
from pathlib import Path
out=Path(sys.argv[1]);exit_code=int(sys.argv[2]);root=Path.cwd()
record=json.loads((out/'window.json').read_text()) if (out/'window.json').is_file() else None
receipt={'process_exit_code':exit_code,'process_exited_normally':exit_code==0,
         'window_receipt_exists':record is not None,'window_workflows_passed':bool(record and record['passed']),
         'head_label':sys.argv[3],'actual_working_tree_in_window_receipt':True,
         'shared_lock_wrapper':'scripts/wine_python.sh',
         'wine11_launcher':'work/wine-persistence-audit/runtime11/run-python11-devel.sh',
         'native_windows_verified':False,'game_actions':0,'chat_requests':0,
         'checks':len(record['checks']) if record else None,
         'covered_new_sections':record.get('new_sections_covered') if record else None,'maintenance261_safe_save_check':record.get('maintenance261_safe_save_check') if record else None,
         'source_drift':record.get('source_drift') if record else None,
         'artifacts_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}}
(out/'execution.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({key:receipt[key] for key in ('process_exit_code','window_workflows_passed','checks','covered_new_sections','source_drift')},ensure_ascii=False))
PY
exit "$window_audit_exit"
