"""Source-only full095 migration planning. Never import project or Qt code."""
import ast
import difflib
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path('/workspace/rougezhushou')
OUT = Path(__file__).resolve().parent
BASE91 = '59961ec3d633ac91b01014fb06b357d45e5979f7'
OLD90 = '2cbc45f03f99ed4f04b9c7e2612b58542f909168'
REPO_INPUTS = (
    'verification/full-090/wine-ui-runner.py',
    'verification/full-090/validation-scope.json',
    'verification/full-090/root-preparation/root-ui090-preflight.py',
    'scripts/verify_damage_ui.py', 'rouge/app.py', 'rouge/reporting.py',
    'rouge/operator_engine.py', 'rouge/estimate.py', 'rouge/damage.py',
    'rouge/data/catalog.json',
    'research/p2-section091-attack-condition-regeneration/ui-author/static-runner-contract-migration091.json',
    'research/p2-section091-attack-condition-regeneration/future092-source-and-unexecuted-candidate/candidate-flow.patch',
    'research/p2-section091-attack-condition-regeneration/future092-source-and-unexecuted-candidate/verification-contract.json',
    'research/p2-section091-attack-condition-regeneration/future092-source-and-unexecuted-candidate/public-candidate-manifest.json',
)
EXTERNAL_INPUTS = (
    '/workspace/.continuation/ui-090-final-gate-revision/wine-ui-smoke-090-final-gate-revision.py',
    '/workspace/.continuation/ui-090-final-gate-revision/runner-scope-and-source-freeze090-revision.json',
    '/workspace/.continuation/ui-090-final/wine-ui-smoke-090-final.py',
    '/workspace/.continuation/ui-090-final/runner-scope-and-source-freeze090.json',
)

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)

def sha(raw):return hashlib.sha256(raw).hexdigest()

def write(name, value):
    p = OUT / name
    if p.exists():raise RuntimeError('Existing source plan artifact: ' + name)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')

observed_before = git('rev-parse', 'HEAD').decode().strip()
data = {rel: git('show', BASE91 + ':' + rel) for rel in REPO_INPUTS}
inputs = [{'repository_path': rel, 'read_git_commit': BASE91, 'bytes': len(raw),
           'sha256': sha(raw), 'git_blob': git('rev-parse', BASE91 + ':' + rel).decode().strip(),
           'copied_source_archive': False} for rel, raw in data.items()]
external = []
for rel in EXTERNAL_INPUTS:
    raw = Path(rel).read_bytes()
    external.append({'source_path': rel, 'bytes': len(raw), 'sha256': sha(raw), 'copied_archive': False})
runner_rel = REPO_INPUTS[0]
raw = data[runner_rel]
old_committed = git('show', OLD90 + ':' + runner_rel)
if old_committed != raw:raise RuntimeError('Committed historical full090 runner bytes changed')
if Path(EXTERNAL_INPUTS[0]).read_bytes() != raw:raise RuntimeError('Designated external full090 final-gate runner differs')
source = raw.decode('utf-8')
old = "assert window.continuous_attacks.isVisible() is (sp090=='INCREASE_WHEN_ATTACK')"
new = "assert window.continuous_attacks.isVisible() is (sp090 in ('INCREASE_WHEN_ATTACK','INCREASE_WITH_TIME'))"
if source.count(old) != 1:raise RuntimeError('Legacy visibility predicate is not uniquely selected')
migrated = source.replace(old, new)
if migrated.replace(new, old).encode('utf-8') != raw:raise RuntimeError('Visibility-only migration is not exactly invertible')
tree = ast.parse(source)
catalog = json.loads(data['rouge/data/catalog.json'])
row_assignment = next(n for n in ast.walk(tree) if isinstance(n, ast.Assign) and
                      any(isinstance(z, ast.Name) and z.id == 'rows090' for z in n.targets))
rows = ast.literal_eval(row_assignment.value)
visibility_rows = []
for row in rows:
    if row['section'] != 88:continue
    scenario = row['input']
    sp = catalog['operators'][scenario['operator']]['skills'][scenario['skill']-1]['levels'][scenario['skill_rank']-1]['sp_type']
    visibility_rows.append({'historical_pair_id': row['pair_id'], 'operator': scenario['operator'],
                            'skill': scenario['skill'], 'rank': scenario['skill_rank'],
                            'checked': row['widget_checked'], 'sp_type': sp,
                            'legacy_expected_visible': sp == 'INCREASE_WHEN_ATTACK',
                            'section91_expected_visible': sp in ('INCREASE_WHEN_ATTACK', 'INCREASE_WITH_TIME')})
saved89 = next(n for n in ast.walk(tree) if isinstance(n, ast.Assign) and
               any(isinstance(z, ast.Name) and z.id == 'saved89_states090' for z in n.targets))
saved89_rows = ast.literal_eval(saved89.value)
contract89 = next(n for n in ast.walk(tree) if isinstance(n, ast.Assign) and
                  any(isinstance(z, ast.Name) and z.id == 'expected89_contract090' for z in n.targets))
contract89_rows = ast.literal_eval(contract89.value.generators[0].iter)
source_guard = next(n for n in ast.walk(tree) if isinstance(n, ast.Assign) and
                   any(isinstance(z, ast.Name) and z.id == '_SOURCE090' for z in n.targets))
