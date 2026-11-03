import ast
import hashlib
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parent
PROJECT=Path('/workspace/rougezhushou')
sha=lambda b:hashlib.sha256(b).hexdigest()
current=subprocess.check_output(['git','-C',str(PROJECT),'rev-parse','HEAD'],text=True).strip()
assert current=='0f27027e7e1f49c08f298706b599e310e299238b'
freeze=json.loads((ROOT/'author-freeze087.json').read_text())
for item in freeze['source_files']:
    path=PROJECT/item['path']
    raw=path.read_bytes() if path.exists() else None
    assert (sha(raw) if raw is not None else None)==item['baseline_sha256'],item['path']
related=[]
for item in freeze['unchanged_author_consumer_sources']:
    path=PROJECT/item['path'];raw=path.read_bytes()
    related.append({'path':item['path'],'bytes':len(raw),'root86_sha256':sha(raw),'author9ef_sha256':item['sha256'],
                    'unchanged':sha(raw)==item['sha256']})
assert all(x['unchanged'] for x in related if x['path'] not in ('rouge/damage.py','rouge/operator_engine.py'))
registry_path=PROJECT/'scripts/verify_cloud.py';registry=registry_path.read_bytes()
text=registry.decode('utf-8');tree=ast.parse(text)
assignment=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='MODULES' for t in n.targets))
assert isinstance(assignment.value,ast.Tuple)
entry='    "tests.test_gummy_back_animation_reference",\n'
assert entry not in text
lines=text.splitlines(keepends=True)
lines.insert(assignment.value.end_lineno-1,entry)
proposal=''.join(lines).encode('utf-8')
assert proposal.replace(entry.encode(),b'',1)==registry
(ROOT/'root86-verify_cloud.py').write_bytes(registry)
(ROOT/'registered-verify_cloud087.py').write_bytes(proposal)
patch=ROOT/'product087.patch'
check=subprocess.run(['git','-C',str(PROJECT),'apply','--check','--whitespace=nowarn',str(patch)],text=True,capture_output=True)
assert check.returncode==0,check.stderr
receipt={'version':1,'author_baseline_commit':freeze['author_baseline_commit'],'actual_root_commit':current,
  'root86_target_old_bytes_match_author_baseline':True,'product_patch_sha256':sha(patch.read_bytes()),'root86_apply_check_exit':check.returncode,
  'root86_apply_check_stdout':check.stdout,'root86_apply_check_stderr':check.stderr,'related_consumer_source_comparison':related,
  'registry_base':{'source_path':str(ROOT/'root86-verify_cloud.py'),'bytes':len(registry),'sha256':sha(registry)},
  'registry_proposal':{'source_path':str(ROOT/'registered-verify_cloud087.py'),'bytes':len(proposal),'sha256':sha(proposal),'new_entry_literal':entry,'inverse_exact':True},
  'source_and_test_bytes_changed':False,'root_mutation':False,'API_test_formatter_parser_download_Qt_Wine_calls':0,
  'note':'The root86 damage/engine and registry changes are retained. Three product target paths still match the9ef old bytes exactly; no engine copy or retesting of the passed35matrix/138API was performed.'}
(ROOT/'root86-transport-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'root_commit':current,'apply_check_exit':0,'unchanged_related_consumers':[x['path'] for x in related if x['unchanged']],'registry_proposal_sha256':sha(proposal)}))
