"""Preserve second precommit refusal; clear only live diagnostic before staging itself."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import json,ast
R=Path(__file__).resolve().parents[1]
def pin(n):
 b=(R/n).read_bytes();return {'path':n,'sha256':sha256(b).hexdigest(),'bytes':len(b)}
src=R/'verification/sections/380-index-validation'; dst=R/'verification/sections/380-index-validation-failed-attempt2'
assert not dst.exists(); text=(src/'git-diff-check.txt').read_text('utf8')
assert 'verification/sections/380-index-validation/git-diff-check.txt:2: trailing whitespace.'in text
assert all(line.startswith(('verification/sections/380-index-validation/git-diff-check.txt:','+')) for line in text.splitlines())
f=R/'.cache/finalize380.py'; raw=f.read_bytes(); assert (src/'execution-runner.py').read_bytes()==raw
assert sha256(raw).hexdigest()=='0a56dc7b752743a125e298a1783fd0e2c965c4c72dc9ba54ffba3fd9102ccf96'
dst.mkdir()
for p in src.iterdir():
 q=dst/p.name;assert not q.exists();q.write_bytes(p.read_bytes());assert q.read_bytes()==p.read_bytes()
backup=R/'.cache/finalize380-before-live-diagnostic-order.py';assert not backup.exists();backup.write_bytes(raw)
old=json.loads((R/'verification/sections/380-immutable-evidence-preservation/repair.json').read_bytes())
pins=old['exact_excluded_immutable_files']+[pin('verification/sections/380-index-validation-failed-attempt2/git-diff-check.txt')]
body=raw.decode('utf8'); a='_immutable_evidence_pins = '+repr(old['exact_excluded_immutable_files']); b='_immutable_evidence_pins = '+repr(pins)
assert body.count(a)==1;body=body.replace(a,b)
anchor="subprocess.run(['git','add','-f','--',*allowed],cwd=ROOT,check=True)"
replacement="""# Prior refusal is retained in immutable attempt2; do not recursively stage old live check output.
_previous_live_diagnostic_pin = """+repr(pins[-1])+"""
_live_diagnostic=out/'git-diff-check.txt'
assert _live_diagnostic.read_bytes()==(ROOT/_previous_live_diagnostic_pin['path']).read_bytes()
assert sha256(_live_diagnostic.read_bytes()).hexdigest()==_previous_live_diagnostic_pin['sha256']
_live_diagnostic.write_bytes(b'')
"""+anchor
assert body.count(anchor)==1;body=body.replace(anchor,replacement)
old_ex="':(exclude,literal)verification/sections/380-index-validation-failed-attempt1/git-diff-check.txt']"
new_ex="':(exclude,literal)verification/sections/380-index-validation-failed-attempt1/git-diff-check.txt',':(exclude,literal)verification/sections/380-index-validation-failed-attempt2/git-diff-check.txt']"
assert body.count(old_ex)==1;body=body.replace(old_ex,new_ex)
ast.parse(body)
assert body.replace(new_ex,old_ex).replace(replacement,anchor).replace(b,a)==raw.decode('utf8')
f.write_text(body,encoding='utf8',newline='\n')
record={'section':380,'kind':'LIVE_DIFF_DIAGNOSTIC_STAGING_ORDER_REPAIR','at_UTC':datetime.now(timezone.utc).isoformat(),
 'actual_second_finalizer_exit':1,'original_second_refusal':pins[-1],
 'original_second_finalizer':pin('verification/sections/380-index-validation-failed-attempt2/execution-runner.py'),
 'cause':'Finalizer staged its previous failed live diff output before checking; that output contains original whitespace by definition.',
 'repair':'After exact failed-output preservation and byte binding, empty only the live diagnostic before staging. Final real check output is then written and staged normally.',
 'immutable_exceptions':pins,'entire_original_finalizer_restored_by_exact_three_inverse_replacements':True,
 'archived_original_outputs_or_full380_summary_modified':False,'source_whitespace_checks_disabled':False,
 'next_action':'Run finalizer only; no tests or close380 rerun; no new section.'}
target=R/'verification/sections/380-immutable-evidence-preservation/repair-revision2.json';assert not target.exists()
target.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
copy=R/'verification/sections/380-immutable-evidence-preservation/live-diagnostic-order-helper.py';assert not copy.exists();copy.write_bytes(Path(__file__).read_bytes())
print(json.dumps({'second_refusal_preserved':True,'exact_pinned_exceptions':len(pins),'staging_order_fixed':True,'finalizer_sha256':sha256(f.read_bytes()).hexdigest()}))
