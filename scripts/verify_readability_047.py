"""Current Chinese presentation tests and untouched numerical source guards."""
import ast,hashlib,json,sys,time,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))


def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8'))
def digest(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()


def main():
    started=time.perf_counter();previous=read('FINAL_0.46_VERIFICATION.json')
    changed={n for n,sha in previous['source_sha256'].items() if digest(n)!=sha}
    allowed={'pyproject.toml','rouge/app.py','rouge/battle_view.py','rouge/battle_preview.py',
        'rouge/enemy_skills.py','rouge/spawn_reference.py','rouge/view_catalog.py','rouge/branch_choice.py',
        'rouge/reporting.py','rouge/map_reporting.py','rouge/operator_summary.py',
        'tests/test_battle_preview_039.py','tests/test_spawn_reference_040.py','tests/test_enemy_skills_042.py',
        'tests/test_neural_relic_034.py'}
    assert changed<=allowed,changed-allowed
    public_backup=read('.cache/batch-047-before/manifest.json')
    assert all(digest('.cache/batch-047-before/'+n)==sha for n,sha in public_backup.items())
    guarded={
        'rouge/battle_preview.py':('battle_data','display_cell','route_reference','hidden_group_reference','spawn_rows','enemy_preview'),
        'rouge/enemy_skills.py':('skill_data','enemy_skill_reference'),
        'rouge/spawn_reference.py':('finite_nonnegative','local_sequence','ordinal_offset','movement_reference')}
    guarded_count=0
    for name,functions in guarded.items():
        def nodes(path):return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(path.read_text(encoding='utf-8')).body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
        before=nodes(ROOT/'.cache/batch-047-before'/name);after=nodes(ROOT/name)
        for function in functions:assert before[function]==after[function],(name,function);guarded_count+=1
    before=nodes(ROOT/'.cache/batch-047-before/rouge/reporting.py');after=nodes(ROOT/'rouge/reporting.py')
    for name in before:
        if name!='format_report':assert before[name]==after[name],name;guarded_count+=1
    modules=[*read('BRANCH_0.46_VERIFICATION.json')['test_modules'],
        'tests.test_readability_047','tests.test_readable_battle_047','tests.test_readable_map_047']
    folder=ROOT/'.cache/readable-047';folder.mkdir(exist_ok=True)
    attempt=1
    while (folder/f'all-tests-{attempt}.log').exists():attempt+=1
    log=str((folder/f'all-tests-{attempt}.log').relative_to(ROOT))
    with (ROOT/log).open('x',encoding='utf-8') as stream:
        result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(modules))
    assert result.wasSuccessful(),[(t.id(),err[-1500:]) for t,err in [*result.failures,*result.errors]]
    skipped=len(result.skipped);assert skipped==70,skipped
    extra={str(p.relative_to(ROOT)) for p in (ROOT/'scripts').glob('*047.py')}
    extra|={str(p.relative_to(ROOT)) for p in (ROOT/'tests').glob('*047.py')}
    extra|={'rouge/map_reporting.py','rouge/data/profession-icons.json'}
    names=set(previous['source_sha256'])|extra
    new_count=result.testsRun-543
    receipt={'version':'0.47.0','passed':True,'verified_at':time.time(),
        'tests_run':result.testsRun,'current_tests_passed':result.testsRun-skipped,'new_unit_tests':new_count,
        'historical_combat_tests_skipped':skipped,'failures':len(result.failures),'errors':len(result.errors),
        'test_modules':modules,'test_log':log,'test_log_sha256':digest(log),
        'changed_existing_source_files':sorted(changed),'source_sha256':{n:digest(n) for n in sorted(names)},
        'guarded_numeric_functions':guarded_count,'numeric_and_recognition_core_unchanged':True,
        'map_calibrations_unchanged':True,'numeric_public_replay_rerun':False,'inherited_numeric_cases':732,
        'synthetic_gui_tests_only':True,'new_recognition_speed_claim':False,'game_actions':0,'chat_requests':0,
        'seconds':time.perf_counter()-started}
    (ROOT/'READABILITY_0.47_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in receipt.items() if k not in ('source_sha256','test_modules')},ensure_ascii=False))


if __name__=='__main__':main()
