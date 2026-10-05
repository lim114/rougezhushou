"""Seal current public code and receipts; never inspect private runtime data."""
import argparse,hashlib,json,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):return json.loads(path.read_text(encoding='utf-8'))


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--routing',type=Path,required=True)
    args=parser.parse_args()
    routing=args.routing.resolve()
    assert routing.is_relative_to(ROOT/'.cache/research/page-routing-056')
    freeze=ROOT/'.cache/batch-056-source-freeze-epoch4.json'
    source=read(freeze)['source_hashes']
    assert all(sha(ROOT/name)==value for name,value in source.items()),'Source changed after freeze'
    paths=[ROOT/'CORE_0.56_VERIFICATION.json',ROOT/'NUMERIC_REPLAY_0.56_VERIFICATION.json',
        ROOT/'NATIVE_UI_0.56_VERIFICATION.json',ROOT/'SKILL_UI_0.56_VERIFICATION.json',
        ROOT/'APP_0.56_LAUNCH_VERIFICATION.json',routing,
        ROOT/'.cache/page-features-056/core-region-experiment-1791142710952945400/final-receipt.json',
        ROOT/'.cache/page-features-056/review-static-closure-1791143559019374400.json',
        ROOT/'.cache/research/relic-panel-056/final-static-1791141429607832400.json']
    receipts=[read(path) for path in paths]
    core,numeric,native,skill,app,route,feature,closure,mechanism=receipts
    assert all(d.get('passed') is True for d in (core,numeric,native,skill,route,feature,closure)), 'A required receipt did not pass'
    assert mechanism['read_only_static_final'] and mechanism['original_16_file_freeze_unchanged']
    assert mechanism['hp_atk_def_source_layers_verified']
    assert sha(ROOT/'.cache/research/relic-panel-056/REPORT.md')==mechanism['report_sha256']
    mechanism_freeze=ROOT/'.cache/research/relic-panel-056/freeze.json'
    evidence=read(mechanism_freeze)
    assert all(sha(ROOT/name)==value for name,value in evidence['files'].items())
    native_evidence=ROOT/'.cache/research/relic-panel-056/native-evidence.json'
    assert sha(native_evidence)==evidence['native_evidence_sha256']
    paths += [mechanism_freeze,native_evidence]
    assert route['all_cases']==19 and route['strict_equal_cases']==19 and not route['missing_cases']
    assert route['source_sha256']==source,'Image receipt is for another source epoch'
    assert numeric['full_formal_source_sha256']==source and numeric['full_formal_source_count']==len(source)
    assert not numeric['unexpected_changes'] and not numeric['unused_exact_allowances']
    assert not core['source_drift_during_tests']
    assert app['same_run_preserved'] and app['settings_and_bindings_unchanged']
    assert app['window_visible_and_restored'] and app['only_one_project_window']
    for receipt in (core,native,skill):
        for name,value in receipt.get('source_sha256',{}).items():
            assert sha(ROOT/name)==value,('Receipt source drift',name)
    public=[ROOT/name for name in source]
    public += [ROOT/name for name in ('README.md','PROJECT_PROGRESS.md','PROJECT_COMPLETED.md',
        'WORK_IN_PROGRESS.md','BATCH_0.56.md','pyproject.toml','run.cmd')]
    public += list((ROOT/'scripts').glob('*056*.py'))
    # The maintained suite contains both modules and individual test selectors.
    public += [ROOT/('/'.join(module.split('.')[:2])+'.py') for module in core['test_modules']]
    record={'version':'0.56.0','passed':True,'verified_at':time.time(),
        'tests_run':core['tests_run'],'current_tests_passed':core['current_tests_passed'],
        'historical_tests_skipped':core['historical_tests_skipped'],'failures':0,'errors':0,
        'receipt_sha256':{p.relative_to(ROOT).as_posix():sha(p) for p in paths+[freeze]},
        'source_sha256':{p.relative_to(ROOT).as_posix():sha(p) for p in sorted(set(public))},
        'image_replay_cases':19,'numeric_replay_cases':732,'all_priority_1_completed':False,
        'all_priority_1_3_completed':False,'game_actions':0,'chat_requests':0,
        'scope':'Evidence-backed rune fixes, maintained regression, limited visual page controls, fixed public image replay and actual own test window.',
        'limits':['No new current-game predicted/actual panel pair or hotfix equivalence proof.',
                  'Attribute differential cases retain existing skill models; not complete native skill oracles.',
                  'Faster visual detectors were rejected; domain area savings are not OCR speed claims.',
                  'Routing resources cover cultivation/module pages; other pages use full discovery.',
                  'Public image development corpus and derived transforms are not universal accuracy or live P95.']}
    output=ROOT/'FINAL_0.56_VERIFICATION.json'
    with output.open('x',encoding='utf-8') as stream:json.dump(record,stream,ensure_ascii=False,indent=2)
    print(json.dumps({k:record[k] for k in ('passed','tests_run','current_tests_passed','historical_tests_skipped','image_replay_cases','numeric_replay_cases')},ensure_ascii=False))


if __name__=='__main__':main()
