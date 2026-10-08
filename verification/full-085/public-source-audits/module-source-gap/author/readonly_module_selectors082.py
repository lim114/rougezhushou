"""Bounded novel semantic module-selector audit; no API or tracked writes."""
import hashlib,json,subprocess
from pathlib import Path

repo=Path('/workspace/rougezhushou')
out=Path('/workspace/.continuation/p2-module-source-gap-082-author');out.mkdir(exist_ok=True)
head='c950fbc800245f7f784d6070f7126890352ffcc9'
catalog_bytes=subprocess.check_output(['git','show',head+':rouge/data/catalog.json'],cwd=repo)
cat=json.loads(catalog_bytes)
sources={};tables={}
for name,path,expected in (
 ('character_table',repo/'.cache/p2-s1-binding/character_table.json','68e3a3b5ee0d407ce234afaa5867c6fda6379a6843c7d5317a7bbda4779f8697'),
 ('char_patch_table',Path('/workspace/.continuation/p2-after-076-condition-eligibility-audit/char_patch_table.json'),'d1850d5aeec1a9246a0531e88c167e66745644957662c8272fc764f54904c57e'),
 ('battle_equip_table',Path('/workspace/.continuation/p2-after-070-source-audit/originals/battle_equip_table.json'),'006687f201a823abf31c6a1c57b2269099bd3ea375c2ec3ae5595cc98a1ec460')):
 data=path.read_bytes();sha=hashlib.sha256(data).hexdigest();assert sha==expected
 tables[name]=json.loads(data);sources[name]={'path':str(path),'sha256':sha,'bytes':len(data)}
originals={**tables['character_table'],**tables['char_patch_table']['patchChars']}
profiles=[];empty=[];missing_fields=[];scoped=[]
for profile in cat['operators'].values():
 raw=originals.get(profile['id'])
 if not raw:continue
 names_checked=0
 for index,group in enumerate(profile['talents']):
  names={c['name'] for c in group}
  if not names:
   empty.append({'operator':profile['id'],'index':index});continue
  original_indices=[i for i,g in enumerate(raw.get('talents') or [])
                    if names & {c.get('name') for c in g['candidates']}]
  assert original_indices==[index],(profile['id'],index,original_indices)
  names_checked+=1
 profiles.append({'operator':profile['id'],'named_groups_checked':names_checked,
                  'catalog_groups':len(profile['talents']),'original_groups':len(raw.get('talents') or [])})
 for module in profile['modules']:
  for stage in module['levels']:
   original_parts=tables['battle_equip_table'][module['id']]['phases'][stage['level']-1]['parts']
   # Raw part identity is needed for this semantic selector audit; do not
   # repeat the prior 34/102 qualification/static-attribute matrix.
   assert stage['parts']==original_parts
   for part_index,part in enumerate(stage['parts']):
    selector=f"battle_equip_table.{module['id']}.phases[{stage['level']-1}].parts[{part_index}]"
    if part.get('validInGameTag') is not None or part.get('validInMapTag') is not None:
     scoped.append({'operator':profile['id'],'module':module['id'],'stage':stage['level'],
                    'selector':selector,'raw_part':part})
    if part['target']!='TALENT_DATA_ONLY' or part.get('isToken'):continue
    for candidate_index,c in enumerate((part.get('addOrOverrideTalentDataBundle') or {}).get('candidates') or []):
     i=c['talentIndex']
     if not 0<=i<len(profile['talents']):continue
     previous=[t for t in profile['talents'][i] if t['phase']<=2 and t['potential_rank']<=c['requiredPotentialRank']]
     if not previous:continue
     prior=previous[-1];missing=set(prior['values'])-{b['key'] for b in c['blackboard']}
     if missing:
      missing_fields.append({'operator':profile['id'],'module':module['id'],'stage':stage['level'],
                             'selector':selector+f'.addOrOverrideTalentDataBundle.candidates[{candidate_index}]',
                             'original_talent':prior,'candidate':c,'missing_prior_keys':sorted(missing)})
assert {row['operator'] for row in missing_fields}<= {'char_206_gnosis','char_437_mizuki'}
receipt={'status':'READONLY_NO_CONFIRMED_NEW_DEFECT','baseline_commit':head,'source_commit':'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add',
         'sources':sources,'catalog_sha256':hashlib.sha256(catalog_bytes).hexdigest(),
         'original_group_identity_checks':profiles,'empty_catalog_groups_preserved':empty,
         'all_named_group_indices_match_original':True,
         'data_only_candidates_missing_previous_keys':missing_fields,
         'scoped_module_parts':scoped,
         'conclusions':['No compacted original-talent-index bug: null-name source groups remain empty placeholders.',
                        'Only pre-existing Gnosis/Mizuki ISW-A special # bundles lack prior keys. Existing specialized guards/replacements already handle them; no generic merge or native attachment inference is authorized.',
                        'Scoped parts exist only on current catalog mechanical/Gnosis/Mizuki IS modules. Current product only has Blackflow run configuration; no confirmed public other-mode mapping was found. Raw tags alone do not establish a new game-mode consumer.'],
         'new_public_API_calls':0,'new_tests':0,'GUI_or_Wine_executed':False,'tracked_mutations':False,
         'prior_negative_static_audit_not_repeated':'No 34/102 module qualification/static numeric matrix.',
         'is_numbered_section_completion':False}
(out/'semantic-selector-readonly082.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
(out/'catalog-frozen082.json').write_bytes(catalog_bytes)
print(json.dumps({'profiles':len(profiles),'named_groups':sum(p['named_groups_checked'] for p in profiles),
                 'empty_preserved_groups':len(empty),'missing_prior_key_candidates':len(missing_fields),
                 'scoped_parts':len(scoped),'new_API_calls':0}))
