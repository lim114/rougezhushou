"""Explicit child v1 archive seal; no API, helper, test or apply repetition."""
from pathlib import Path
import hashlib
import json

OUT=Path(__file__).resolve().parent
AUTHOR=Path('/workspace/.continuation/p2-orchid-near-text-085')
def sha(data):return hashlib.sha256(data).hexdigest()
def save(name,value):
    with (OUT/name).open('x',encoding='utf-8') as f:
        json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
receipt=json.loads((OUT/'source-guard-review085.json').read_bytes())
assert receipt['status']=='passed_no_blocker' and receipt['calculate_damage_calls']==0
assert sha((OUT/'source-guard-review085.json').read_bytes())=='26d2acf6b5cabed781034d2bbfaf58c94da90dd5693164e43ba0797355314926'
for rel,row in receipt['baseline_public_hashes'].items():
    data=(AUTHOR/'baseline'/rel).read_bytes();assert len(data)==row['bytes'] and sha(data)==row['sha256']
    if rel!='rouge/damage.py':assert (AUTHOR/'draft'/rel).read_bytes()==data
for row in receipt['bindings']:
    data=(OUT/row['archive_path']).read_bytes()
    assert len(data)==row['bytes'] and sha(data)==row['sha256'] and Path(row['source_path']).read_bytes()==data
helper=json.loads((OUT/'selected-helper-qualification085.json').read_bytes())
assert helper['actual_selected_talents_calls']==9 and helper['calculate_damage_calls']==0
assert json.loads((OUT/'readonly-apply-check085.json').read_bytes())['returncode']==0
assert json.loads((OUT/'patch-numstat085.json').read_bytes())['returncode']==0
save('seal-validation085.json',{'status':'passed','baseline720_and_existingdraft719_rechecked':True,
    'all_source_and_author_bindings_unchanged':True,'calculate_damage_calls':0,'pure_helper_calls_repeated':0,
    'tests_repeated':0,'apply_checks_repeated':0,'tracked_mutations':False})
names=['audit_source085.py','audit-source085.log','patch-numstat085.json','readonly-apply-check085.json',
       'selected-helper-qualification085.json','source-guard-review085.json','boundary085.md','NOTE.md',
       'seal_subreview085.py','seal-validation085.json']
names += [row['archive_path'] for row in receipt['bindings']]
assert len(names)==len(set(names))
save('handoff.json',{'status':'final_sealed_source_guard_transport_passed','source_guard_review_sha256':sha((OUT/'source-guard-review085.json').read_bytes()),
    'frozen_author_sha256':receipt['author_freeze_sha256'],'final_author_damage_sha256':receipt['author_damage_sha256'],
    'final_author_patch_sha256':receipt['patch_sha256'],'source22_manifest_sha256':receipt['source_only22_manifest_sha256'],
    'pure_selected_talents_helper_calls':9,'calculate_damage_calls':0,'new_tests_run':0,'GUI':False,'Wine':False,
    'tracked_mutations':False,'no_blocker':True,'not_a_numerical_or_native_return_type_review':True,
    'surgical_root_integration_required':True,'artifacts_excluding_this_handoff_and_manifest':len(names)})
names.append('handoff.json')
rows=[]
for name in sorted(names):
    path=OUT/name;data=path.read_bytes();rows.append({'source_path':str(path),'archive_path':name,'bytes':len(data),'sha256':sha(data)})
save('public-artifacts-manifest.json',{'format_version':1,'status':'final_sealed_source_guard_transport_passed',
    'files':rows,'bytes':sum(r['bytes'] for r in rows),'calculate_damage_calls':0,'pure_selected_talents_helper_calls':9,
    'excluded_execution_copies':['fixed-helper-package/','readonly-apply-target/']})
assert all(len(Path(r['source_path']).read_bytes())==r['bytes'] and sha(Path(r['source_path']).read_bytes())==r['sha256'] for r in rows)
print(json.dumps({'status':'passed','files':len(rows),'bytes':sum(r['bytes'] for r in rows),
    'source_review_sha256':sha((OUT/'source-guard-review085.json').read_bytes()),
    'handoff_sha256':sha((OUT/'handoff.json').read_bytes()),
    'manifest_sha256':sha((OUT/'public-artifacts-manifest.json').read_bytes()),'calculate_damage_calls':0,'helper_calls':9}))
