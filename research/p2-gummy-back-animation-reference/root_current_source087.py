"""Read-only verification of the applied source/test/registry contract; no APIs."""
import argparse
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('root',type=Path)
parser.add_argument('--author-draft',action='store_true')
args=parser.parse_args()
sha=lambda b:hashlib.sha256(b).hexdigest()
freeze=json.loads((HERE/'author-freeze087.json').read_text())
transport=json.loads((HERE/'root86-transport-receipt.json').read_text())
checked=[]
for item in freeze['source_files']:
    data=(args.root/item['path']).read_bytes()
    assert len(data)==item['draft_bytes'] and sha(data)==item['draft_sha256'],item['path']
    checked.append({'path':item['path'],'sha256':sha(data),'bytes':len(data)})
for item in freeze['unchanged_author_consumer_sources']:
    data=(args.root/item['path']).read_bytes()
    if args.author_draft:
        expected=item['sha256']
    else:
        expected=next(x for x in transport['related_consumer_source_comparison'] if x['path']==item['path'])['root86_sha256']
    assert sha(data)==expected,item['path']
    checked.append({'path':item['path'],'sha256':sha(data),'bytes':len(data)})
registry=(args.root/'scripts/verify_cloud.py').read_bytes()
literal=transport['registry_proposal']['new_entry_literal'].encode()
if args.author_draft:
    original=(HERE/'baseline/scripts/verify_cloud.py').read_bytes()
    assert registry==original
    registry_scope='Unregistered immutable9ef author draft; the prepared root86 registration inverse is checked separately'
    proposed=(HERE/'registered-verify_cloud087.py').read_bytes()
    root86=(HERE/'root86-verify_cloud.py').read_bytes()
    assert proposed.count(literal)==1 and proposed.replace(literal,b'',1)==root86
else:
    assert sha(registry)==transport['registry_proposal']['sha256']
    assert registry.count(literal)==1
    inverse=registry.replace(literal,b'',1)
    assert len(inverse)==transport['registry_base']['bytes'] and sha(inverse)==transport['registry_base']['sha256']
    registry_scope='Exact one-line new module registration inverse restores the root86 bytes'
data=json.loads((args.root/'rouge/data/original-animation-references.json').read_bytes())
assert data['counts']=={'operators':32,'source_skeletons':64,'animations':928,'selectable_references':162,'unverified_or_transition_references':766,'missing_skeletons':0}
profile=data['operators']['char_196_sunbr'];records=profile['records']
back=[r for r in records if r['orientation']=='Back']
assert len(records)==14 and [r['animation'] for r in back]==['Attack','Default','Idle','Skill','Start']
assert all(not r['runtime_binding_verified'] for r in back)
assert profile['missing_sources']==[]
inverse=json.loads(json.dumps(data))
inverse['operators']['char_196_sunbr']['records']=records[:9]
inverse['operators']['char_196_sunbr']['missing_sources']=[{'orientation':'Back','reason':'Error: boneData cannot be null.'}]
inverse['counts']={'operators':32,'source_skeletons':64,'animations':923,'selectable_references':160,'unverified_or_transition_references':763,'missing_skeletons':1}
del inverse['source_additions']
old_raw=(json.dumps(inverse,ensure_ascii=False,indent=2)+'\n').replace('\n','\r\n').encode()
old_item=next(x for x in freeze['source_files'] if x['path'].endswith('original-animation-references.json'))
assert len(old_raw)==old_item['baseline_bytes'] and sha(old_raw)==old_item['baseline_sha256']
report={'version':1,'passed':True,'root':str(args.root),'source_files_checked':checked,'registry_scope':registry_scope,
        'full_original_dataset_inverse_byte_exact':True,'old_records_preserved':923,'added_raw_Back_records':5,
        'API_helper_formatter_test_source_parser_download_Qt_Wine_calls':0,
        'qualification_scope':'Source-only. The literal Skill retains no skill number; no choices function, UI or native clock was invoked.'}
print(json.dumps(report,ensure_ascii=False,indent=2))
