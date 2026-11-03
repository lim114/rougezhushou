"""Seal source reuse, paired-output evidence and an external patch for root review."""
import difflib
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent
PREVIOUS = ROOT.parent / 'p2-after-055-audit/derived-report'
BASE = PREVIOUS / 'frozen'
DRAFT = ROOT / 'draft'
REPO = Path('/workspace/rougezhushou')
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def write(name, value):
    (ROOT / name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

original=json.loads((PREVIOUS / 'source-receipt.json').read_text())
source={**original,'section':59,'change_scope':'known_damage_subtotals report notes only',
    'prior_readonly_audit_head':original['public_code_head'],
    'reused_evidence_directory':str(PREVIOUS),
    'fresh_table_hashes':{name:{'sha256':sha(Path(info['reused_local_path'])),
                               'matches_prior':sha(Path(info['reused_local_path']))==info['sha256']}
                          for name,info in original['tables'].items()},
    'source_facts_used_for_change':[
        'Public neural_s1_reference already marks unresolved first binding attachment and refresh, independently of relic choice.',
        'Public neural_incoming_reference already marks unavailable normal-attack timestamps; count alone cannot schedule neural events.',
        'Public neural_relic_reference supports naming River as a missing subtotal source; a held-relic record alone does not prove that attribution.',
        'S3 continuous-damage and bait notes retain their existing source boundary when other pending sources coexist.',
        'Shield S2 declared break-count public reference is an additional no-River reachability of the same fallback; generic warning attributes no invented source.'
    ],'new_native_mechanism_inferred':False,
    'reused_shield_receipt':{'path':'research/p2-shield-break-reference/NOTE.md',
        'sha256':sha(REPO / 'research/p2-shield-break-reference/NOTE.md')}}
assert all(v['matches_prior'] for v in source['fresh_table_hashes'].values())
write('source-receipt.json',source)
manifest=json.loads((PREVIOUS/'freeze-manifest.json').read_text())
drift=[rel for rel,digest in manifest['files'].items()
       if not (BASE/rel).is_file() or sha(BASE/rel)!=digest]
assert not drift,drift
write('baseline-integrity.json',{'head':manifest['head'],'verified_files':len(manifest['files']),
    'baseline_intact':True,'drift':drift,'manifest_sha256':sha(PREVIOUS/'freeze-manifest.json')})
audit=ROOT/'prior-readonly-audit'
audit.mkdir(exist_ok=True)
for name in ('NOTE.md','source-receipt.json','public-results.json','validation.json',
             'reproduce.py','collect_source.py','freeze-manifest.json'):
    shutil.copyfile(PREVIOUS/name,audit/name)
diff=''
for relative in ('rouge/reporting.py','tests/test_damage_subtotal_sources.py'):
    baseline=BASE/relative
    draft=DRAFT/relative
    diff+=''.join(difflib.unified_diff(
        baseline.read_text(encoding='utf-8').splitlines(keepends=True) if baseline.exists() else [],
        draft.read_text(encoding='utf-8').splitlines(keepends=True),
        fromfile='a/'+relative if baseline.exists() else '/dev/null',tofile='b/'+relative))
(ROOT/'section59.patch').write_text(diff,encoding='utf-8',newline='')
new=json.loads((ROOT/'draft-new-tests.json').read_text())
related_log=(ROOT/'related-tests.log').read_text()
assert new['passed'] and 'Ran 102 tests' in related_log and related_log.rstrip().endswith('OK')
comparison=json.loads((ROOT/'matrix-comparison.json').read_text())
write('test-receipt.json',{'passed':True,'new_tests':new,'related_tests':{
    'run':102,'failures':0,'errors':0,'skipped':0,'console_sha256':sha(ROOT/'related-tests.log')},
    'public_pairs':comparison['public_pairs'],'public_calls':comparison['public_calls'],
    'changed_notes_only':comparison['changed_notes_only'],
    'unchanged_whole_outputs':comparison['unchanged_whole_outputs'],
    'numeric_scope_complete_phase_sp_and_actual_fields_identical':True,
    'new_source_mechanisms':False,'native_windows':False,
    'draft_preparation_corrections':[
        {'kind':'test_fixture_expectation','tests_run':6,'failed_method':
            'test_real_river_alone_keeps_its_existing_subtotal_warning_and_numbers',
         'reason':'The preexisting Mantra unbound reference selects the generic primary note, not River-only fallback; source inspected and test corrected without production change.',
         'console_saved':False,'source_change_for_correction':False},
        {'kind':'matrix_schema','public_calls':0,'error':'KeyError: number',
         'reason':'Normalized skill records have id/unlock_elite/levels, with number established by list position; runner corrected before making any matrix claims.',
         'original_console':'baseline-matrix-initial-schema-error.log'},
        {'kind':'source_attribution_review','reviewer':'root',
         'reason':'Held River without a real neural_relic_reference is not the missing source of mechanical shield-break subtotal; narrowed River note gate to actual reference.',
         'prior_draft':'prior-draft-v1','counterexample':'prior-draft-v1/root-counterexample.json',
         'matrix_cases_preserved':True,'production_numeric_changes':False}]})
write('handoff-receipt.json',{'section':59,'baseline_head':manifest['head'],
    'baseline_reporting_sha256':sha(BASE/'rouge/reporting.py'),
    'draft_reporting_sha256':sha(DRAFT/'rouge/reporting.py'),
    'patch_sha256':sha(ROOT/'section59.patch'),'patch_bytes':(ROOT/'section59.patch').stat().st_size,
    'patch_files':['rouge/reporting.py','tests/test_damage_subtotal_sources.py'],
    'selected_runner_registration_required':'tests.test_damage_subtotal_sources',
    'baseline_intact':True,'related_tests_passed':True,'public_output_pairs_passed':True,
    'independent_review':'pending','tracked_repository_edited':False,
    'root_integration_and_actual_ui_validation_required':True})
print(json.dumps({'patch_sha256':sha(ROOT/'section59.patch'),'public_pairs':comparison['public_pairs'],
    'changed_notes_only':comparison['changed_notes_only'],'verified_baseline_files':len(manifest['files'])},ensure_ascii=False))
