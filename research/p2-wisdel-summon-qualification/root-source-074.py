import contextlib, hashlib, io, json, runpy, sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
sys.argv=['root-current-source.py','74','char_1035_wisdel']
out=io.StringIO()
with contextlib.redirect_stdout(out):
    runpy.run_path('/workspace/.continuation/root-current-source.py',run_name='__main__')
base=json.loads(out.getvalue())
char=json.loads(Path('.cache/p2-s1-binding/character_table.json').read_bytes())
skill=json.loads(Path('.cache/p2-s1-binding/skill_table.json').read_bytes())
d=json.loads(Path('rouge/data/wisdel-summon-qualification-reference.json').read_bytes())
c=char[d['operator_id']]; t=c['talents'][1]['candidates']; assert len(t)==1
t=t[0]; r=d['talent_route']; s=c['skills'][2]; q=d['skill_route']
assert d['schema_version']==1 and d['operator_id']=='char_1035_wisdel'
assert d['token_id']==t['tokenKey']==s['overrideTokenKey']=='token_10035_wisdel_wward'
assert (r['name'],r['description'],r['prefab_key'],r['required_potential_rank'],r['token_key'])==(t['name'],t['description'],t['prefabKey'],t['requiredPotentialRank'],t['tokenKey'])
assert (r['source_selector'],q['source_selector'])==('character_table.char_1035_wisdel.talents[1].candidates[0]','character_table.char_1035_wisdel.skills[2]')
assert (r['unlock_elite'],r['unlock_level'],t['unlockCondition'])==(2,1,{'phase':'PHASE_2','level':1})
assert (q['skill_number'],q['skill_id'],q['override_token_key'],q['unlock_elite'],q['unlock_level'],s['unlockCond'])==(3,s['skillId'],s['overrideTokenKey'],2,1,{'phase':'PHASE_2','level':1})
levels=skill[s['skillId']]['levels'];assert len(q['levels'])==len(levels)==10
for rank,(actual,original) in enumerate(zip(q['levels'],levels),1):
    assert actual=={'rank':rank,'source_selector':f'skill_table.skchr_wisdel_3.levels[{rank-1}]','description':original['description'],'values':{x['key']:x['value'] for x in original['blackboard']}}
    assert all(fragment in original['description'] for fragment in q['original_common_fragments'])
for name,row in d['sources'].items():
    raw=(Path('.cache/p2-s1-binding')/(name+'.json')).read_bytes()
    assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256']==base['raw_hashes'][name]
    assert d['source_commit']=='a550f5e048bb94e7cdefc6eb97a4091f0c4c7add' and d['source_commit'] in row['url']
print(json.dumps({**base,'summon_route_raw_binding_verified':True,'rank_specific_descriptions_and_common_fragments_verified':10,'cultivation_source_only':True,'actual_provenance_presence_cast_clock_and_all_routes_verified':False},ensure_ascii=False))
