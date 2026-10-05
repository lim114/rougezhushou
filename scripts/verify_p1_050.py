"""P1 regression, deterministic derivation and isolated public baseline replay."""
import hashlib,inspect,json,shutil,subprocess,sys,tempfile,time,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from capture_phase_baseline_036 import scenarios
from rouge.damage import calculate_damage


def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8'))
def digest(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()


def fresh_before(folder):
    with tempfile.TemporaryDirectory() as directory:
        temp=Path(directory);package=temp/'rouge';package.mkdir()
        for source in (ROOT/'rouge').glob('*.py'):shutil.copy2(source,package/source.name)
        (package/'data').mkdir()
        for source in (ROOT/'rouge/data').glob('*.json'):shutil.copy2(source,package/'data'/source.name)
        backup=ROOT/'.cache/batch-050-before/rouge'
        for source in backup.glob('*.py'):shutil.copy2(source,package/source.name)
        for source in (backup/'data').glob('*.json'):shutil.copy2(source,package/'data'/source.name)
        target=folder/'before-default-results.json'
        driver=temp/'capture.py'
        driver.write_text('import json,sys\nfrom pathlib import Path\nfrom rouge.catalog import catalog\n'
            'from rouge.damage import calculate_damage\n'+inspect.getsource(scenarios)+
            "\nrows=[]\nfor i,s in enumerate(scenarios(),1):\n rows.append({'scenario':s,'result':calculate_damage(s)})\n"
            " if i%100==0:print(i,flush=True)\n"
            "Path(sys.argv[1]).write_text(json.dumps(rows,ensure_ascii=False),encoding='utf-8')\n",
            encoding='utf-8')
        log=folder/'fresh-before.log'
        with log.open('x',encoding='utf-8') as stream:
            result=subprocess.run([sys.executable,str(driver),str(target)],cwd=temp,stdout=stream,stderr=subprocess.STDOUT)
        assert result.returncode==0,log
    return target


def main():
    started=time.perf_counter();folder=ROOT/'.cache/p1-050';folder.mkdir(exist_ok=True)
    previous=read('FINAL_0.49_VERIFICATION.json')
    allowed={'rouge/app.py','rouge/relics.py','rouge/run_state.py','rouge/reporting.py',
             'rouge/data/relic-mechanics.json','scripts/build_relic_mechanics.py','pyproject.toml'}
    changed={n.replace('\\','/') for n,sha in previous['source_sha256'].items() if digest(n)!=sha}
    assert changed<=allowed,changed-allowed
    backup=read('.cache/batch-050-before/manifest.json')
    assert all(digest('.cache/batch-050-before/'+n)==sha for n,sha in backup.items())
    old=read('.cache/batch-050-before/rouge/data/relic-mechanics.json')
    new=read('rouge/data/relic-mechanics.json');ids={'rogue_6_relic_assign_'+str(n) for n in (5,7,9,10,12,13,15)}
    assert old['char_buffs']==new['char_buffs']
    assert set(old['relics'])==set(new['relics'])
    changed_items={rid for rid,item in old['relics'].items() if item!=new['relics'][rid]}
    assert changed_items==ids,changed_items
    for rid in ids:
        expected=dict(old['relics'][rid]);expected.update(status='conditional',pending=[])
        entry=dict(new['relics'][rid]);binding=entry.pop('recipient_binding')
        assert entry==expected,rid
        assert binding['scope']=='current_operator_only' and binding['effect_path']=='char_buff_only'
    target='rouge/data/relic-mechanics.json';first=digest(target)
    attempt=1
    while (folder/f'deterministic-build-{attempt}.log').exists():attempt+=1
    for attempt in range(attempt,attempt+2):
        log=folder/f'deterministic-build-{attempt}.log'
        with log.open('x',encoding='utf-8') as stream:
            result=subprocess.run([sys.executable,'scripts/build_relic_mechanics.py'],cwd=ROOT,
                stdout=stream,stderr=subprocess.STDOUT)
        assert result.returncode==0 and digest(target)==first,log
    modules=[*read('ROUTES_0.49_VERIFICATION.json')['test_modules'],
             'tests.test_relic_reading_050','tests.test_recipient_binding_050']
    attempt=1
    while (folder/f'all-tests-{attempt}.log').exists():attempt+=1
    log=folder/f'all-tests-{attempt}.log'
    with log.open('x',encoding='utf-8') as stream:
        tests=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(modules))
    assert tests.wasSuccessful(),[(t.id(),error[-1800:]) for t,error in [*tests.errors,*tests.failures]]
    assert len(tests.skipped)==70
    before=folder/'before-default-results.json'
    if not before.exists():before=fresh_before(folder)
    rows=json.loads(before.read_text(encoding='utf-8'));assert len(rows)==732
    for i,row in enumerate(rows,1):
        assert calculate_damage(row['scenario'])==row['result'],row['scenario']
        if i%100==0:print(json.dumps({'exact_default_replays':i}),flush=True)
    names={n.replace('\\','/') for n in previous['source_sha256']}|allowed
    names|={str(p.relative_to(ROOT)) for base in ('scripts','tests') for p in (ROOT/base).glob('*050.py')}
    result={'version':'0.50.0','passed':True,'tests_run':tests.testsRun,
        'current_tests_passed':tests.testsRun-len(tests.skipped),'new_unit_tests':tests.testsRun-640,
        'historical_combat_tests_skipped':len(tests.skipped),'failures':len(tests.failures),'errors':len(tests.errors),
        'test_modules':modules,'test_log':str(log.relative_to(ROOT)),'test_log_sha256':digest(str(log.relative_to(ROOT))),
        'fresh_previous_public_baseline':str(before.relative_to(ROOT)),
        'fresh_previous_public_baseline_sha256':digest(str(before.relative_to(ROOT))),
        'exact_default_public_replays':len(rows),'default_public_outputs_unchanged':True,'numeric_public_replay_rerun':True,
        'deterministic_builds':2,'stable_binding_parent_entries':len(ids),'char_buff_formulas_unchanged':True,
        'changed_existing_source_files':sorted(changed),'source_sha256':{n:digest(n) for n in sorted(names)},
        'live_measurements':0,'new_recognition_speed_claim':False,'game_actions':0,'chat_requests':0,
        'seconds':time.perf_counter()-started}
    (ROOT/'P1_0.50_VERIFICATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('source_sha256','test_modules')},ensure_ascii=False))


if __name__=='__main__':main()
