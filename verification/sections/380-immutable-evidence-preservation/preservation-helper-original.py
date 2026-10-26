"""Preserve the actual precommit refusal; exempt only exact pinned immutable evidence."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import ast,json,re,shutil

R=Path(__file__).resolve().parents[1]
def read(n):return json.loads((R/n).read_bytes())
def pin(n):
    b=(R/n).read_bytes();return {'path':n,'sha256':sha256(b).hexdigest(),'bytes':len(b)}
def save(n,data):
    p=R/n;assert not p.exists()
    with p.open('xb')as s:s.write((json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode('utf8'))

original=R/'verification/sections/380-index-validation'
failed=R/'verification/sections/380-index-validation-failed-attempt1'
assert not failed.exists()
assert {p.name for p in original.iterdir()}=={'current-validation.json','execution-runner.py','git-diff-check.txt'}
bad={}
for line in (original/'git-diff-check.txt').read_text('utf8').splitlines():
    m=re.match(r'^(.*?):([0-9]+): (.+)$',line)
    if m:bad.setdefault(m[1],[]).append({'line':int(m[2]),'reason':m[3]})
log='verification/full-380/execution-attempt1/offline/actual/windows-offline.log'
diff='verification/full-380/postprocessing-schema-repair/prepared-candidate/exact-original-to-revision2.diff'
assert set(bad)=={log,diff} and len(bad[log])==1 and len(bad[diff])==5
assert all(x['reason']=='trailing whitespace.' for rows in bad.values() for x in rows)
am='verification/full-380/execution-attempt1/archive-manifest.json'
pm='verification/full-380/postprocessing-schema-repair/prepared-candidate/PREPARED_FILES.json'
assert {k:pin(log)[k]for k in('sha256','bytes')}==read(am)['files']['offline/actual/windows-offline.log']
assert {k:pin(diff)[k]for k in('sha256','bytes')}==read(pm)['files']['exact-original-to-revision2.diff']
failed.mkdir()
for p in original.iterdir():
    q=failed/p.name;q.write_bytes(p.read_bytes());assert q.read_bytes()==p.read_bytes()
fp='verification/sections/380-index-validation-failed-attempt1/git-diff-check.txt'
f=R/'.cache/finalize380.py'; before=f.read_bytes()
assert (original/'execution-runner.py').read_bytes()==before
cachebackup=R/'.cache/finalize380-before-immutable-whitespace.py';assert not cachebackup.exists();cachebackup.write_bytes(before)
pins=[pin(n)for n in(log,diff,fp)]
guard='''
# Exact immutable original evidence only; never normalize archived output or patch context.
_immutable_evidence_pins = '''+repr(pins)+'''
for _pin in _immutable_evidence_pins:
 _path=ROOT/_pin['path'];assert _path.is_file()and not _path.is_symlink()and _path.resolve().is_relative_to(ROOT.resolve())
 _raw=_path.read_bytes();assert len(_raw)==_pin['bytes']and sha256(_raw).hexdigest()==_pin['sha256'],_pin['path']
 assert git('show',':'+_pin['path'])==_raw,'Staged immutable evidence must equal its pinned original bytes.'
'''
text=before.decode('utf8')
anchor="check=subprocess.run(['git','-c','core.whitespace=cr-at-eol,-blank-at-eof','diff','--cached','--check','--','.',':(exclude)research/p3-current-guest-material-380/*.html']"
assert text.count(anchor)==1
new="check=subprocess.run(['git','-c','core.whitespace=cr-at-eol,-blank-at-eof','diff','--cached','--check','--','.',':(exclude)research/p3-current-guest-material-380/*.html',"+','.join(repr(':(exclude,literal)'+p['path'])for p in pins)+']'
text=text.replace(anchor,guard+new)
ast.parse(text)
assert text.replace(guard+new,anchor)==before.decode('utf8')
f.write_text(text,encoding='utf8',newline='\n')
out='verification/sections/380-immutable-evidence-preservation'
(R/out).mkdir()
save(out+'/repair.json',{'section':380,'kind':'PRECOMMIT_IMMUTABLE_EVIDENCE_STYLE_REFUSAL_PRESERVED',
    'at_UTC':datetime.now(timezone.utc).isoformat(),'original_actual_outer_phase_exit':1,
    'failure_stage':'Finalizer git diff --cached --check; before functional commit or push',
    'actual_failed_diff_diagnostics':bad,'original_failed_output':pin(fp),
    'original_failed_finalizer':pin('verification/sections/380-index-validation-failed-attempt1/execution-runner.py'),
    'original_full_and_candidate_manifests':[pin(am),pin(pm)],'exact_excluded_immutable_files':pins,
    'all_other_finalizer_source_restores_byte_exact_by_inverse':True,
    'all_source_and_nonlisted_evidence_diff_checks_preserved':True,
    'immutable_log_diff_and_first_refusal_reformatted':False,
    'full380_summary_or_test_results_changed':False,
    'ordinary_commit_or_push_claimed':False})
print(json.dumps({'actual_style_failure_preserved':True,'only_exact_pinned_immutable_exceptions':len(pins),
    'finalizer_after_sha256':sha256(f.read_bytes()).hexdigest(),'resume_stage':'finalize380 only, not close380 or full phase wrapper'},ensure_ascii=False))
