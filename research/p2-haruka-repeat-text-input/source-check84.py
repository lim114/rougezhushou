import ast
import hashlib
import json
import sys
from pathlib import Path

OUT=Path(__file__).parent
freeze=json.loads((OUT/'freeze-receipt.json').read_bytes())
for rel,proof in freeze['files'].items():
    data=(OUT/'frozen'/rel).read_bytes()
    assert hashlib.sha256(data).hexdigest()==proof['sha256']
sys.path.insert(0,str(OUT/'frozen'))
from rouge.catalog import catalog
from rouge.operator_engine import selected_talents
paths={
 'character_table':('/workspace/rougezhushou/.cache/p2-s1-binding/character_table.json','68e3a3b5ee0d407ce234afaa5867c6fda6379a6843c7d5317a7bbda4779f8697'),
 'skill_table':('/workspace/rougezhushou/.cache/p2-s1-binding/skill_table.json','86f4aa64c785f39727edd06d6dd8a4f27f371c8e4ace5345ba0dc61dee1386ca'),
 'battle_equip_table':('/workspace/.continuation/p2-after-070-source-audit/originals/battle_equip_table.json','006687f201a823abf31c6a1c57b2269099bd3ea375c2ec3ae5595cc98a1ec460'),
 'uniequip_table':('/workspace/.continuation/p2-after-070-source-audit/originals/uniequip_table.json','b508483cc87c03d8313f4dd8dfc1b9195bc50385a8dfec51d17e657cb26ffad9')}
tables,proofs={},{}
for name,(name_path,expected) in paths.items():
    path=Path(name_path);data=path.read_bytes()
    assert hashlib.sha256(data).hexdigest()==expected
    tables[name]=json.loads(data)
    proofs[name]={'path':str(path),'bytes':len(data),'sha256':expected}
owner=tables['character_table']['char_4202_haruka']
projected=catalog()['operators']['char_4202_haruka']
binding=owner['skills'][1]
assert binding['skillId']=='skchr_haruka_2'
assert binding['unlockCond']=={'phase':'PHASE_1','level':1}
assert projected['skills'][1]['unlock_elite']==1
raw_skill=tables['skill_table']['skchr_haruka_2']
levels=[]
for rank,(raw,part) in enumerate(zip(raw_skill['levels'],projected['skills'][1]['levels'],strict=True),1):
    values={b['key']:b['value'] for b in raw['blackboard']}
    assert values==part['values'] and raw['description']==part['description']
    assert '第二次及以后使用时攻击力' in raw['description'] and '持续时间无限' in raw['description']
    assert values['haruka_s_2[first].atk']==0
    assert values['atk']==(0.15 if rank<=3 else 0.2 if rank<=6 else {7:0.25,8:0.3,9:0.35,10:0.4}[rank])
    levels.append({'rank':rank,'complete_raw_level':raw})
for raw_group,current_group in zip(owner['talents'],projected['talents'],strict=True):
    for raw,current in zip(raw_group['candidates'],current_group,strict=True):
        assert raw['name']==current['name'] and raw['description']==current['description']
        assert int(raw['unlockCondition']['phase'][-1])==current['phase']
        assert raw['unlockCondition']['level']==current['level']
        assert raw['requiredPotentialRank']==current['potential_rank']
        assert {b['key']:b['value'] for b in raw['blackboard']}==current['values']
module=projected['modules'][0]
assert module['id']=='uniequip_002_haruka' and module['unlock_elite']==2 and module['unlock_level']==60
raw_module=tables['battle_equip_table'][module['id']]
raw_meta=tables['uniequip_table']['equipDict'][module['id']]
assert raw_meta['charId']==projected['id'] and raw_meta['unlockLevel']==60
for raw,current in zip(raw_module['phases'],module['levels'],strict=True):
    assert raw['parts']==current['parts'] and raw['equipLevel']==current['level']
    assert {b['key']:b['value'] for b in raw['attributeBlackboard']}==current['attributes']
