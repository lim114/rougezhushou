"""Seal this batch's current sources, explicit scopes and immutable evidence."""
import hashlib,json,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OCR=Path('.cache/research/ocr-pipeline-057/epoch-1791147282575917000')
VISUAL=Path('.cache/research/visual-recognition-057/epoch-1791147810880983400')
COST=Path('.cache/research/empty-bed-cost-057')


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))


def verify_hashes(mapping,base=ROOT):
    for name,value in mapping.items():assert sha(base/name)==value,('Source/evidence drift',name)


def main():
    paths=[Path(f'{n}_0.57_VERIFICATION.json') for n in
        ('CORE','NUMERIC_REPLAY','NATIVE_UI','RECOGNITION_UI','PACKAGE')]
    paths+=[Path('APP_0.57_LAUNCH_VERIFICATION.json'),OCR/'receipt-1791147474484788800.json',
        VISUAL/'receipt.json',OCR/'owned-freeze.json',VISUAL/'owned-freeze.json',COST/'freeze.json',
        COST/'verification.json',Path('.cache/batch-057-source-freeze.json')]
    data=[read(ROOT/p) for p in paths]
    core,numeric,native,ui,package,app,ocr,visual,ocr_freeze,visual_freeze,cost_freeze,cost,freeze=data
    assert all(r.get('passed') is True for r in (core,numeric,native,ui,package,ocr,visual))
    assert not core['source_drift_during_tests'] and not core['failures'] and not core['errors']
    assert numeric['exact_structured_unchanged']==732 and not numeric['unexpected_changes']
    assert ocr['strict_observation_pairs']==9 and visual['cases']==42
    assert visual['strict_semantic_differences']==0 and visual_freeze['tests_passed']==18
    assert cost['verified'] and cost_freeze['related_tests']['failures']==0
    assert app['same_run_preserved'] and app['settings_and_bindings_unchanged']
    assert app['window_visible_and_restored'] and app['only_one_project_window']
    for record in (core,numeric,native,ui,package):verify_hashes(record['source_sha256'])
    for field in ('owned_source_hashes','owned_verification_hashes'):verify_hashes(ocr[field])
    assert sha(ROOT/OCR/'receipt-1791147474484788800.json')==ocr_freeze['receipt_sha256']
    verify_hashes(visual_freeze['owned_source_hashes']);verify_hashes(cost_freeze['files'])
    verify_hashes(cost_freeze['evidence'],ROOT/COST)
    assert sha(ROOT/VISUAL/'receipt.json')==visual_freeze['receipt_sha256']
    assert sha(ROOT/VISUAL/'REPORT.md')==visual_freeze['report_sha256']
    verify_hashes(freeze['source_hashes'])
    assert freeze['source_hashes']==core['source_sha256']
    for path,value in ((core['test_log'],core['test_log_sha256']),
        (package['wheel'],package['wheel_sha256']),
        (numeric['worker_receipt'],numeric['worker_receipt_sha256']),
        (numeric['current_output'],numeric['current_output_sha256']),
        (numeric['baseline_output'],numeric['baseline_sha256'])):
        assert sha(ROOT/path)==value,('Downstream evidence drift',path)
        paths.append(Path(path))
    before=read(ROOT/'.cache/batch-057-before/manifest.json')['source_hashes']
    changed=sorted(name for name,value in before.items() if sha(ROOT/name)!=value)
    production_changes=[n for n in changed if n.startswith('rouge/')]
    assert production_changes==sorted(['rouge/app.py','rouge/deployment.py','rouge/dynamic_ocr.py',
        'rouge/page_features.py','rouge/recognition.py','rouge/visual_recognition.py']),production_changes
    public=set(freeze['source_hashes'])
    public.update(('README.md','PROJECT_PROGRESS.md','PROJECT_COMPLETED.md','WORK_IN_PROGRESS.md',
        'BATCH_0.57.md','pyproject.toml','run.cmd','tests/test_relic_extension.py'))
    public.update(p.relative_to(ROOT).as_posix() for p in (ROOT/'scripts').glob('*057*.py'))
    public.update('/'.join(selector.split('.')[:2])+'.py' for selector in core['test_modules'])
    # OCR's report is its pinned JSON receipt, not a separate Markdown file.
    paths+=[VISUAL/'REPORT.md',COST/'REPORT.md']
    record={'version':'0.57.0','passed':True,'verified_at':time.time(),
        'tests_run':core['tests_run'],'current_tests_passed':core['current_tests_passed'],
        'historical_tests_skipped':core['historical_tests_skipped'],
        'failures':0,'errors':0,'numeric_defaults_exact':732,'ocr_observation_pairs':9,
        'visual_semantic_cases':42,'visual_repeated_animation_pairs':33,
        'changed_existing_sources':changed,'changed_production_files':production_changes,
        'receipt_sha256':{p.as_posix():sha(ROOT/p) for p in paths},
        'source_sha256':{n:sha(ROOT/n) for n in sorted(public)},
        'test_source_monitoring':'Production monitored before/after CORE; test files sealed at finalization. No concurrent test edits were performed.',
        'all_priority_1_completed':False,'all_priority_1_3_completed':False,
        'game_actions':0,'chat_requests':0,'scope':'Both recognition paths, source-backed empty-bed cost, installed assets and own test window.',
        'limits':['Visual cache benefits require exact pixels; actual animation had no cache hits or general speed gain.',
            'OCR exact-control gain is demonstrated in a controlled one-pixel derivative, not a new independent positive animation.',
            'Independent home-menu captures are negative pages; positive recognition coverage remains limited.',
            'Empty-bed costs are an offline native-baseline reference; actual deployment and current hotfix equivalence are not verified.',
            'Other remaining tasks stay in PROJECT_PROGRESS.md.']}
    with (ROOT/'FINAL_0.57_VERIFICATION.json').open('x',encoding='utf-8') as stream:
        json.dump(record,stream,ensure_ascii=False,indent=2)
    print(json.dumps({k:record[k] for k in ('passed','tests_run','current_tests_passed','historical_tests_skipped')},ensure_ascii=False))


if __name__=='__main__':main()
