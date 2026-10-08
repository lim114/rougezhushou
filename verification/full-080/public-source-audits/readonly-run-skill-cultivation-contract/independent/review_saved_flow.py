import ast
import collections
import gzip
import hashlib
import json
import subprocess
from pathlib import Path

root = Path('/workspace/.continuation/p2-run-skill-cultivation-contract-audit')
own = root / 'independent'
commit = 'a52a4bf9217aee3c11617135b7fc9cc6c38fd0f2'
repo = Path('/workspace/rougezhushou')

def identity(raw):
    return {'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}

assert identity((own / 'independent-artifact-hashes.json').read_bytes())['sha256'] == '23f6c2af5eba6e4d1c6dc6d4f98dafc9d1f6badde596f73b9ea08cdb426b6505'
selected = json.loads((root / 'flow-source-selectors.json').read_text())
assert selected['baseline_head'] == commit
source_checks = []
for f in selected['files']:
    rel = f['source_path']
    raw = (root / 'frozen75' / rel).read_bytes()
    expected = subprocess.check_output(['git', 'show', commit + ':' + rel], cwd=repo)
    assert raw == expected
    assert identity(raw) == {k: f[k] for k in ('sha256', 'bytes')}
    lines = raw.decode().splitlines()
    for span in f['spans']:
        assert '\n'.join(lines[span['start_line'] - 1:span['end_line']]) == span['exact_text']
    source_checks.append({'source_path': rel, **identity(raw), 'matched_fixed_git_object_bytes': True,
                          'exact_spans_checked': len(f['spans'])})
flow = (root / 'flow_probe.py').read_text()
tree = ast.parse(flow)
app = ast.parse((root / 'frozen75/rouge/app.py').read_text())
cls = next(n for n in app.body if isinstance(n, ast.ClassDef) and n.name == 'MainWindow')
methods = {n.name: n for n in cls.body if isinstance(n, ast.FunctionDef)}
expected_methods = ['current_operator_state', 'training_conditions', 'skill_rank_value']
decl = next(n for n in tree.body if isinstance(n, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == 'names' for t in n.targets))
assert list(ast.literal_eval(decl.value)) == expected_methods
assert all(name in methods for name in expected_methods)
assert 'ast.Module(body=[methods[name] for name in names]' in flow
assert 'choices_node.value' in flow and 'scenario_node.value' in flow
r = json.loads((root / 'synthetic-flow-probe-receipt.json').read_text())
packed = (root / 'synthetic-flow-public-whole-outcomes.json.gz').read_bytes()
raw = gzip.decompress(packed)
assert identity(packed) == {'sha256': r['gzip_sha256'], 'bytes': r['gzip_bytes']}
assert identity(raw) == {'sha256': r['raw_sha256'], 'bytes': r['raw_bytes']}
records = json.loads(raw)
counts = collections.Counter()
per_elite = collections.defaultdict(collections.Counter)
for index, row in enumerate(records):
    assert row['id'] == index
    scenario = row['initial_calculate_scenario_from_exact_frozen_expression']
    member = row['synthetic_run_member']
    elite = member['fields']['elite']
    skill = scenario['skill']
    known = member['skill_ranks']
    rank = known.get(str(skill), 10 if elite == 2 else 7)
    assert row['skill_rank_value'] == scenario['skill_rank'] == rank
    assert scenario['elite'] == elite
    choices = list(range(1, elite + 2))
    assert row['available_skill_choices_from_exact_frozen_expression'] == choices
    assert row['selected_skill_available_in_ui'] == (skill in choices)
    outcome = row['public_outcome']
    allowed = skill <= elite + 1 and (elite == 2 or rank <= 7)
    assert outcome['accepted'] == allowed
    key = 'accepted' if allowed else 'original_qualification_error'
    counts[key] += 1
    per_elite[elite][key] += 1
    if allowed:
        assert all(isinstance(outcome[k], str) for k in ('formatted_report', 'technical_report', 'formatted_estimate'))
    else:
        assert outcome['error_type'] == 'ValueError'
        assert outcome['error'] == '当前精英阶段尚未开放所选技能或专精。'
assert len(records) == r['actual_public_calculate_calls'] == 72
assert counts['accepted'] == r['accepted'] == 42
assert counts['original_qualification_error'] == r['errors'] == 30
controls = json.loads((root / 'synthetic-flow-controls.json').read_text())
assert [x['skill_rank_value'] for x in controls] == [7, 10, 7, 10, 10]
archive = own / 'author-flow-static'
archive.mkdir(exist_ok=True)
copies = {}
for name in ('flow_probe.py', 'flow-source-selectors.json', 'synthetic-flow-probe-receipt.json',
             'synthetic-flow-public-whole-outcomes.json.gz', 'synthetic-flow-controls.json', 'FLOW_NOTE.md'):
    data = (root / name).read_bytes()
    dest = archive / name
    assert not dest.exists()
    dest.write_bytes(data)
    copies[name] = identity(data)
receipt = {
    'status': 'PASS_READONLY_STATIC_AND_SAVED_CONTRACT_REVIEW', 'baseline_commit': commit,
    'source_public_files': source_checks, 'ast_selected_method_names': expected_methods,
    'producer_AST_expressions_in_source': {'choices_line': r['source_choices_line'],
                                          'initial_scenario_line': r['source_initial_scenario_line']},
    'saved_contract_outcomes': {'records': len(records), 'accepted': counts['accepted'],
        'original_qualification_errors': counts['original_qualification_error'],
        'per_run_elite': {k: dict(v) for k, v in per_elite.items()},
        'exact_inputs_to_existing_gate_checked': True, 'new_calculate_calls': 0,
        'raw': identity(raw), 'gzip': identity(packed),
        'decompression': 'Python gzip.decompress + complete JSON parse'},
    'synthetic_controls_known_run_unknown_invalid_absent_disabled_ranks': [x['skill_rank_value'] for x in controls],
    'author_linux_import_failure_retained': r['linux_full_app_import_attempt'],
    'validation_scope': 'Author exact immutable AST method bodies/initial choices/scenario expressions plus synthetic controls and public API outcomes; neither actual Qt behavior nor native game mechanics. All selected skills carry equal synthetic rank, so this narrow probe is not a test of unequal per-skill account rank merging.',
    'static_assertion_limit': 'The source compares the original scenario after passing deepcopy to calculate_damage; it does not independently prove the copied input was unchanged. No stronger mutation claim is made.',
    'account_rank_inheritance_or_run_cap_proven': False, 'gate_changed': False,
    'new_gui_wine_or_import_attempts': 0, 'preserved_author_evidence_copies': copies,
    'independent_harness_compile_typo_preserved': 'flow-static-review-attempt1-syntax.log',
    'prior_independent_sealed_evidence_unchanged': True}
(own / 'independent-flow-static-review.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
paths = [p for p in own.rglob('*') if p.is_file() and p.name != 'independent-final-public-manifest.json']
manifest = {'status': 'READONLY_COMPLETE_DEFER', 'baseline_commit': commit,
            'scope': 'Explicit independent public evidence only; no frozen75 whole tree or private files. Original source-only seal preserved, additional copies/static review appended.',
            'files': {str(p.relative_to(own)): identity(p.read_bytes()) for p in sorted(paths)}}
(own / 'independent-final-public-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
for path, expected in manifest['files'].items():
    assert identity((own / path).read_bytes()) == expected
for file in ('independent-flow-static-review.json', 'independent-final-public-manifest.json'):
    print(json.dumps({'file': file, **identity((own / file).read_bytes())}))
print(json.dumps({'status': 'PASS readonly / mechanics defer', 'manifest_files': len(paths),
                  'source_files': len(source_checks), 'saved_records_checked': len(records), 'new_calls': 0}))
