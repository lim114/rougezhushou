"""Retain raw level definitions separately; never guess list/skill inheritance."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from rouge.battle_preview import battle_data
FIELDS=('skills','spData','talentBlackboard')

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    data=battle_data();source=data['source']['enemy_database']
    path=ROOT/'.cache/game-data/levels/enemydata/enemy_database.json'
    assert digest(path)==source['sha256']
    raw={r['Key']:r['Value'] for r in json.loads(path.read_text(encoding='utf-8'))['enemies']}
    ids={e['id'] for s in data['stages'].values() for e in s['enemies']}
    definitions={};bindings={};refs=0;overrides=0
    for eid in sorted(ids):
        definitions[eid]={}
        for record in raw.get(eid,[]):
            level=str(record['level']);assert level not in definitions[eid]
            d=record['enemyData']
            definitions[eid][level]={key:d[key] for key in FIELDS if key in d}
    for sid,stage in data['stages'].items():
        path=ROOT/'.cache/game-data/levels'/stage['level_source']['url'].split('/levels/',1)[-1]
        assert digest(path)==stage['level_source']['sha256'],sid
        rawrefs=json.loads(path.read_text(encoding='utf-8'))['enemyDbRefs'];bindings[sid]={}
        for enemy in stage['enemies']:
            found=[r for r in rawrefs if r['id']==enemy['id'] and r['level']==enemy['level']]
            assert len(found)==1,(sid,enemy['id'],enemy['level'])
            overwrite=found[0].get('overwrittenData') or {}
            patch={key:overwrite[key] for key in FIELDS if key in overwrite and overwrite[key] is not None}
            bindings[sid][enemy['id']+'@'+str(enemy['level'])]={'stage_overrides':patch}
            overrides+=bool(patch);refs+=1
    result={'schema_version':1,'source':{'game_commit':data['source']['game_commit'],'enemy_database':source},
        'binding_rule':'Stage + enemy ID + reference level. Raw definitions stay per level; no skill/null/list inheritance is inferred.',
        'definitions':definitions,'bindings':bindings}
    output=ROOT/'rouge/data/enemy-skill-references.json'
    output.write_text(json.dumps(result,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    receipt={'version':'0.42.0','stages':len(bindings),'enemy_references':refs,'enemy_ids':len(ids),
        'level_definitions':sum(len(v) for v in definitions.values()),
        'skill_entries':sum(len(d.get('skills') or []) for v in definitions.values() for d in v.values()),
        'definitions_with_skills':sum(bool(d.get('skills')) for v in definitions.values() for d in v.values()),
        'definitions_with_sp':sum(bool(d.get('spData')) for v in definitions.values() for d in v.values()),
        'stage_skill_overrides':overrides,'data_sha256':digest(output),'source':result['source'],
        'skill_lists_not_merged':True,'actual_activation_times_verified':False,'source_all_fields_exact':True}
    folder=ROOT/'.cache/research/enemy-skills-042';folder.mkdir(parents=True,exist_ok=True)
    (folder/'data-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(receipt,ensure_ascii=True))

if __name__=='__main__':main()
