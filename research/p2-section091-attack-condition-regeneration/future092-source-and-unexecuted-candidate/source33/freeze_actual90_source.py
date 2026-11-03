"""Read named Git source objects only; no project imports or execution."""
from pathlib import Path
import hashlib
import json
import subprocess

REPO = Path('/workspace/rougezhushou')
HERE = Path(__file__).resolve().parent
ACTUAL = '2cbc45f03f99ed4f04b9c7e2612b58542f909168'
NAMES = ('rouge/app.py', 'rouge/damage.py', 'rouge/operator_engine.py',
         'rouge/timing.py', 'rouge/estimate.py', 'rouge/reporting.py',
         'rouge/run_modifiers.py', 'rouge/enemy_environment.py',
         'rouge/condition_inputs.py', 'rouge/charge_reference.py', 'rouge/relics.py')
entries = []
for rel in NAMES:
    result = subprocess.run(['git', 'show', f'{ACTUAL}:{rel}'], cwd=REPO,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        (HERE/'preparation-primary-freeze-attempt2-error.json').write_text(json.dumps({
            'path': rel, 'returncode': result.returncode, 'stderr': result.stderr.decode(),
            'dependent_operations_stopped': True}, indent=2)+'\n')
        raise SystemExit(result.returncode)
    raw = result.stdout
    dest = HERE/'fixed-actual90'/rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        assert dest.read_bytes() == raw, 'Partial earlier Git object unexpectedly differs'
    else:
        dest.write_bytes(raw)
    blob = subprocess.run(['git', 'rev-parse', f'{ACTUAL}:{rel}'], cwd=REPO,
                          stdout=subprocess.PIPE, text=True, check=True).stdout.strip()
    entries.append({'source_path': str(REPO/rel), 'git_ref': ACTUAL, 'git_blob': blob,
                    'archive_path': str(dest), 'bytes': len(raw),
                    'sha256': hashlib.sha256(raw).hexdigest()})
(HERE/'fixed-source-binding.json').write_text(json.dumps({
    'format_version': 1, 'status': 'SOURCE_ONLY_RESEARCH_NOT_COMPLETED_SECTION',
    'actual_root_commit': ACTUAL, 'sources': entries,
    'new_API_helper_formatter_Qt_Wine_tests': 0,
    'preparation': {'attempt1': 'External stdin source-copy script selected nonexistent rouge/enemy_resolution.py; git exit128, dependent processing stopped. Actual failure receipt preserved. No original disk script existed; not reconstructed or claimed retained.',
                    'attempt2': 'Corrected actual rouge/enemy_environment.py; same partial fixed objects byte-exact; no project calls.'}
}, indent=2)+'\n')
print(json.dumps({'status': 'FIXED_SOURCE_FREEZE_PASS', 'files': len(entries),
                  'bytes': sum(x['bytes'] for x in entries), 'project_calls': 0}))
