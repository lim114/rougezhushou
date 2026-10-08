"""Independent source/static design check only. Final080 source and execution remain pending."""
import ast
from collections import Counter
import hashlib
import json
from pathlib import Path

P=Path('/workspace/.continuation/ui-080-draft')
R=P/'review-resume'
ROOT=Path('/workspace/rougezhushou')
sha=lambda data:hashlib.sha256(data).hexdigest()
names=('cases080.py','public_contracts.py','supplemental-checks.py.fragment','wine-ui-smoke-080.py')
raw={n:(P/n).read_bytes()for n in names}
assert raw=={n:(P/n).read_bytes()for n in names},'concurrent draft mutation'
assert sha(raw['wine-ui-smoke-080.py'])=='74fa02dd0f962008f4a6a051e53633e101615c3a4c44a1661f8b5e68f35df4e9'
for name,data in raw.items():(R/('trait80-preliminary-'+name)).write_bytes(data)
ns={};exec(compile(raw['cases080.py'],'<pure design cases>','exec'),ns)
all_cases=ns['cases080']()
assert Counter(c['section']for c in all_cases)=={76:432,77:424,78:360,79:212,80:180}
cases=[c for c in all_cases if c['section']==80]
sources={
    'patch':(Path('/workspace/.continuation/p2-after-076-condition-eligibility-audit/char_patch_table.json'),'d1850d5aeec1a9246a0531e88c167e66745644957662c8272fc764f54904c57e'),
    'battle':(Path('/workspace/.continuation/p2-after-070-source-audit/originals/battle_equip_table.json'),'006687f201a823abf31c6a1c57b2269099bd3ea375c2ec3ae5595cc98a1ec460'),
    'equip':(Path('/workspace/.continuation/p2-after-070-source-audit/originals/uniequip_table.json'),'b508483cc87c03d8313f4dd8dfc1b9195bc50385a8dfec51d17e657cb26ffad9')}
data={}
for kind,(path,expected)in sources.items():
    b=path.read_bytes();assert sha(b)==expected;data[kind]=json.loads(b)
op='char_1037_amiya3';mid='uniequip_002_amiya3'
original=data['patch']['patchChars'][op]
base=original['trait']['candidates'];assert len(base)==1
base=base[0]
assert base['blackboard']==[{'key':'scale','value':.5,'valueStr':None}]
meta=data['equip']['equipDict'][mid]
assert meta['charId']=='char_002_amiya'and meta['tmplId']==op
assert meta['unlockEvolvePhase']=='PHASE_2'and meta['unlockLevel']==50
assert mid in data['equip']['charEquip'][op]
catalog=json.loads((ROOT/'rouge/data/catalog.json').read_bytes())['operators'][op]
module=next(m for m in catalog['modules']if m['id']==mid)
assert catalog['trait']==original['trait']
for i,phase in enumerate(data['battle'][mid]['phases']):
    assert phase['parts']==module['levels'][i]['parts']
    parts=[p for p in phase['parts']if p['target']=='TRAIT_DATA_ONLY']
    assert len(parts)==1
    part=parts[0]
    assert part['isToken']is False and part['validInGameTag']is None and part['validInMapTag']is None
    cs=part['overrideTraitDataBundle']['candidates'];assert len(cs)==1
    c=cs[0]
    assert c['overrideDescripton']==base['overrideDescripton']
    assert c['blackboard']==[{'key':'scale','value':.6,'valueStr':None}]
    assert c['unlockCondition']=={'phase':'PHASE_2','level':50}and c['requiredPotentialRank']==0
    assert c['additionalDescription']is None
for case in cases:
    args=case['input'];skill=args['skill']
    assert args['operator']==op
    assert type(args['healing_targets'])is int and 0<=args['healing_targets']<=(100 if skill==1 else 1)
    assert 1<=args['level']<=catalog['phases'][args['elite']]['max_level']
    assert catalog['skills'][skill-1]['unlock_elite']<=args['elite']
    if args['module_id']is None:assert args['module_level']==0
    else:assert args['module_id']==mid and args['module_level']in(1,2,3)
    ratio=.6 if args['module_id']==mid and args['elite']==2 and args['level']>=50 else .5
    assert case['expected_trait_ratio']==ratio
    assert args['relic_ids']in([],['rogue_6_relic_legacy_81'])
    assert args['enemy_defense']==0 and args['enemy_resistance']in(0,50)
mechanics=json.loads((ROOT/'rouge/data/relic-mechanics.json').read_bytes())
relic=mechanics['relics']['rogue_6_relic_legacy_81']
assert relic['status']=='numeric'
assert any(e['kind']=='healing_factor'and e['value']==1.2 for e in relic['effects'])
fragment=raw['supplemental-checks.py.fragment'].decode()
for text in ("relics(requested080['relic_ids'])","window.defense.setValue(requested080['enemy_defense'])",
             "window.resistance.setValue(requested080['enemy_resistance'])"):
    assert text in fragment
assert "'enemy_defense','enemy_resistance')"in fragment
assert "'healing_targets','relic_ids'"in fragment
assert "receipt['sections77_80_final_checks_pending']=True"in fragment
base_runner=Path('/workspace/.compat/wine-ui-smoke-075.py').read_bytes()
assert sha(base_runner)=='645ebd2e90ab3aef1fa5c9318300bd5e690c5f1dd6cfb67f94ed74f355ca4f03'
helpers=raw['public_contracts.py'].decode()+'\n'+raw['cases080.py'].decode()
runner=raw['wine-ui-smoke-080.py'].decode();ast.parse(runner)
assert runner.count(fragment+'\n')==1 and runner.count(helpers+'\n\n')==1
restored=runner.replace(fragment+'\n','',1).replace(helpers+'\n\n','',1)
for name in('wine-ui-report-difference-075.json','wine-window-075.png','wine-ui-075.json',
            'wine-ui-failure-075.png','wine-sown-tile-control-075.png','wine-movement-reference-075.png'):
    restored=restored.replace(name.replace('-075','-080'),name)
restored=restored.replace('-(next_end-next_start)','')
restored=restored.replace("        receipt['preserved_full_075_checks']=len(checks)\n"
    "        assert receipt['preserved_full_075_checks']==1455,receipt['preserved_full_075_checks']\n",'')
assert restored.encode()==base_runner
receipt={'status':'all_design_static_preliminary_passed_final080_source_and_preflight_pending',
    'scope':'Source/static only, including all76-80 producer design; no actual UI or new API calls',
    'files':{n:sha(b)for n,b in raw.items()},'runner_sha256':sha(raw['wine-ui-smoke-080.py']),
    'all_case_design_counts':dict(Counter(c['section']for c in all_cases)),
    'new_design_count':len(all_cases),'old1455_complete_body_reconstructed_exactly':True,
    'exact_medical_template_and_all3_same_trait_override_verified':True,
    'qualified_trait_parameter_is_replacement_not_stack':True,
    'global_relic_defense_resistance_have_per_row_real_producers_and_scenario_assertions':True,
    'blockers':[],'new_public_api_calls':0,'gui_executed':False,'wine_executed':False,
    'ready_for_actual_execution':False,
    'limits':'Author/root 80 final source and fixed-commit 1608 API preflight still pending. No native attachment, actual recipient, S2 opening order or end-clock proof.'}
(R/'trait80-preliminary-static-review.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items()if k!='files'},ensure_ascii=False))
