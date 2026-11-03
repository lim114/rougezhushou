"""Freeze named root086 and actual producer parameters before one44 API pass."""
import ast
import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = Path('/workspace/rougezhushou')
COMMIT = '0f27027e7e1f49c08f298706b599e310e299238b'
assert (HERE / 'preparation-source-only-stage090-086/immutable-snapshot-manifest.json').is_file()
initial = json.loads((HERE / 'preparation-source-only-stage090-086/initial-stage-manifest-original.json').read_bytes())
assert len(initial['files']) == 35
listed = subprocess.check_output(['git', 'ls-tree', '-r', '-z', COMMIT], cwd=REPO)
entries = {}
for entry in listed.split(b'\0'):
    if not entry:
        continue
    head, name = entry.split(b'\t', 1)
    mode, kind, blob = head.split()
    name = name.decode()
    if name.split('/')[0] in ('rouge', 'tests', 'scripts') and Path(name).suffix in ('.py', '.json'):
        assert kind == b'blob'
        entries[name] = blob.decode()
assert len(entries) == 724
process = subprocess.Popen(['git', 'cat-file', '--batch'], cwd=REPO,
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
names = sorted(entries)
process.stdin.write(''.join(entries[name] + '\n' for name in names).encode())
process.stdin.close()
rows = []
package = HERE / 'public-schema-086-ui090'
public = {}
for name in names:
    blob, kind, length = process.stdout.readline().rstrip(b'\n').split()
    raw = process.stdout.read(int(length))
    assert process.stdout.read(1) == b'\n' and blob.decode() == entries[name] and kind == b'blob'
    assert raw == (REPO / name).read_bytes(), name
    digest = hashlib.sha256(raw).hexdigest()
    rows.append({'source_path': name, 'git_blob_sha1': entries[name], 'bytes': len(raw), 'sha256': digest})
    if name.startswith('rouge/'):
        target = package / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        public[name] = digest
assert process.wait() == 0 and len(public) == 125
assert public['rouge/damage.py'] == '6cc15cf93eb52fc42120fff6b795e2cbbf2903cf0af8d7d293ffea9f73f121c6'
assert public['rouge/operator_engine.py'] == 'c6a7b5e5cd444480f3579a8174246a31f891cb7a2b1c93bbf0826aa4a7765c68'
proof = {'status': 'PASS_NAMED_ROOT086_724_MAINTAINED_FILES_PUBLIC125_EXACT',
    'root_commit': COMMIT, 'maintenance_python_json_files': len(rows),
    'public_files': len(public), 'public_source_sha256': public, 'files': rows,
    'overlay': False, 'all_bytes_match_current_and_named_git': True,
    'application_API_calls': 0, 'formatter_calls': 0, 'production_helper_calls': 0,
    'Qt_calls': 0, 'Wine_calls': 0}
(HERE / 'root086-ui090-source-proof.json').write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n')

plan_path = HERE / 'small-explicit-pair-plan090.json'
plan = json.loads(plan_path.read_bytes())
plan['source86_product_final'] = True
plan['actual_root86_commit'] = COMMIT
plan['status'] = 'DECLARATIVE_REAL_ROOT086_PENDING_SINGLE_BOUNDED_API_PREFLIGHT'
plan['shared_Qt_controls_reset_explicitly'] = {'continuous_attacks': True, 'healing_targets': 1,
    'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0,
    'limit_window': True, 'window_seconds': 30.0, 'relic_ids': []}
plan['qualification_and_coveredmodule_pairs'][1]['source_relation'] = (
    'Qualified selected颂乐音符.max_cnt12 overrides skill ratio1; actual normal plan and consumed signal must be observed in the same call. '
    'S1 early duration/rechargeNone and S2switch do not run normal; S3 uses original cycle/continuous gate. Never infer consumption from finalcycle.')
plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n')
option_tree = ast.parse((package / 'rouge/operator_options.py').read_bytes())
options = ast.literal_eval(next(node.value for node in option_tree.body
    if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == 'OPTIONS'
                                           for target in node.targets)))
cases = []
for kind, key in [('active', 'active_pairs'), ('qualification', 'qualification_and_coveredmodule_pairs'),
                  ('hidden', 'hidden_key_omission_pairs')]:
    for pair in plan[key]:
        owner, number = pair['owner'], pair['skill']
        defaults = {item[0]: item[2] for item in options[owner] if number in item[4]}
        args = {'operator': owner, 'skill': number, 'skill_rank': pair['skill_rank'],
            **pair['training_fields'], 'timing_mode': 'frames', 'window_seconds': 30.0,
            'healing_targets': 1, 'continuous_attacks': True, 'deployment_elapsed_seconds': 0.0,
            'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': [], **defaults}
        field = pair['field']
        if kind == 'hidden':
            assert field not in defaults
            states = pair['hidden_widget_checked_states']
        else:
            assert field in defaults and type(defaults[field]) is bool
            states = pair['states']
        for state in states:
            assert type(state) is bool
            requested = json.loads(json.dumps(args))
            if kind != 'hidden':
                requested[field] = state
            cases.append({'section': 86, 'pair_id': pair['id'], 'kind': kind, 'field': field,
                'widget_checked': state, 'field_serialized': kind != 'hidden',
                'input': requested, 'context': f"{pair['id']} checked={state}"})
assert len(cases) == 44
unique = {json.dumps(case['input'], ensure_ascii=False, sort_keys=True, separators=(',', ':')) for case in cases}
data = {'root_source_commit': COMMIT, 'UI_state_design_records': 44, 'pair_groups': 22,
    'unique_requested_calculation_inputs': len(unique), 'case_input_origin': 'Exact real bool/number Qt producer values, cultivation readonly state; automatic base_attack left to existing public preparation.',
    'rows': cases, 'new_API_calls': 0}
(HERE / 'cases090-section086.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
(HERE / 'cases090_section086.py').write_text('"""Pure data for pendingUI09086; no product imports or execution."""\n\ndef cases090_section086():\n    return ' + repr(cases) + '\n')
print(json.dumps({'source_files': len(rows), 'public_files': len(public), 'case_design_records': len(cases),
    'unique_calculation_inputs': len(unique), 'new_API_calls': 0}))
