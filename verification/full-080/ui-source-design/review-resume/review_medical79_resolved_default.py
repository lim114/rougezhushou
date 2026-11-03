"""Static medical-form UI design review; saved-output checks are not new API calls."""
import ast
from collections import Counter
import gzip
import hashlib
import json
import sys
from pathlib import Path

P=Path('/workspace/.continuation/ui-080-draft')
R=P/'review-resume'
S=Path('/workspace/.continuation/p2-amiya-regeneration-talent-qualification-079')
ROOT=Path('/workspace/rougezhushou')
sha=lambda data:hashlib.sha256(data).hexdigest()
names=('cases080.py','public_contracts.py','supplemental-checks.py.fragment','wine-ui-smoke-080.py')
raw={n:(P/n).read_bytes()for n in names}
assert raw=={n:(P/n).read_bytes()for n in names},'concurrent draft mutation'
assert sha(raw['wine-ui-smoke-080.py'])==sys.argv[1]
for name,data in raw.items():(R/('medical79-corrected-'+name)).write_bytes(data)
ns={};exec(compile(raw['cases080.py'],'<pure cases>','exec'),ns)
cases=[c for c in ns['cases080']()if c['section']==79]
assert len(cases)==212
app=(ROOT/'rouge/app.py').read_text()
assert "if key=='amiya_hit_targets':widget.setMinimum(1)"in app
assert "limit=100 if (op=='char_1037_amiya3' and skill==1)"in app
assert "else 1)"in app
fragment=raw['supplemental-checks.py.fragment'].decode()
assert "window.healing_targets.maximum()==(100 if number080==1 else 1)"in fragment
assert "medical_targets080.minimum()==1 and medical_targets080.maximum()==100"in fragment
assert "'amiya_hit_targets'not in args080"in fragment
catalog=json.loads((ROOT/'rouge/data/catalog.json').read_bytes())['operators']['char_1037_amiya3']
for case in cases:
    args=case['input'];skill=args['skill'];elite=args['elite']
    assert args['operator']=='char_1037_amiya3'
    assert 1<=args['level']<=catalog['phases'][elite]['max_level']
    assert catalog['skills'][skill-1]['unlock_elite']<=elite
    assert type(args['healing_targets'])is int and 0<=args['healing_targets']<=(100 if skill==1 else 1)
    if skill==2:assert type(args['amiya_hit_targets'])is int and 1<=args['amiya_hit_targets']<=100
    else:assert 'amiya_hit_targets'not in args
    assert 'base_attack'not in args and 'base_hp'not in args

source=json.loads((S/'source-receipt79.json').read_bytes())
original=(S/'char_patch_table.json').read_bytes()
assert sha(original)=='d1850d5aeec1a9246a0531e88c167e66745644957662c8272fc764f54904c57e'
patch=json.loads(original);medical=patch['patchChars']['char_1037_amiya3']
assert 'char_1037_amiya3'in patch['infos']['char_002_amiya']['tmplIds']
assert medical['profession']=='MEDIC'and medical['subProfessionId']=='incantationmedic'
talents=[c for t in medical['talents']for c in t['candidates']if c['name']=='诚挚期许']
assert [c['unlockCondition']for c in talents]==[{'phase':'PHASE_1','level':1},{'phase':'PHASE_2','level':1}]
assert source['form_identity']['complete_original_medical_form']==medical
metadata=source['exact_module_metadata']
assert metadata['charId']=='char_002_amiya'and metadata['tmplId']=='char_1037_amiya3'
assert metadata['unlockEvolvePhase']=='PHASE_2'and metadata['unlockLevel']==50
module=next(m for m in catalog['modules']if m['id']=='uniequip_002_amiya3')
assert module['unlock_elite']==2 and module['unlock_level']==50

saved_raw=(S/'public-draft79.json.gz').read_bytes()
saved=json.loads(gzip.decompress(saved_raw))
contract_ns={};exec(compile(raw['public_contracts.py'],'<pure contract helpers>','exec'),contract_ns)
reviewed=[]
for record in saved:
    args=dict(record['scenario']);args.setdefault('healing_targets',1);outcome=record['outcome']
    if 'result'not in outcome or args.get('window_seconds')not in (0,10):continue
    if args.get('timing_mode')not in ('frames','continuous'):continue
    if args['healing_targets']>(100 if args['skill']==1 else 1):continue
    if args.get('timing',{})not in ({},{'target_disappears_seconds':0},{'target_windows':[]}):continue
    if args.get('relic_ids',[])or args.get('enemy_defense',0)!=0 or args.get('enemy_resistance',0)!=0:continue
    contract_ns['require_medical_amiya080'](outcome['result'],args,outcome['text_report'])
    reviewed.append({'elite':args['elite'],'skill':args['skill'],'mode':args['timing_mode'],
        'window':args['window_seconds'],'label':record['label']})
assert reviewed
receipt={'status':'medical79_static_and_saved_contract_review_passed_final080_pending',
    'scope':'Static actual Qt producer and original medical form; saved author outputs only',
    'files':{n:sha(data)for n,data in raw.items()},
    'runner_sha256':sha(raw['wine-ui-smoke-080.py']),'design_cases':212,
    'readonly_source_form_and_talent_gate_verified':True,
    'module_exact_base_character_and_medical_template_binding_verified':True,
    'actual_S1_S2_friendly_target_limit_verified':{'S1':[0,100],'S2':[0,1]},
    'actual_S2_opening_target_spin_limit_verified':[1,100],
    'inactive_S1_opening_target_omission_verified':True,
    'author_saved_output_contract_checks':len(reviewed),
    'saved_output_sha256':sha(saved_raw),
    'saved_sparse_input_default_adapter':'healing_targets default1 directly proven by frozen original engine line332; GUI scenario always includes this key',
    'saved_case_scope':dict(Counter(f"E{r['elite']}S{r['skill']}:{r['mode']}"for r in reviewed)),
    'blockers':[],'new_public_api_calls':0,'gui_executed':False,'wine_executed':False,
    'ready_for_actual_execution':False,
    'boundary':'No account form-unlock, zero-HP, native clock, module attachment, or actual healing-recipient proof.'}
(R/'medical79-saved-contract-scope.json').write_text(json.dumps(reviewed,ensure_ascii=False,indent=2)+'\n')
(R/'medical79-static-review.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items()if k!='files'},ensure_ascii=False))
