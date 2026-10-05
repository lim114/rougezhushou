"""Evidence-scoped changes, current regression and exact public baseline."""
import hashlib,json,subprocess,sys,time,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from rouge.damage import calculate_damage

def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8'))
def sha(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()

def main():
    start=time.perf_counter();folder=ROOT/'.cache/relics-052';folder.mkdir(exist_ok=True)
    old_receipt=read('FINAL_0.51_VERIFICATION.json')
    allowed={'rouge/app.py','rouge/relics.py','rouge/reporting.py','rouge/run_modifiers.py',
        'rouge/data/relic-mechanics.json','scripts/build_relic_mechanics.py','pyproject.toml','tests/test_spawn_hp_033.py'}
    changed={n.replace('\\','/') for n,h in old_receipt['source_sha256'].items() if sha(n)!=h}
    assert changed<=allowed,changed-allowed
    before=read('.cache/batch-052-before/manifest.json');assert len(before)==11
    assert all(sha('.cache/batch-052-before/'+n)==h for n,h in before.items())
    old=read('.cache/batch-052-before/rouge/data/relic-mechanics.json');new=read('rouge/data/relic-mechanics.json')
    assert old['char_buffs']==new['char_buffs'] and old['counts']==new['counts']
    assert set(old['relics'])==set(new['relics'])
    ids={rid for rid in old['relics'] if old['relics'][rid]!=new['relics'][rid]}
    assert ids=={'rogue_6_relic_fight_30','rogue_6_relic_hand_4','rogue_6_start_3'},ids
    for rid in ids:
        previous=old['relics'][rid];current=new['relics'][rid]
        assert previous['pending']==current['pending'] and previous['status']==current['status']
        expected=json.loads(json.dumps(current))
        expected.pop('pending_scopes',None)
        for effect in expected['effects']:
            for name in ('hp_composition','hp_template_key','hp_template_source','hp_template_sha256'):effect.pop(name,None)
        baseline=json.loads(json.dumps(previous));baseline.pop('pending_scopes',None)
        assert expected==baseline,rid
    source='rouge/data/relic-mechanics.json';data_sha=sha(source)
    for index in range(2):
        log=folder/f'build-{index+1}.log'
        with log.open('x',encoding='utf-8') as stream:
            p=subprocess.run([sys.executable,'scripts/build_relic_mechanics.py'],cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT)
        assert p.returncode==0 and sha(source)==data_sha,log
    modules=[*read('INVENTORY_0.51_VERIFICATION.json')['test_modules'],
        'tests.test_relic_stack_052','tests.test_relic_scope_052','tests.test_relic_resolution_052']
    attempt=1
    while (folder/f'all-tests-{attempt}.log').exists():attempt+=1
    log=folder/f'all-tests-{attempt}.log'
    with log.open('x',encoding='utf-8') as stream:
        result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(modules))
    assert result.wasSuccessful(),[(t.id(),error[-2000:]) for t,error in [*result.errors,*result.failures]]
    assert len(result.skipped)==70
    baseline_receipt=read('P1_0.50_VERIFICATION.json');baseline=baseline_receipt['fresh_previous_public_baseline']
    assert sha(baseline)==baseline_receipt['fresh_previous_public_baseline_sha256']
    rows=read(baseline);assert len(rows)==732
    for i,row in enumerate(rows,1):
        assert calculate_damage(row['scenario'])==row['result'],row['scenario']
        if i%100==0:print(json.dumps({'exact_default_replays':i}),flush=True)
    names={n.replace('\\','/') for n in old_receipt['source_sha256']}|allowed
    names|={p.relative_to(ROOT).as_posix() for base in ('tests','scripts') for p in (ROOT/base).glob('*052.py')}
    # Final sealing may be authored after this run; validated source and test
    # hashes stay fixed. The final driver is sealed as an artifact separately.
    names.discard('scripts/verify_final_052.py')
    receipt={'version':'0.52.0','passed':True,'tests_run':result.testsRun,
        'current_tests_passed':result.testsRun-len(result.skipped),'new_unit_tests':result.testsRun-693,
        'historical_combat_tests_skipped':len(result.skipped),'test_modules':modules,
        'failures':len(result.failures),'errors':len(result.errors),'test_log':log.relative_to(ROOT).as_posix(),
        'test_log_sha256':sha(log.relative_to(ROOT)),'exact_default_public_replays':len(rows),
        'default_public_outputs_unchanged':True,'numeric_public_replay_rerun':True,
        'baseline_receipt':'P1_0.50_VERIFICATION.json','baseline_receipt_sha256':sha('P1_0.50_VERIFICATION.json'),
        'baseline_file':baseline,'baseline_file_sha256':sha(baseline),'deterministic_builds':2,
        'changed_relic_entries':sorted(ids),'char_buff_formulas_unchanged':True,'data_status_counts_unchanged':True,
        'changed_existing_sources':sorted(changed),'source_sha256':{n:sha(n) for n in sorted(names)},
        'game_actions':0,'chat_requests':0,'live_measurements':0,'new_recognition_speed_claim':False,
        'seconds':time.perf_counter()-start}
    (ROOT/'RELICS_0.52_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in receipt.items() if k not in ('source_sha256','test_modules')},ensure_ascii=True))

if __name__=='__main__':main()
