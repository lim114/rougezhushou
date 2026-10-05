"""Current tests plus exact public replay against backed-up 0.47 sources."""
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
        for source in (ROOT/'.cache/batch-048-before/rouge').glob('*.py'):shutil.copy2(source,package/source.name)
        target=folder/'before-default-results.json'
        driver=temp/'capture.py'
        driver.write_text('import json,sys\nfrom pathlib import Path\nfrom rouge.catalog import catalog\n'
            'from rouge.damage import calculate_damage\n'+inspect.getsource(scenarios)+
            "\nrows=[]\nfor i,s in enumerate(scenarios(),1):\n rows.append({'scenario':s,'result':calculate_damage(s)})\n"
            " if i%100==0:print(i,flush=True)\n"
            "Path(sys.argv[1]).write_text(json.dumps(rows,ensure_ascii=False),encoding='utf-8')\n",
            encoding='utf-8')
        log=folder/'fresh-before.log'
        with log.open('w',encoding='utf-8') as stream:
            result=subprocess.run([sys.executable,str(driver),str(target)],cwd=temp,stdout=stream,stderr=subprocess.STDOUT)
        assert result.returncode==0,log
    return target


def main():
    started=time.perf_counter();folder=ROOT/'.cache/mechanisms-048';folder.mkdir(exist_ok=True)
    previous=read('FINAL_0.47_VERIFICATION.json')
    allowed={'rouge/app.py','rouge/timing.py','rouge/operator_engine.py','rouge/elemental_relics.py',
        'rouge/reporting.py','pyproject.toml','rouge/data/battle-map-projections.json'}
    changed={n for n,sha in previous['source_sha256'].items() if digest(n)!=sha}
    assert changed<=allowed,changed-allowed
    backup=read('.cache/batch-048-before/manifest.json')
    assert all(digest('.cache/batch-048-before/'+n)==sha for n,sha in backup.items())
    modules=[*read('READABILITY_0.47_VERIFICATION.json')['test_modules'],
        'tests.test_original_animation_048','tests.test_bait_unknown_048','tests.test_map_projection_048']
    attempt=1
    while (folder/f'all-tests-{attempt}.log').exists():attempt+=1
    log=folder/f'all-tests-{attempt}.log'
    with log.open('x',encoding='utf-8') as stream:
        tests=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(modules))
    assert tests.wasSuccessful(),[(t.id(),error[-1200:]) for t,error in [*tests.errors,*tests.failures]]
    assert len(tests.skipped)==70
    before=folder/'before-default-results.json'
    if not before.exists():before=fresh_before(folder)
    rows=json.loads(before.read_text(encoding='utf-8'))
    assert len(rows)==732
    for i,row in enumerate(rows,1):
        assert calculate_damage(row['scenario'])==row['result'],row['scenario']
        if i%100==0:print(json.dumps({'exact_default_replays':i}),flush=True)
    names=set(previous['source_sha256'])|{str(p.relative_to(ROOT)) for base in ('scripts','tests')
        for p in (ROOT/base).glob('*048.py')}|{'rouge/animation_reference.py','rouge/data/original-animation-references.json'}
    receipt={'version':'0.48.0','passed':True,'tests_run':tests.testsRun,
        'current_tests_passed':tests.testsRun-len(tests.skipped),'new_unit_tests':tests.testsRun-589,
        'historical_combat_tests_skipped':len(tests.skipped),'failures':len(tests.failures),'errors':len(tests.errors),
        'test_modules':modules,'test_log':str(log.relative_to(ROOT)),'test_log_sha256':digest(str(log.relative_to(ROOT))),
        'fresh_previous_public_baseline':str(before.relative_to(ROOT)),
        'fresh_previous_public_baseline_sha256':digest(str(before.relative_to(ROOT))),
        'exact_default_public_replays':len(rows),'default_public_outputs_unchanged':True,
        'numeric_public_replay_rerun':True,'recognition_core_unchanged':True,
        'changed_existing_source_files':sorted(changed),'source_sha256':{n:digest(n) for n in sorted(names)},
        'live_measurements':0,'new_recognition_speed_claim':False,'game_actions':0,'chat_requests':0,
        'seconds':time.perf_counter()-started}
    (ROOT/'MECHANISMS_0.48_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in receipt.items() if k not in ('source_sha256','test_modules')},ensure_ascii=False))


if __name__=='__main__':main()
