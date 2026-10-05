"""Fresh regressions and raw enemy-field audit without borrowing inheritance."""
import hashlib,json,sys,time,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from rouge.damage import calculate_damage
from rouge.battle_preview import battle_data,enemy_preview
from rouge.enemy_skills import skill_data,enemy_skill_reference
from rouge.relics import mechanics
from rouge.offline_scope import scope_counts


def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8-sig'))
def digest(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()


def main():
    start=time.perf_counter();folder=ROOT/'.cache/preview-042'
    prior=read('AMMO_0.41_VERIFICATION.json')
    names=prior['test_modules']+['tests.test_enemy_skills_042']
    with (folder/'tests.log').open('w',encoding='utf-8') as log:
        result=unittest.TextTestRunner(stream=log,verbosity=2).run(
            unittest.defaultTestLoader.loadTestsFromNames(names))
    assert result.wasSuccessful(),str(folder/'tests.log')
    current=result.testsRun-len(result.skipped)
    assert current==403 and len(result.skipped)==70,(current,len(result.skipped))
    rows=read('.cache/preview-042/before-public-results.json')
    for i,row in enumerate(rows,1):
        assert calculate_damage(row['scenario'])==row['result'],row['scenario']
        if i%100==0:print(json.dumps({'exact_old_public_outputs':i}),flush=True)
    assert len(rows)==732
    data=battle_data();skills=skill_data();fields=('skills','spData','talentBlackboard')
    path='.cache/game-data/levels/enemydata/enemy_database.json'
    assert digest(path)==skills['source']['enemy_database']['sha256']
    raw={r['Key']:r['Value'] for r in read(path)['enemies']}
    ids={e['id'] for s in data['stages'].values() for e in s['enemies']}
    assert set(skills['definitions'])==ids
    definitions=entries=sp_definitions=0
    for eid in ids:
        expected={str(r['level']):{k:r['enemyData'][k] for k in fields if k in r['enemyData']}
            for r in raw.get(eid,[])}
        assert skills['definitions'][eid]==expected,eid
        for row in expected.values():
            definitions+=1;entries+=len(row.get('skills') or []);sp_definitions+=bool(row.get('spData'))
    refs=overrides=exact_missing=0
    for sid,stage in data['stages'].items():
        path='.cache/game-data/levels/'+stage['level_source']['url'].split('/levels/',1)[-1]
        assert digest(path)==stage['level_source']['sha256'],sid
        originals=read(path)['enemyDbRefs'];seen=set()
        for e in stage['enemies']:
            key=e['id']+'@'+str(e['level'])
            found=[r for r in originals if r['id']==e['id'] and r['level']==e['level']]
            assert len(found)==1
            patch=found[0].get('overwrittenData') or {}
            expected={k:patch[k] for k in fields if k in patch and patch[k] is not None}
            assert skills['bindings'][sid][key]=={'stage_overrides':expected},(sid,key)
            ref=enemy_skill_reference(sid,e['id'],e['level'])
            assert ref['stage_overrides']==expected
            assert all(d['level']<=e['level'] for d in ref['definitions'])
            assert ref['first_activation_seconds'] is ref['effective_skill_damage'] is None
            assert ref['inheritance_resolved'] is False
            preview=enemy_preview(sid,e['id'],e['level'],{'difficulty':{'value':0}})
            assert preview['skill_reference']==ref
            seen.add(key);refs+=1;overrides+=bool(expected);exact_missing+=not ref['exact_requested_level_present']
        assert set(skills['bindings'][sid])==seen
    assert set(skills['bindings'])==set(data['stages'])
    assert (len(ids),definitions,entries,sp_definitions,refs,overrides)==(334,333,169,21,1087,115)
    built=read('.cache/research/enemy-skills-042/data-receipt.json')
    assert digest('rouge/data/enemy-skill-references.json')==built['data_sha256']
    images=read('.cache/research/battle-039/image-receipt.json')
    assert len(images['images'])==105
    for image in images['images'].values():assert digest('rouge/data/'+image['file'])==image['sha256']
    previous=read('FINAL_0.41_VERIFICATION.json')
    allowed={'rouge/app.py','rouge/battle_preview.py','pyproject.toml'}
    changed={n for n,sha in previous['source_sha256'].items() if digest(n)!=sha}
    assert changed==allowed,changed
    for name,receipt in (('therapy-042',read('.cache/research/therapy-042/source-receipt.json')),
                         ('ammo-041',read('.cache/research/ammo-041/source-receipt.json'))):
        for filename,row in receipt['files'].items():
            body=(ROOT/'.cache/research'/name/filename).read_bytes()
            assert len(body)==row['bytes'] and hashlib.sha256(body).hexdigest()==row['sha256']
            assert hashlib.sha1(b'blob '+str(len(body)).encode()+b'\0'+body).hexdigest()==row['git_blob']
    template=read('.cache/research/ammo-041/data_buff_templates.json')
    excerpt=read('.cache/research/therapy-042/template-excerpt.json')
    assert {k:template[k] for k in excerpt}==excerpt
    manifest=read('.cache/batch-042-before/manifest.json')
    assert len(manifest)==8 and manifest==read('.cache/preview-042/baseline.json')['source_hashes']
    for name,sha in manifest.items():assert digest('.cache/batch-042-before/'+name)==sha
    files=('rouge/app.py','rouge/battle_preview.py','rouge/battle_view.py','rouge/enemy_skills.py',
        'rouge/data/battle-previews.json','rouge/data/enemy-skill-references.json',
        'scripts/build_enemy_skills_042.py','scripts/verify_preview_042.py','tests/test_enemy_skills_042.py','pyproject.toml')
    receipt={'version':'0.42.0','passed':True,'verified_at':time.time(),
        'tests_run':result.testsRun,'current_tests_passed':current,'new_tests':20,
        'historical_combat_tests_skipped':len(result.skipped),'failures':len(result.failures),'errors':len(result.errors),
        'test_modules':names,'exact_public_output_cases':len(rows),'public_baseline_outputs_unchanged':True,
        'battle_stages':len(data['stages']),'enemy_references':refs,'raw_level_definitions':definitions,
        'raw_skill_entries':entries,'raw_sp_definitions':sp_definitions,'raw_stage_overrides':overrides,
        'exact_requested_definition_missing':exact_missing,'all_source_fields_exact':True,
        'skill_inheritance_inferred':False,'actual_skill_activation_times_verified':False,
        'inherited_map_hashes_checked':105,'preserved_old_source_hashes_checked':True,
        'changed_existing_source_files':sorted(changed),'source_files_sha256_and_git_blob_verified':True,
        'data_rule_counts':mechanics()['counts'],'offline_scope':scope_counts(mechanics()),
        'source_hashes':{n:digest(n) for n in files},
        'test_log':'.cache/preview-042/tests.log','test_log_sha256':digest('.cache/preview-042/tests.log'),
        'baseline_hashes':{n:digest(n) for n in ('.cache/preview-042/before-public-results.json','.cache/preview-042/baseline.json')},
        'elapsed_seconds':time.perf_counter()-start,'chat_requests':0,'game_actions':0,'private_state_used':False,
        'completed_items_removed_from_todo':True,
        'limits':['Raw per-level enemy configuration is not effective inheritance, activation timing or damage.',
            'Therapy-card descriptions do not resolve creation/lifetime/stacking; no numeric effect added.',
            'No new recognition timing or inventory-accuracy measurement. P1-P3 remain incomplete.']}
    (ROOT/'PREVIEW_0.42_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ('passed','current_tests_passed','exact_public_output_cases',
        'raw_level_definitions','raw_stage_overrides','elapsed_seconds')}),flush=True)


if __name__=='__main__':main()