write('original-runner-and-source-index.json', {
    'status': 'SOURCE_READ_ONLY_NOT_FULL095_VALIDATION', 'source_baseline91': BASE91,
    'observed_live_root_head_before': observed_before,
    'observed_live_root_head_after': git('rev-parse', 'HEAD').decode().strip(),
    'read_only_repository_inputs': inputs, 'read_only_external_inputs': external,
    'original_final090_committed_external_runner_exact': True,
    'original_guard_entry_count_historical_only': len(source_guard.value.keys),
    'current_full095_guard_or_final_source_count': 'PENDING_ACTUAL95_HEAD',
    'root_tracked_mutations': 0, 'copied_full090_archives': 0,
    'calls': {'project_API': 0, 'project_helper': 0, 'project_formatter': 0, 'tests': 0,
              'Qt': 0, 'Wine': 0, 'network': 0},
})
write('visibility-single-predicate-inverse-proof.json', {
    'scope': 'Unexecuted source-only preview of one necessary full095 assertion migration; not a full095 runner',
    'old_runner_path': runner_rel, 'old_runner_sha256': sha(raw), 'old_runner_bytes': len(raw),
    'old_source_assertion_line': 3011, 'selected_rank_source_line': 3010,
    'before': old, 'after': new, 'single_occurrence': True,
    'preview_sha256': sha(migrated.encode('utf-8')), 'preview_not_saved_or_executed': True,
    'exact_full_runner_byte_inverse_after_only_predicate_reversal': True,
    'selected_requested_rank_already_present_and_not_changed': True,
    'current_verify_damage_ui_path': 'scripts/verify_damage_ui.py',
    'current_verify_damage_ui_sha256': sha(data['scripts/verify_damage_ui.py']),
    'current_verify_damage_ui_line39_uses_selected_rank_and_Attack_Natural': True,
    'old_full090_section88_rows': visibility_rows,
    'changed_visibility_rows': sum(r['legacy_expected_visible'] != r['section91_expected_visible'] for r in visibility_rows),
    'historical_ids_stay_as_provenance_not_current_hidden_UI_claims': True,
    'all4283_or4217_unchanged_claim_supported': False,
    'diff': ''.join(difflib.unified_diff(source.splitlines(True), migrated.splitlines(True), 'original-full090.py', 'visibility-only-full095-preview.py')),
    'future_final_inverse_required': 'Final95 guard/output/provenance/ledger and new groups must each have an explicit delta ledger; after reversing registered final deltas the retained original body must equal its exact original SHA. This preview does not prove those future changes.',
})
lines = source.splitlines()
def excerpt(first, last):return '\n'.join(lines[first-1:last])
write('legacy-calculation-and-saved089-dependencies.json', {
    'legacy_52_request_rows': len(rows), 'section88_visibility_source_line': 3011,
    'saved089_run_states': {'ast_source_line': saved89.lineno, 'records': len(saved89_rows),
                           'keys': list(saved89_rows[0]),
                           'only_roster_owners': sorted({k for r in saved89_rows for k in r['state']['operators']}),
                           'contains_damage_result_report_or_formatter_text': False},
    'saved089_expected_consumer_contract': {'ast_source_line': contract89.lineno,
                                         'records': len(contract89_rows), 'keys': list(contract89_rows[0]),
                                         'contains_damage_result_report_or_formatter_text': False},
    'saved089_dependency_path': {'source_lines': '3083..3127',
                                'fact': 'Assign saved temporary RunState state; refresh roster/summary; switch training; select mechanist and update_operator using current app. Current calculations/rendering may run automatically, while native current_state/training/roster/labels/runstate and no-constructor/apply-replay are asserted. It is not old damage result replay.'},
    'old_result_formatter_behavior': {'app_render_damage_lines': '1209..1213',
                                    'estimate_format_lines': '247..250',
                                    'fact': 'Both render existing result.report through current format_report. They do not call build_report or migrate old notes/metrics. Existing old result does not gain91/92 fields merely by formatting.'},
    'legacy_original_numeric_projection': {'lines': '1014..1020 +3015',
                                          'excludes': ['result.report', 'estimate.notes'],
                                          'includes': ['root numeric totals/components/timing/references', 'estimate.training', 'estimate.base_stats', 'estimate.skill'],
                                          'future_rule': 'Keep exact projection assertions unless93/94/95 actual evidence proves a narrower approved numerical change;91notes and92report rows alone do not justify relaxing projection.'},
    'legacy_same_current_call_guards': {'lines': '3021..3028',
                                     'fact': 'Estimate/default current formats agree; actual widget uses that same current result in default/technical; formatter preserves full native current result and scenario. No historical text golden equality is asserted here.'},
    'legacy_same_head_inactive_pairs': {'lines': [1986,2103,2336,2385,3033],
                                      'fact': 'Whole JSON equality compares two freshly computed current-head outcomes for inactive flags, not old saved full JSON. Preserve rather than globally strip qualifications.'},
    'existing_Deepcolor_counts': {'lines': '2018..2054',
                               'fact': 'Old section63 retains typed declared counts/caps and no-rose fixed S1 rates. It does not assert old4200/1400 note text. Add qualified91text scope in new95group; do not label its text unchanged.'},
    'excerpts': {'projection': excerpt(1014,1020), 'same_call_text_native': excerpt(3015,3033),
                 'saved089_actions': excerpt(3083,3092), 'saved089_native_guards': excerpt(3101,3127),
                 'old_deepcolor_fixed_rates': excerpt(2030,2038)},
})
print(json.dumps({'status': 'SOURCE_PLAN_CAPTURE_PASS_NOT_EXECUTION',
                  'read_git_baseline91': BASE91, 'old_full090_copy_count': 0,
                  'migrated_section88_visibility_rows': 6, 'project_Qt_Wine_tests_network': 0}))
