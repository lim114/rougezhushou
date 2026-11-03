"""Prepare the independent A3 readback wrapper from reviewed A2 pure checks."""
from pathlib import Path
import ast
ROOT=Path(__file__).resolve().parents[1]
old=(ROOT/'.cache/audit-full275-saved-readback.py').read_text(encoding='utf8')
tail=old[old.index("tool = BUNDLE/'audit_full261_saved_readback.py'"):]
tail=tail.replace("assert sha(tar_path.read_bytes())==first_manifest['frozen_source_archive_sha256']\n",'')
tail=tail.replace("'actual_native_attempt':2", "'actual_native_attempt':3")
tail=tail.replace("'original_frozen_public_evidence_root':SNAPSHOT.relative_to(ROOT).as_posix(),", 
                  "'audit_root':str(ROOT), 'source_scope':'Exact A3 root source still matches source-freeze-reset-repair; no previous phase reused',")
prefix='''"""Only decode actual A3 saved output and inspect exact source; never run application."""
from pathlib import Path
import ast, collections, copy, gzip, hashlib, importlib.util, json, subprocess, sys
sys.dont_write_bytecode=True
ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / 'verification/full-275/legacy-window-attempt3'
BUNDLE = ARCHIVE / 'executed-tools'
FREEZE = ROOT / 'verification/full-275/source-freeze-reset-repair.json'
BASE = ROOT / '.cache/full275-saved-readback-attempt3'
BASE.mkdir(exist_ok=False)
SNAPSHOT = ROOT
CONTAINER = BASE / 'audit-input-container'
CONTAINER.mkdir()
def sha(raw):return hashlib.sha256(raw).hexdigest()
def read(path):return json.loads(path.read_bytes())
def write(path,value):
    with path.open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\\n')
def ordered(value):return json.dumps(value,ensure_ascii=False,separators=(',',':'))
def copy_exclusive(source,target,expected):
    assert source.is_file() and not source.is_symlink()
    raw=source.read_bytes();assert sha(raw)==expected
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('xb') as f:f.write(raw)
    assert sha(target.read_bytes())==expected
    return {'from':source.relative_to(ROOT).as_posix(),'to':target.relative_to(BASE).as_posix(),'sha256':expected,'bytes':len(raw)}
manifest=read(ARCHIVE/'archive-manifest.json')
original_hashes={name:sha((ARCHIVE/name).read_bytes()) for name in manifest['files']}
assert all(original_hashes[name]==pin['sha256'] and (ARCHIVE/name).stat().st_size==pin['bytes'] for name,pin in manifest['files'].items())
original_hashes['archive-manifest.json']=sha((ARCHIVE/'archive-manifest.json').read_bytes())
live_pins=read(FREEZE)['source_sha256']
live_before={name:sha((ROOT/name).read_bytes()) for name in live_pins}
assert live_before==live_pins
guard=read(BUNDLE/'current-source-guard.json')
for group in ('source_sha256','source_additional_sha256'):
    for name,pin in guard[group].items():assert sha((ROOT/name).read_bytes())==pin,name
copied=[]
for source in sorted((ARCHIVE/'actual').rglob('*')):
    if source.is_file():
        relative='actual/'+source.relative_to(ARCHIVE/'actual').as_posix()
        copied.append(copy_exclusive(source,CONTAINER/relative,original_hashes[relative]))
copied.append(copy_exclusive(ARCHIVE/'supervisor.json',CONTAINER/'supervisor.json',original_hashes['supervisor.json']))
supervisor=read(ARCHIVE/'supervisor.json')
assert supervisor['status']=='completed' and supervisor['child_primary_exit']==supervisor['supervisor_exit']==0
assert supervisor['timed_out'] is False and supervisor['owned_job_no_live_execution_verified'] is True
with (CONTAINER/'process.exit').open('x',encoding='ascii') as f:f.write(str(supervisor['supervisor_exit'])+'\\n')
write(BASE/'input-preparation.json',{
    'kind':'READONLY_A3_SAVED_OUTPUT_FROM_REAL_SEALED_BYTES',
    'current_root_source_count':len(live_pins),'current_root_freeze_sha256':sha(FREEZE.read_bytes()),
    'guard_source_count':len(guard['source_sha256']),'guard_additional_source_count':len(guard['source_additional_sha256']),
    'current_checkout_replaced_or_application_executed':False,
    'original_archive_files_hash_before':original_hashes,
    'process_exit':'DERIVED_INPUT_ONLY_FROM_TERMINAL_REAL_SUPERVISOR_NOT_ORIGINAL_RAW_CONSOLE',
    'process_exit_authority':{'path':(ARCHIVE/'supervisor.json').relative_to(ROOT).as_posix(),
        'sha256':original_hashes['supervisor.json'],'terminal_status':supervisor['status'],
        'child_primary_exit':supervisor['child_primary_exit'],'supervisor_exit':supervisor['supervisor_exit'],
        'timed_out':supervisor['timed_out'],'owned_job_no_live_execution_verified':supervisor['owned_job_no_live_execution_verified']},
    'copies':copied,'private_state_or_game_samples_read':False})
'''
text=prefix+tail
ast.parse(text)
target=ROOT/'.cache/audit-full275-saved-readback-attempt3.py'
with target.open('x',encoding='utf8',newline='') as f:f.write(text)
print(str(target))
