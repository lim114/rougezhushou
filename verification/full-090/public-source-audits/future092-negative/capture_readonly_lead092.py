"""Read current committed source and reuse saved evidence; execute no project code."""
from pathlib import Path
import ast
import hashlib
import json
import subprocess

ROOT = Path('/workspace/rougezhushou')
OUT = Path(__file__).resolve().parent
BASE = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip()
sha = lambda raw: hashlib.sha256(raw).hexdigest()
FILES = [
    'PROJECT_PROGRESS.md', 'DAMAGE_SPEC.md', 'DEVELOPMENT_PLAN.md',
    'rouge/app.py', 'rouge/catalog.py', 'rouge/damage.py', 'rouge/estimate.py',
    'rouge/operator_recognition.py', 'rouge/run_state.py', 'rouge/operator_summary.py',
    'research/p2-training-input-types/NOTE.md',
    'research/p2-training-input-types/source-receipt.json',
    'research/p2-mei-airborne-module-reference/prior-readonly-audit/NOTE.md',
    'research/p2-mei-airborne-module-reference/prior-readonly-audit/lead-audit-receipt.json',
    'research/p2-mei-airborne-module-reference/prior-readonly-audit/common-skill-public-contract.json',
]


def write_json(name, value):
    with (OUT / name).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


captured = []
for rel in FILES:
    raw = subprocess.check_output(['git', 'show', BASE + ':' + rel], cwd=ROOT)
    path = OUT / 'committed-sources' / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        stream.write(raw)
    captured.append({'repository_path': rel, 'snapshot_path': path.relative_to(OUT).as_posix(),
                     'bytes': len(raw), 'sha256': sha(raw), 'actual_git_commit': BASE})

snap = OUT / 'committed-sources'
sources = {}
for rel, names in {
    'rouge/app.py': ['current_operator_state', 'training_conditions', 'skill_rank_value'],
    'rouge/catalog.py': ['operator_attributes'],
    'rouge/damage.py': ['_prepare_damage'],
}.items():
    text = (snap / rel).read_text()
    tree = ast.parse(text)
    sources[rel] = {node.name: ast.get_source_segment(text, node) for node in ast.walk(tree)
                    if isinstance(node, ast.FunctionDef) and node.name in names}
    assert set(sources[rel]) == set(names)
assert "(elite<2 and rank>7)" in sources['rouge/damage.py']['_prepare_damage']
assert "10 if self.training_conditions()['elite']==2 else 7" in sources['rouge/app.py']['skill_rank_value']
assert "'skill_ranks':ranks" in sources['rouge/app.py']['current_operator_state']

lead_path = snap / 'research/p2-mei-airborne-module-reference/prior-readonly-audit/lead-audit-receipt.json'
lead = json.loads(lead_path.read_bytes())
control_path = snap / 'research/p2-mei-airborne-module-reference/prior-readonly-audit/common-skill-public-contract.json'
controls = json.loads(control_path.read_bytes())
assert isinstance(controls, list) and len(controls) == 16
training_path = snap / 'research/p2-training-input-types/source-receipt.json'
training = json.loads(training_path.read_bytes())
catalog_raw = subprocess.check_output(['git', 'show', BASE + ':rouge/data/catalog.json'], cwd=ROOT)
catalog = json.loads(catalog_raw)
profile_rows = []
for op in ('mechanist', 'char_298_susuro', 'char_133_mm'):
    profile = catalog['operators'][op]
    profile_rows.append({'operator': op, 'name': profile['name'],
                         'phase_max_levels': [p['max_level'] for p in profile['phases']],
                         'skills': [{'id': s['id'], 'unlock_elite': s.get('unlock_elite'),
                                     'rank_count': len(s['levels'])} for s in profile['skills']]})
