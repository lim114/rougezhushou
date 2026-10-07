"""Read-only local source audit. Writes only adjacent audit artifacts."""
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from rouge.damage import calculate_damage

ROOT=Path('/workspace/rougezhushou')
DEST=Path('/workspace/.continuation/p2-after-050/finite-positive-source')
def read(path):return json.loads((ROOT/path).read_text(encoding='utf-8'))
def manifest(path):
 p=ROOT/path
 return {'path':str(p),'exists':p.is_file(),**({'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} if p.is_file() else {})}
character=read('.cache/p2-s1-binding/character_table.json')
skills=read('.cache/p2-s1-binding/skill_table.json')
profiles=read('rouge/data/timing-profiles.json')
references=read('rouge/data/original-animation-references.json')
old=read('research/p2-empty-enemy-scope/source-receipt.json')
phase=read('research/p2-phase-guards/source-receipt.json')
selectors={
 'character_table.char_002_amiya.skills[0].skillId':character['char_002_amiya']['skills'][0]['skillId'],
 'character_table.char_002_amiya.phases[2].attributesKeyFrames[-1].data.baseAttackTime':character['char_002_amiya']['phases'][2]['attributesKeyFrames'][-1]['data']['baseAttackTime'],
 'character_table.char_002_amiya.talents[0].candidates[1]':character['char_002_amiya']['talents'][0]['candidates'][1],
 'skill_table.skcom_magic_rage[3].levels[9]':skills['skcom_magic_rage[3]']['levels'][9],
 'timing-profiles.operators.char_002_amiya':profiles['operators']['char_002_amiya'],
 'original-animation-references.operators.char_002_amiya.Attack_records':[
  record for record in references['operators']['char_002_amiya']['records']
  if record['animation']=='Attack' and record['selectable_as_conventional_reference']]
}
comparisons={key:old['selectors'].get(key)==selectors[key] for key in ['skill_table.skcom_magic_rage[3].levels[9]']}
source_files=['.cache/p2-s1-binding/character_table.json','.cache/p2-s1-binding/skill_table.json','rouge/data/original-animation-references.json','rouge/data/timing-profiles.json']
original_files=['.cache/research/timing/arkdps_data_collection/customdata/dps_anim.json']
receipt={
 'captured_at_utc':datetime.now(timezone.utc).isoformat(),
 'reviewed_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
 'workflow':'Read-only local audit; no tracked edits, network requests, private/game/desktop/chat actions. Artifacts only in adjacent continuation directory.',
 'scope':'Caster Amiya S1 enemy-facing interval reference and post-skill mixed-SP under explicit finite-positive target lifetime or owner target-range constraints. Other skills/friendly/instant sources excluded.',
 'reused_pinned_commit':'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add',
 'sources':{name:manifest(name) for name in source_files},
 'matches_previous_hashes':{name:manifest('.cache/p2-s1-binding/'+name+'.json')['sha256']==old['sources'][name]['sha256'] for name in ['character_table','skill_table']},
 'selectors':selectors,
 'matches_previous_selector':comparisons,
 'existing_receipts':{
  'research/p2-empty-enemy-scope/NOTE.md':{'manifest':manifest('research/p2-empty-enemy-scope/NOTE.md'),'relevant_lines':[17,28,36,42,44],'facts':'Only exact enemy-life-zero boundary closed. Finite-positive continuous lifetime/range retains old parameter reference; no actual acquisition/stop/phase evidence. Deployment initial deliberately separate.'},
  'research/p2-empty-enemy-scope/source-receipt.json':{'manifest':manifest('research/p2-empty-enemy-scope/source-receipt.json'),'source_scope':old['source_scope'],'existing_timing_contract':old['existing_contracts']['rouge/timing.py']['observed_contract'],'limits':old['limits']},
  'research/p2-phase-guards/source-receipt.json':{'manifest':manifest('research/p2-phase-guards/source-receipt.json'),'runtime_binding_verified':phase['runtime_binding_verified'],'fresh_native_verification':phase['fresh_native_verification']},
  'research/p2-mei-s1-reference/NOTE.md':{'manifest':manifest('research/p2-mei-s1-reference/NOTE.md'),'relevant_lines':[7],'facts':'Prior ordinary animation reference was not a runtime attack-selector or actual skill-end proof.'},
  'research/p2-amiya-phase-reference/NOTE.md':{'manifest':manifest('research/p2-amiya-phase-reference/NOTE.md'),'relevant_lines':[20,32],'facts':'Separate S2 receipt establishes reference zero from finite life/short window cannot prove actual zero; no caster S1 native-clock proof.'}
 },
 'original_raw_availability':{name:manifest(name) for name in original_files},
 'source_supports':[
  'Public caster identity char_002_amiya and S1 binding skcom_magic_rage[3].',
  'E2 potential1 attack-enemy credit 2 SP and kill credit 8 SP as separate source parameters; no kills inferred.',
  'S1 rank10 AS +90, nominal duration30, natural-recovery type, SP cost30/init15/increment1.0.',
  'Base ordinary interval1.6 is a parameter, and original visual Attack reference has19-frame OnAttack /53-frame animation. Runtime binding remains false.',
  'Exact zero target lifetime excludes this current enemy source mathematically, independently of phase; owner range exit differs from target disappearance in existing reference contract.'
 ],
 'source_does_not_support':[
  'Current native continuous first release/impact, cooldown/reset phase, current skin or hot-update selector.',
  'Real attack acquisition/reacquisition or stop events at finite-positive target lifetime or owner target-window boundaries.',
  'Applying min(window,lifetime) or dividing range length by interval as actual hits, actual post-skill mixed-SP or actual cycle.',
  'Treating synthetic interval times_seconds as native event timestamps because the field exists.',
  'Treating30/rate natural-only parameter as a proven actual recharge for a positive finite-lifetime source.',
  'Applying this skill-relative post-cast disappearance/range constraint to the deliberately separate deployment initial clock.'
 ],
 'targeted_local_searches':[
  'Read existing empty-enemy and phase receipt contracts, then direct pinned original selectors above.',
  'Search research notes for finite positive/有限正/continuous phase/clock; empty-enemy notes explicitly retain the gap.',
  'Inspect original-animation references binding_status and all selected Amiya Attack records; runtime_binding_verified=false.',
  'Search .cache/research REPORT/native-proof/native-fields for AttackAction/attack interval/first tick/continuous/lifetime; available operator-specific native evidence does not bind caster Amiya S1 continuous clocks.'
 ],
 'fresh_native_verification':False,
 'native_clock_proof_found':False,
 'public_entrypoint':'rouge.damage.calculate_damage',
 'public_cases':[]
}
base={'operator':'char_002_amiya','skill':1,'timing_mode':'continuous','base_attack':1000,'window_seconds':10}
for name,timing in [('default',{}),('life01',{'target_disappears_seconds':.1}),('life1',{'target_disappears_seconds':1}),('range01',{'target_windows':[[0,1]]}),('life0',{'target_disappears_seconds':0}),('rangeEmpty',{'target_windows':[]})]:
 scenario={**base,'timing':timing};result=calculate_damage(scenario)
 receipt['public_cases'].append({'name':name,'scenario':scenario,'result':result})
(DEST/'source-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'artifact':str(DEST/'source-receipt.json'),'public_cases':len(receipt['public_cases']),'source_hash_matches':receipt['matches_previous_hashes'],'source_selector_matches':comparisons,'native_clock_proof_found':False},ensure_ascii=False))
