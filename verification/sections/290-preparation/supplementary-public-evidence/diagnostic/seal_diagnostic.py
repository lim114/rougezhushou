"""Save exact public diagnostic originals; does not run tests or touch A1."""
from datetime import datetime,timezone
import hashlib,json,shutil
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
freeze=ROOT/'verification/full-290/source-freeze.json'
frozen=json.loads(freeze.read_bytes())
receipt=json.loads((HERE/'candidates-receipt.json').read_bytes())
if receipt['safety_events'] or not receipt['after_matches_frozen_source'] or not receipt['freeze_bytes_unchanged']:
    raise ValueError('Do not label a safety-intervened or source-drifted diagnosis as unmodified')
manifest_path=HERE/'diagnostic-originals.json'
if manifest_path.exists():raise FileExistsError(manifest_path)
files={}
def copy(path,name,expected=None):
    before=sha(path)
    if expected is not None and before!=expected:raise ValueError('Source no longer matches original diagnostic: '+name)
    target=HERE/name;target.parent.mkdir(parents=True,exist_ok=True)
    with path.open('rb') as src,target.open('xb') as dst:shutil.copyfileobj(src,dst)
    if sha(path)!=before or sha(target)!=before:raise ValueError('Source changed during exact copy')
    files[name]={'sha256':before,'bytes':target.stat().st_size}

sources={row['test'].split('.')[0]+'.'+row['test'].split('.')[1] for row in receipt['actual_test_failures']}
paths=[name.replace('.','/')+'.py' for name in sorted(sources)]
paths+=['rouge/player_node_information.py','rouge/battle_preview.py','rouge/node_catalog_view.py',
        'rouge/event_planning.py','rouge/choice_recruitment_results.py','scripts/verify_full_available.py',
        'rouge/enemy_skill_resources.py','rouge/enemy_prefab_skill_gates.py']
for name in paths:
    copy(ROOT/name,'public-source/'+name,frozen['source_sha256'][name])
copy(freeze,'public-source/source-freeze-original.json',receipt['original_freeze_sha256'])
copy(Path(receipt['original_progress_log']),'original-A1-windows-offline-progress.log',receipt['original_progress_log_sha256'])
for path in sorted(HERE.iterdir()):
    if path.is_file() and path.name!='diagnostic-originals.json':
        files[path.name]={'sha256':sha(path),'bytes':path.stat().st_size}
record={'kind':'EXACT_OFFSCREEN_DIAGNOSTIC_ORIGINALS_NOT_FULL_VALIDATION',
    'sealed_at':datetime.now(timezone.utc).isoformat(),'files':files,
    'original_A1_files_changed':False,'production_or_test_sources_changed':False,
    'safety_interventions':0,'all_five_actual_diagnostic_failures_unintervened':True,
    'failures':[{'test':row['test'],'safety_guard_hit':False,'traceback_in':'candidates-receipt.json',
                 'original_A1_failure_identity_inferred':False} for row in receipt['actual_test_failures']],
    'classification':'All five stop at presentation assertions; no numerical mechanism conclusion is inferred. Test contract changes require separate review.',
    'native_or_full_validation_pass_claimed':False,
    'bound_original_freeze_sha256':receipt['original_freeze_sha256']}
with manifest_path.open('x',encoding='utf8') as f:json.dump(record,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'manifest_sha256':sha(manifest_path),'public_source_files':len(paths),
    'actual_diagnostic_failures':len(record['failures']),'production_modified':False},ensure_ascii=False))