selections=[]
for scenario in ({'elite':0,'level':1,'potential':1},{'elite':1,'level':1,'potential':1},
                 {'elite':2,'level':1,'potential':4},{'elite':2,'level':1,'potential':5},
                 {'elite':2,'level':59,'potential':5,'module_id':module['id'],'module_level':3},
                 {'elite':2,'level':60,'potential':5,'module_id':module['id'],'module_level':3}):
    chosen,parts=selected_talents(projected,scenario)
    assert any(t['name']=='扶摇花火' for t in chosen)==(scenario['elite']==2)
    selections.append({'scenario':scenario,'selected_talents':chosen,'module_parts':parts})
engine=(OUT/'frozen/rouge/operator_engine.py').read_text()
start=engine.index("        elif op=='char_4202_haruka':")
end=engine.index('\n        elif ',start+1)
consumer=engine[start:end]
assert engine.count("self.s.get('haruka_repeat',False)")==1
assert ("            if normal:regular('magic')\n            else:\n                if self.n==2:\n"
        "                    repeat=self.s.get('haruka_repeat',False)") in consumer
assert "attack=self.base*(1+self.atk_bonus+(bb['atk'] if repeat else 0))+self.atk_flat" in consumer
assert "if repeat:mode='infinite';duration=window if window is not None else 30" in consumer
assert "bursts=self.option('bubble_bursts',0,maximum=10000,integer=True)" in consumer
options=(OUT/'frozen/rouge/operator_options.py').read_text()
app=(OUT/'frozen/rouge/app.py').read_text()
assert "('haruka_repeat','二技能第二次及以后开启',False,1,(2,))" in options
assert 'widget=QCheckBox(label);widget.setChecked(default)' in app
assert 'scenario[key]=widget.isChecked() if isinstance(widget,QCheckBox) else widget.value()' in app
damage=(OUT/'frozen/rouge/damage.py').read_text()
tree=ast.parse(damage)
function=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_evaluate_damage_once')
assert isinstance(function.body[-1],ast.Return)
assert "result['report'] = build_report(scenario, result)"==ast.unparse(function.body[-2])
receipt={'passed':True,'status':'SOURCE_CLOSED_NO_NEW_MECHANISM','baseline_commit':freeze['baseline_commit'],
         'source_commit':'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add','source_files':proofs,
         'complete_raw_character':owner,'complete_raw_s2_skill':raw_skill,'s2_rank_bindings':levels,
         'complete_raw_module':raw_module,'complete_raw_module_meta':raw_meta,
         'actual_source_helper_selections':selections,'actual_consumer':consumer,
         'active_gate':'actual char_4202_haruka + skill2 + nonnormal plan; S2 unlocked E1L1, independent of E2-only 扶摇花火',
         'inactive_gates':['normal plan','S1','S3','other owners'],
         'actual_ui':'False QCheckBox default, S2 only, isChecked boolean producer; no GUI executed',
         'proposed_guard_location':'_evaluate_damage_once after all existing finishers and completed build_report, before return',
         'priority_basis':'Existing cultivation, healing count, bubble_bursts, timing, initialsp, finish and report validation execute first; outer deployment/wine paths must be checked by actual public comparisons.',
         'proposed_behavior':'Reject all raw str for qualified public HarukaS2 only; preserve every old nontext truthiness, inactive fields and exact old errors. Do not parse or define textual true/false.',
         'existing_source_used':['research/p2-haruka-bubble-talent-qualification/NOTE.md',
                                 'rouge/haruka_healing_reference.py','tests/test_haruka_bubble_talent_qualification.py',
                                 'tests/test_haruka_healing_targets.py','tests/test_haruka_event_reference.py'],
         'unknowns_retained':['BLS-Y native composition','extra recipient acquisition', 'unplaced bubble timing',
                              'neighbor coverage','actual repeat acquisition or clock','native attachment and live state'],
         'new_calculate_damage_calls':0,'gui_executed':False,'wine_executed':False,'tracked_edits':False}
(OUT/'source-receipt84.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'passed':True,'s2_ranks':10,'actual_helper_selections':6,
                  'source_sha256':hashlib.sha256((OUT/'source-receipt84.json').read_bytes()).hexdigest()}))
