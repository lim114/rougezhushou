"""Seal current hybrid recognition, regressions, package and visible own app."""
import hashlib,json,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
HYBRID=Path('.cache/research/hybrid-058/epoch-current')
ENGINE=Path('.cache/research/page-ocr-058/freeze-1791173910294123300.json')
FEATURE=Path('.cache/page-features-058/freeze-1791173413785587000.json')
HYBRID_FREEZE=Path('.cache/research/hybrid-058/freeze-1791175246045218300.json')

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def verify(mapping):
    for name,value in mapping.items():assert sha(ROOT/name)==value,('Source/evidence drift',name)

def main():
    paths=[Path(f'{name}_0.58_VERIFICATION.json') for name in
        ('CORE','NUMERIC_REPLAY','NATIVE_UI','RECOGNITION_UI','PACKAGE')]
    paths+=[Path('APP_0.58_LAUNCH_VERIFICATION.json'),Path('HYBRID_0.58_VERIFICATION.json'),
        ENGINE,FEATURE,Path('.cache/batch-058-source-freeze.json'),HYBRID/'inventory.json',
        HYBRID/'baseline-package-seal.json',Path('.cache/batch-058-before/manifest.json')]
    core,numeric,native,ui,package,app,hybrid,engine,feature,freeze,inventory,baseline,before=[read(ROOT/p) for p in paths]
    roster_path=Path('ROSTER_0.58_VERIFICATION.json');roster=read(ROOT/roster_path);paths.append(roster_path)
    hybrid_freeze=read(ROOT/HYBRID_FREEZE);paths.append(HYBRID_FREEZE)
    assert hybrid_freeze['passed'] and hybrid_freeze['real_cases']==23 and hybrid_freeze['strict_differences']==0
    verify(hybrid_freeze['public_source_sha256']);verify(hybrid_freeze['owned_files_and_receipts_sha256'])
    paths.extend(Path(name) for name in hybrid_freeze['owned_files_and_receipts_sha256'])
    assert all(r.get('passed') is True for r in (core,numeric,native,ui,package,hybrid,engine,feature))
    assert roster['passed'] and roster['route_verified'] and roster['source_stable']
    assert not roster['strict_semantic_differences']
    assert not (Path.home()/'.codex/automations/1-3/automation.toml').exists()
    assert not core['failures'] and not core['errors'] and not core['source_drift_during_tests']
    assert core['maintained_test_files_sealed'] and core['runner_sealed']
    assert numeric['exact_structured_unchanged']==732 and not numeric['unexpected_changes']
    assert hybrid['strict_equal_cases']==22 and not hybrid['missing_cases'] and not hybrid['failed_cases']
    assert app['same_run_preserved'] and app['history_preserved'] and app['settings_and_bindings_unchanged']
    assert app['window_visible_and_restored'] and app['only_one_project_window'] and app['foreground_verified']
    for record in (core,numeric,native,ui,package,hybrid,roster):verify(record['source_sha256'])
    verify(numeric['full_formal_source_sha256'])
    assert not numeric['source_drift'] and numeric['allowances']==[]
    verify(engine['files']);verify(feature['source_sha256'])
    verify(feature['original_ten_binary_assets_sha256']);verify(freeze['source_hashes'])
    production_sources={name:value for name,value in core['source_sha256'].items() if name.startswith('rouge/')}
    assert freeze['source_hashes']==production_sources==hybrid['source_sha256']
    evidence={core['test_log']:core['test_log_sha256'],package['wheel']:package['wheel_sha256'],
        numeric['worker_receipt']:numeric['worker_receipt_sha256'],
        numeric['current_output']:numeric['current_output_sha256'],numeric['baseline_output']:numeric['baseline_sha256']}
    evidence.update(hybrid['replay_receipts']);verify(evidence)
    for item in [roster['immutable_receipt'],roster['case_receipt'],*roster['worker_receipts'].values(),
            hybrid['immutable_summary'],hybrid['actual_animation_pixel_evidence'],hybrid['baseline_package_seal']]:
        evidence[item['path']]=item['sha256']
    assert sha(ROOT/'scripts/verify_roster_overview_058.py')==roster['verifier_sha256']
    assert sha(ROOT/'scripts/verify_hybrid_058.py')==hybrid['verifier_sha256']==roster['hybrid_verifier_sha256']
    verify(evidence)
    paths.extend(Path(name) for name in evidence)
    for name,value in baseline['frozen_original_sources'].items():
        assert sha(ROOT/HYBRID/'baseline-source'/name)==value
    for name,value in baseline['supplemented_current_public_media'].items():
        assert sha(ROOT/HYBRID/'baseline-source'/name)==value
    assert sha(ROOT/'.cache/batch-058-before/manifest.json')==baseline['before_manifest_sha256']
    for sample in inventory['cases']:
        for frame in sample['frames']:assert sha(ROOT/frame['file'])==frame['sha256']
    changed=sorted(name for name,value in before['source_hashes'].items() if sha(ROOT/name)!=value)
    production=[name for name in changed if name.startswith('rouge/')]
    assert production==sorted(['rouge/app.py','rouge/recognition.py','rouge/data/page-features/manifest.json']),production
    # No numerical production source or catalogue changes are hidden by a new verifier.
    public=set(core['source_sha256'])
    public.update(('README.md','PROJECT_PROGRESS.md','PROJECT_COMPLETED.md','WORK_IN_PROGRESS.md',
        'BATCH_0.58.md','pyproject.toml','run.cmd'))
    public.update(p.relative_to(ROOT).as_posix() for p in (ROOT/'scripts').glob('*058*.py'))
    paths.extend([Path('.cache/research/page-ocr-058/REPORT.md'),Path('.cache/research/hybrid-058/ROOT_SOURCE_CHECK.md'),
        Path('.cache/research/hybrid-058/FINAL_REPORT-1791175298865671200.md')])
    receipt={'version':'0.58.0','passed':True,'verified_at':time.time(),
        'tests_run':core['tests_run'],'current_tests_passed':core['current_tests_passed'],
        'historical_tests_skipped':core['historical_tests_skipped'],'failures':0,'errors':0,
        'numeric_defaults_exact':732,'strict_hybrid_cases':23,'packaged_reference_assets':package['assets_checked'],
        'changed_existing_sources':changed,
        'changed_existing_production_files':production,
        'receipt_sha256':{p.as_posix():sha(ROOT/p) for p in paths},
        'source_sha256':{name:sha(ROOT/name) for name in sorted(public)},
        'test_source_monitoring':'Production, maintained test sources and CORE runner monitored at both ends.',
        'all_priority_1_completed':False,'all_priority_1_3_completed':False,'automation_1_3_deleted':True,
        'game_actions':0,'chat_requests':0,
        'scope':'Pure visual page controls choose current OCR priority; all current detector boxes remain; exact batch reuse only.',
        'limits':['Cold reads retain all REC; no general first-frame speed claim.',
            'Two real animation pairs are descriptive; resized cases are derived and training sources are marked.',
            'Complete text coverage refers to current detector boxes, not all small text on any layout.',
            'Remaining mechanisms and recognition coverage stay in PROJECT_PROGRESS.md.']}
    with (ROOT/'FINAL_0.58_VERIFICATION.json').open('x',encoding='utf-8') as handle:
        json.dump(receipt,handle,ensure_ascii=False,indent=2)
    print(json.dumps({key:receipt[key] for key in ('passed','tests_run','current_tests_passed','strict_hybrid_cases')},ensure_ascii=False))

if __name__=='__main__':main()
