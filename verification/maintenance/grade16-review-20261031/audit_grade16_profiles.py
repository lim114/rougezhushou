from pathlib import Path
from copy import deepcopy
from collections import Counter
from types import ModuleType
from unittest.mock import patch
import json,sys,time
R=Path.cwd();sys.path.insert(0,str(R))
out=R/'verification/maintenance/grade16-review-20261031/profile-audit-closure';out.mkdir(parents=True,exist_ok=False)
from rouge import current_battle_reference as current,enemy_environment,run_modifiers,battle_preview
from rouge.current_enemy_forecast import forecasts
from rouge.run_config import config_data
from rouge.relic_recognition import resolve_difficulty_icons
p=current.packet();assert p
source=next(r for r in p['version']['source']['records']if r['role']=='current')
details=p['version']['current']['details']
profiles=[r for r in details['difficulties']if r['modeDifficulty']=='NORMAL']
assert [r['grade']for r in profiles]==list(range(17))
assert details['difficultyUpgradeRelicGroups']==config_data()['difficulty_upgrade_relic_groups']
selection={'source':source,'normal_profiles':profiles,'relic_groups':details['difficultyUpgradeRelicGroups'],
 'source_snapshot_not_installed_version_proof':True}
(out/'source-selection.json').write_text(json.dumps(selection,ensure_ascii=False,indent=2)+'\n','utf8')
old={}
for name in('enemy_environment','run_modifiers','battle_preview'):
 mod=ModuleType('rouge.'+name);mod.__package__='rouge';mod.__file__=str(R/'rouge'/(name+'.py'))
 with patch.dict(sys.modules,{'rouge.'+k:v for k,v in old.items()}):
  exec(compile((R/'research/grade16-review-20261031'/('before-'+name+'.py')).read_bytes(),'<own-prior-'+name+'>','exec'),mod.__dict__)
 old[name]=mod
cases=[]
stages=battle_preview.battle_data()['stages']
for tier in('NORMAL','ELITE','BOSS'):
 sid,enemy=next((sid,e)for sid,s in stages.items()for e in s['enemies']if e['level_type']==tier)
 cases.append((sid,enemy))
comparisons=[]
for grade in range(16):
 for sid,enemy in cases:
  config={'difficulty':{'value':grade,'source':'public-old-new-comparison'},'zone':{'id':'zone_6'}}
  with patch.dict(sys.modules,{'rouge.'+k:v for k,v in old.items()}):
   prior=old['battle_preview'].enemy_preview(sid,enemy['id'],enemy['level'],deepcopy(config))
  actual=battle_preview.enemy_preview(sid,enemy['id'],enemy['level'],deepcopy(config))
  assert actual==prior,(grade,sid,enemy)
  comparisons.append({'grade':grade,'stage':sid,'enemy':enemy['id'],'tier':enemy['level_type'],'whole_rich_result_equal':True})
families=[]
for key,group in details['difficultyUpgradeRelicGroups'].items():
 ids=[r['relicId']for r in group['relicData']]
 selected=max(group['relicData'],key=lambda r:r['equivalentGrade'])
 result=resolve_difficulty_icons([{'id':ids[0],'candidates':ids,'confirmed':False}],{'value':16})[0]
 assert result['id']==selected['relicId']and result['difficulty_tier']==selected['equivalentGrade']
 families.append({'family':key,'tier':selected['equivalentGrade'],'resolved':result['id']})
rows=[];counts=Counter();started=time.perf_counter();config={'difficulty':{'value':16},'zone':{'id':'zone_6'}}
with patch.object(current,'packet',return_value=p):
 for sid in details['stages']:
  stage=current.stage_reference(sid);projection=forecasts(stage,config)
  for enemy in stage['enemies']:
   value=projection[enemy['key']];qualified=value['environment_component']is not None
   assert value['complete_current_total']is None
   if qualified:assert value['difficulty_profile_source']['commit']==source['commit']and not value['qualified_inputs']['difficulty_fields_equal']
   counts['qualified'if qualified else'unqualified']+=1
   rows.append({'stage_id':sid,'key':enemy['key'],'qualified':qualified,'environment_component':value['environment_component'],'complete_current_total':None})
assert dict(counts)=={'qualified':1049,'unqualified':1011}and len(rows)==2060
result={'passed':True,'old_new_full_result_comparisons':comparisons,'profile0_to15_unchanged':True,
 'grade16_raw_rate_percent':25,'relic_tier_groups_equal':True,'relic_groups_checked':families,
 'grade16_matrix':{'stages':184,'references':len(rows),'counts':dict(counts),'conditions':config,'rows':rows},
 'complete_current_totals_unknown':True,'independent_game_calibration':False,'elapsed_seconds':time.perf_counter()-started}
(out/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps({'passed':True,'old_new_comparisons':len(comparisons),'grade16_reference_counts':dict(counts),'relic_groups':len(families)}))