write_json('source-lead092.json', {
    'format_version': 1, 'status': 'NEGATIVE_FOR_NEW_IMPLEMENTATION_NATIVE_USE_RULE_UNKNOWN',
    'numbered_section': False, 'actual_source_baseline_commit': BASE,
    'captured_files': captured, 'current_source_excerpts_static_only': sources,
    'current_calculation_catalog': {'bytes': len(catalog_raw), 'sha256': sha(catalog_raw),
                                    'form_count': len(catalog['operators']),
                                    'skill_count': sum(len(p['skills']) for p in catalog['operators'].values()),
                                    'selected_profile_metadata': profile_rows},
    'prior_exact_lead_receipt': {'path': str(lead_path), 'bytes': lead_path.stat().st_size,
                                'sha256': sha(lead_path.read_bytes()),
                                'facts_reused': lead['common_skill_sources'],
                                'conclusion_reused': lead['common_skill_conclusion']},
    'prior_account_training_raw_verification_receipt_reused_not_fresh_raw_hash': {
        'path': str(training_path), 'sha256': sha(training_path.read_bytes()),
        'raw_pin_receipts': training['raw_current_verification'],
        'susuro_training_selector': training['susuro_training_selector'],
        'susuro_training_conditions': training['susuro_training_conditions'],
        'training_unlock_is_not_run_skill_use_cap': training['training_unlock_is_not_run_skill_use_cap'],
        'e0_skill_use_limit_verified': training['e0_skill_use_limit_verified']},
    'old_public_controls_reused_no_new_requests': {
        'path': str(control_path), 'sha256': sha(control_path.read_bytes()), 'rows': len(controls),
        'summary': [{'scenario': row['scenario'], 'success': 'result' in row['outcome'],
                     'error_type': row['outcome'].get('error_type'), 'error': row['outcome'].get('error')}
                    for row in controls],
        'scope': 'Historical admission observations only, not fresh verification or native validity'},
    'facts': [
        'Current damage guard rejects mastery rank>7 below E2, not common rank5..7 at E0.',
        'Current UI uses confirmed run ranks independently of account ranks and labels missing rank defaults as preview.',
        'Current common rank<7 recognition assigns the shared rank to all skills.',
        'Existing promotion merge invalidates old rank claims until current observations reconfirm them.',
        'Saved six-theme charUpgradeTable gives E1 common7/mastery0 and E2 common7/mastery3 caps.',
        'Saved character allSkillLvlup unlockCond describes account upgrading costs and conditions, not native restricted-form use.'
    ],
    'no_new_positive_source_contract_gap_established': True,
    'unknowns': ['Account-to-run trained common-skill inheritance under restricted elite form',
                 'Whether E0 can use previously trained common ranks5..7',
                 'Current client protocol for skill availability and corresponding in-run observations'],
    'restart_condition': 'A precise pinned recruit/use protocol, authoritative current rule or original independent run observation proves actual availability and inheritance; then evaluate a bounded reproduction.',
    'new_raw_source_hashes_or_downloads': 0,
    'application_API_project_helper_formatter_tests_Qt_Wine_calls': 0,
    'tracked_edits': 0, 'product_drafts': 0,
    'prior_raw_or_public_sweeps_not_repeated': True,
    'immutable90_source28_and_author62_not_modified': True})
write_json('preparation-diagnostics092.json', {
    'format_version': 1,
    'optional_guessed_path_errors': ['rouge/operator_profile.py', 'rouge/attributes.py',
                                    'rouge/operator_state.py', 'tests/test_operator_state.py', 'tests/test_run_state.py'],
    'resolution': 'Discovered actual source paths using rg --files and global definition searches; no execution or edits depended on absent guesses',
    'oversized_saved_controls_discovery_output': 'Initial generic topkeys print received a JSON list and produced truncated output; subsequently used explicit type and selected leaf summaries.',
    'failed_product_or_mechanism_attempts': 0,
    'application_API_helper_test_Qt_Wine_calls': 0,
    'source_lead_is_negative_not_a_completed_section': True})
print(json.dumps({'status': 'negative/unknown source lead only', 'baseline': BASE,
                  'committed_source_files': len(captured), 'reused_saved_controls': len(controls),
                  'new_API_helper_test_Qt_Wine_calls': 0, 'product_draft_or_tracked_edits': 0}))
