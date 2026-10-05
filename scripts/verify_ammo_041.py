"""Current regressions, fresh before/after public outputs and ammo source audit."""
import hashlib,json,sys,time,unittest
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from rouge.damage import calculate_damage
from rouge.catalog import catalog
from rouge.relics import mechanics
from rouge.offline_scope import scope_counts


def digest(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()


def main():
    started=time.perf_counter();folder=ROOT/'.cache/ammo-041'
    prior=json.loads((ROOT/'BATTLE_0.40_VERIFICATION.json').read_text(encoding='utf-8'))
    names=prior['test_modules']+['tests.test_ammo_refill_041']
    with (folder/'tests.log').open('w',encoding='utf-8') as log:
        tests=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(names))
    assert tests.wasSuccessful(),str(folder/'tests.log')
    assert tests.testsRun-len(tests.skipped)==383 and len(tests.skipped)==70
    rows=json.loads((folder/'before-public-results.json').read_text(encoding='utf-8'))
    for i,row in enumerate(rows,1):
        assert calculate_damage(row['scenario'])==row['result'],row['scenario']
        if i%100==0:print(json.dumps({'exact_old_public_outputs':i}),flush=True)
    assert len(rows)==732
    counts=Counter();numeric_changes=Counter();after=[]
    before=json.loads((folder/'before-book-results.json').read_text(encoding='utf-8'))
    for row in before:
        s=row['scenario'];old=row['result'];r=calculate_damage(s);after.append({'scenario':s,'result':r})
        same=r==old;counts['exact_same' if same else 'changed']+=1
        assert r['estimate']['base_stats']==old['estimate']['base_stats'],s
        source=catalog()['operators'][s['operator']]['skills'][s['skill']-1]['levels'][s['skill_rank']-1]
        if source['duration_type']!='AMMO':
            counts['non_ammo_unchanged']+=1;assert same,s
            continue
        counts['ammo_scenarios']+=1
        for key in ('total_damage','total_healing','duration_seconds','cycle_seconds','cycle_dps','cycle_hps'):
            if r['estimate']['skill'][key]!=old['estimate']['skill'][key]:numeric_changes[key]+=1
        op=s['operator'];n=s['skill'];ids=s['relic_ids']
        known=((op,n) in (('kaltsit',2),('mechanist',1),('char_1035_wisdel',3),('char_1041_angel2',1)) or
            (op,n)==('char_1041_angel2',3) and ids==['rogue_6_relic_legacy_140']) and len(ids)==1
        if not known:
            counts['unknown_skill_reference']+=1
            assert not r['relic_resolution']['complete']
            assert r['relic_resolution']['rules']==[],s
            for key in ('total_damage','duration_seconds','cycle_seconds','cycle_dps'):
                assert r['estimate']['skill'][key] is None,(s,key)
            continue
        counts['known_ammo_reference']+=1
        assert r['relic_resolution']['complete'],s
        half=ids[0].endswith('140')
        expected={('kaltsit',2):(14,15),('mechanist',1):(3,3),
            ('char_1035_wisdel',3):(8,9),('char_1041_angel2',1):(11,12),('char_1041_angel2',3):(None,75)}[(op,n)][half]
        if op=='mechanist':actual=r['hits']//5;counts['known_no_effect']+=1
        elif op=='kaltsit':actual=r['hits'];counts['positive_refill']+=1
        else:
            name='维什戴尔主攻击' if op=='char_1035_wisdel' else '技能攻击'
            actual=r['estimate']['skill']['hit_counts'][name];counts['positive_refill']+=1
        assert actual==expected,(s,actual,expected)
        assert any(b['id']=='ammo_refill_reference' for b in r['report']['sections']),s
    assert len(before)==1008 and counts['non_ammo_unchanged']==468 and counts['ammo_scenarios']==540
    assert counts['known_ammo_reference']==180 and counts['unknown_skill_reference']==360
    assert counts['known_no_effect']==40 and counts['positive_refill']==140
    (folder/'after-book-results.json').write_text(json.dumps(after,ensure_ascii=False),encoding='utf-8')
    sources=json.loads((ROOT/'.cache/research/ammo-041/source-receipt.json').read_text(encoding='utf-8'))
    for name,row in sources['files'].items():
        body=(ROOT/'.cache/research/ammo-041'/name).read_bytes()
        assert len(body)==row['bytes'] and hashlib.sha256(body).hexdigest()==row['sha256'],name
        assert hashlib.sha1(b'blob '+str(len(body)).encode()+b'\0'+body).hexdigest()==row['git_blob'],name
    raw=json.loads((ROOT/'.cache/research/ammo-041/data_buff_templates.json').read_text(encoding='utf-8'))
    excerpt=json.loads((ROOT/'.cache/research/ammo-041/ammo-template-excerpt.json').read_text(encoding='utf-8'))
    assert {k:raw[k] for k in excerpt}==excerpt
    manifest=json.loads((ROOT/'.cache/batch-041-before/manifest.json').read_text(encoding='utf-8'))
    assert digest('rouge/data/relic-mechanics.json')==manifest['rouge/data/relic-mechanics.json']
    for name,sha in prior['source_hashes'].items():
        if name in ('rouge/battle_preview.py','rouge/battle_view.py','rouge/spawn_reference.py','rouge/data/battle-previews.json'):
            assert digest(name)==sha,name
    files=('rouge/ammo_reference.py','rouge/data/ammo-refill-reference.json','rouge/relics.py',
        'rouge/relic_events.py','rouge/damage.py','rouge/operator_engine.py','rouge/reporting.py',
        'tests/test_ammo_refill_041.py','tests/test_relic_extension.py','scripts/verify_ammo_041.py',
        'rouge/data/relic-mechanics.json','pyproject.toml')
    receipt={'version':'0.41.0','passed':True,'verified_at':time.time(),
        'tests_run':tests.testsRun,'current_tests_passed':383,'new_tests':24,'historical_combat_tests_skipped':70,
        'failures':len(tests.failures),'errors':len(tests.errors),'test_modules':names,
        'exact_public_output_cases':732,'public_baseline_outputs_unchanged':True,
        'book_cases':len(before),'book_comparison':dict(counts),'book_metric_changes':dict(numeric_changes),
        'source_files_sha256_and_git_blob_verified':True,'raw_relic_data_unchanged':True,
        'battle_source_and_ui_unchanged':True,'data_rule_counts':mechanics()['counts'],'offline_scope':scope_counts(mechanics()),
        'source_hashes':{name:digest(name) for name in files},
        'test_log':'.cache/ammo-041/tests.log','test_log_sha256':digest('.cache/ammo-041/tests.log'),
        'baseline_hashes':{n:digest(n) for n in ('.cache/ammo-041/before-public-results.json',
            '.cache/ammo-041/before-book-results.json','.cache/ammo-041/after-book-results.json')},
        'elapsed_seconds':time.perf_counter()-started,'chat_requests':0,'game_actions':0,'private_state_used':False,
        'limits':['Count references use only the two sourced ratios; not a generic fixed-point emulator.',
            'Polling phase and client frames are not calibrated; four frames are a conservative reference bound.',
            'Dynamic max ammo, special consumption/partial packets and multi-book acquisition order remain unknown.',
            'No new recognition timing or inventory-accuracy measurement. P1-P3 remain incomplete.']}
    (ROOT/'AMMO_0.41_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ('passed','current_tests_passed','exact_public_output_cases',
        'book_cases','book_comparison','book_metric_changes','elapsed_seconds')}),flush=True)


if __name__=='__main__':main()
