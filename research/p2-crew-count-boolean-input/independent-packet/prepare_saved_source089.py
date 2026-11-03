"""Independent saved/public source audit only; never imports project code or opens real .local."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import math
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / 'p2-crew-count-boolean-089-source'
REPO = Path('/workspace/rougezhushou')
SNAP = ROOT / 'source-preparation-snapshots'
SNAP.mkdir(exist_ok=True)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def dump(name, value):
    (ROOT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def strict(a, b):
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return list(a) == list(b) and all(strict(a[key], b[key]) for key in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(strict(x, y) for x, y in zip(a, b))
    if isinstance(a, float):
        return a.hex() == b.hex()
    return a == b

def native_tree_matches(value, tree):
    name = type(value).__name__
    if tree['type'] != name:
        return False
    if type(value) is dict:
        return len(value) == len(tree['items']) and all(
            native_tree_matches(key, item[0]) and native_tree_matches(item_value, item[1])
            for (key, item_value), item in zip(value.items(), tree['items']))
    if type(value) is list:
        return len(value) == len(tree['items']) and all(native_tree_matches(item, node) for item, node in zip(value, tree['items']))
    if type(value) is float:
        return value.hex() == tree['hex']
    return strict(value, tree['value'])

manifest_path = SOURCE / 'public-manifest.json'
handoff_path = SOURCE / 'handoff-final089-source.json'
assert sha(manifest_path.read_bytes()) == 'adf1b2a619cadea7c747669e9bb2f9c710c5d12ce83de48a63afcc992b3b7aca'
assert sha(handoff_path.read_bytes()) == '0562b57a8d628a3fbe29cc8ba60c085f953bfcff9c74c877dc9d12e6ac9b697d'
manifest = json.loads(manifest_path.read_text())
assert manifest['status'] == 'FINAL_SEALED' and len(manifest['files']) == 38
bindings = []
for row in manifest['files']:
    src = Path(row['source_path'])
    assert src.resolve().is_relative_to(SOURCE.resolve()) and '.local' not in src.parts
    assert src == SOURCE / row['archive_path']
    raw = src.read_bytes()
    assert len(raw) == row['bytes'] and sha(raw) == row['sha256']
    dst = SNAP / row['archive_path']
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    assert dst.read_bytes() == raw
    bindings.append({'source_path': str(src), 'archive_path': str(dst.relative_to(ROOT)),
        'bytes': len(raw), 'sha256': sha(raw)})
shutil.copy2(manifest_path, SNAP / 'public-manifest.json')
plan = json.loads((SNAP / 'authorized-five-case-plan089.json').read_text())
summary = json.loads((SNAP / 'five-reproduction-summary.json').read_text())
assert summary['groups'] == 5 and summary['actual_RunState_file_function_entries']['apply'] == 10
assert summary['explicit_method_calls'] == {'RunState_constructor': 5, 'seed_apply': 5, 'subject_apply': 5}
groups = []
uuids = []
for n, planned in enumerate(plan['groups'], 1):
    path = SNAP / f'case-{n}.json'
    record = json.loads(path.read_text())
    assert strict(record['case'], planned)
    identity = planned['id']
    assert record['file_path'] == str(SOURCE / 'runtime' / identity / 'run.json')
    assert '.local' not in Path(record['file_path']).parts
    for value_key, native_key in [
        ('initial_state', 'initial_state_typed'), ('before_state', 'before_state_typed'),
        ('after_state', 'after_state_typed'), ('seed_observed_before', 'seed_caller_typed_before'),
        ('seed_observed_after', 'seed_caller_typed_after'), ('observed_before', 'caller_typed_before'),
        ('observed_after', 'caller_typed_after')]:
        assert native_tree_matches(record[value_key], record[native_key]), (identity, value_key)
    assert strict(record['seed_caller_typed_before'], record['seed_caller_typed_after'])
    assert strict(record['caller_typed_before'], record['caller_typed_after'])
    assert strict(record['seed_observed_before'], record['seed_observed_after'])
    assert strict(record['observed_before'], record['observed_after'])
    assert type(record['observed_before']['crew_count']) is type(planned['crew_count'])
    assert strict(record['observed_before']['crew_count'], planned['crew_count'])
    assert record['seed_return'] is record['subject_return'] is True
    before_path = SNAP / 'runtime' / identity / 'seed-persisted.json'
    after_path = SNAP / 'runtime' / identity / 'run.json'
    before_raw, after_raw = before_path.read_bytes(), after_path.read_bytes()
    assert sha(before_raw) == record['before_persisted_JSON_bytes_sha256']
    assert sha(after_raw) == record['after_persisted_JSON_bytes_sha256']
    before_json, after_json = json.loads(before_raw), json.loads(after_raw)
    assert strict(before_json, record['before_persisted_JSON']) and strict(after_json, record['after_persisted_JSON'])
    assert strict(before_json, record['before_state']) and strict(after_json, record['after_state'])
    assert native_tree_matches(before_json, record['before_state_typed'])
    assert native_tree_matches(after_json, record['after_state_typed'])
    initial, before, after = record['initial_state'], record['before_state'], record['after_state']
    run_id = initial['id']
    assert type(run_id) is str and re.fullmatch(r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}', run_id)
    uuids.append(run_id)
    assert initial['id'] == before['id'] == after['id']
    assert type(initial['started_at']) is float and math.isfinite(initial['started_at'])
    assert initial['started_at'].hex() == before['started_at'].hex() == after['started_at'].hex()
    assert record['seed_captured_at'] == initial['started_at'] + 1
    assert record['subject_captured_at'] == initial['started_at'] + 2
    assert before['last_read'] == record['seed_captured_at'] and after['last_read'] == record['subject_captured_at']
    assert list(before['operators']) == planned['seed_ids']
    assert all(member['present'] is True for member in before['operators'].values())
    departed = [key for key, member in after['operators'].items() if member['present'] is False]
    assert departed == planned['expected_source_departures'] == record['source_expected_departures_confirmed']
    assert strict(before['history'], after['history'][:len(before['history'])])
    new_history = after['history'][len(before['history']):]
    departures = [event['id'] for event in new_history if event['kind'] == 'operator_no_longer_present']
    assert departures == departed
    assert all(event['at'] == record['subject_captured_at'] for event in new_history)
    assert strict(record['after_history'], after['history'])
    assert before['crew_count'] == planned['seed_crew'] and type(before['crew_count']) is int
    if planned['crew_count'] is None:
        assert after['crew_count'] == planned['seed_crew'] and type(after['crew_count']) is int
    else:
        assert strict(after['crew_count'], planned['crew_count'])
    groups.append({'case': identity, 'crew_value': planned['crew_count'],
        'crew_native_type': type(planned['crew_count']).__name__, 'actual_uuid_preserved': run_id,
        'actual_started_at': initial['started_at'], 'actual_started_at_hex': initial['started_at'].hex(),
        'seed_captured_at': record['seed_captured_at'], 'seed_captured_at_hex': record['seed_captured_at'].hex(),
        'subject_captured_at': record['subject_captured_at'], 'subject_captured_at_hex': record['subject_captured_at'].hex(),
        'departures': departed, 'seed_persisted_bytes': len(before_raw), 'seed_persisted_sha256': sha(before_raw),
        'subject_persisted_bytes': len(after_raw), 'subject_persisted_sha256': sha(after_raw),
        'all_saved_native_inputs_states_disk_and_history_fields_verified': True})
assert len(set(uuids)) == 5

actual_head = subprocess.run(['git', '-C', str(REPO), 'rev-parse', 'HEAD'], check=True,
    capture_output=True, text=True).stdout.strip()
source_names = ['rouge/run_state.py', 'rouge/run_recognition.py', 'rouge/app.py', 'rouge/visual_recognition.py']
current_sources = []
for relative in source_names:
    src = REPO / relative
    raw = src.read_bytes()
    fixed = (SNAP / 'frozen' / relative).read_bytes()
    assert raw == fixed
    dst = ROOT / 'current-public-source' / relative
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(raw)
    current_sources.append({'source_path': str(src), 'archive_path': str(dst.relative_to(ROOT)),
        'bytes': len(raw), 'sha256': sha(raw), 'matches_sealed_source_base0f27027': True})
run = (ROOT / 'current-public-source/rouge/run_state.py').read_text()
producer = (ROOT / 'current-public-source/rouge/run_recognition.py').read_text()
app = (ROOT / 'current-public-source/rouge/app.py').read_text()
assert "crew=observed.get('crew_count')" in run
assert "if crew is not None and len({m['id'] for m in members})==crew:" in run
assert "full_crew=type(crew) is int and len(incoming)==crew" in run
assert "if not observed or captured_at<max(self.state['started_at'],self.state.get('last_read') or 0):return False" in run
assert "if reused_run and reused_run!=self.state['id']:return False" in run
assert "values={int(t['text']) for t in texts if valid(t)}" in producer
assert producer.count("values={int(text) for _,text,score in raw or []") == 2
assert "crew_count=near_number(image,texts,crew,engine,side='right') if crew else None" in producer
assert "if member and not member.get('present',True):member=None" in app

def quote(path, exact):
    text = (ROOT / path).read_text()
    assert exact in text
    return {'archive_path': path, 'line': text[:text.index(exact)].count('\n') + 1, 'quote': exact}
source_quotes = [quote('current-public-source/rouge/run_state.py', "crew=observed.get('crew_count')"),
    quote('current-public-source/rouge/run_state.py', "if crew is not None and len({m['id'] for m in members})==crew:"),
    quote('current-public-source/rouge/run_state.py', "full_crew=type(crew) is int and len(incoming)==crew"),
    quote('current-public-source/rouge/run_recognition.py', "values={int(t['text']) for t in texts if valid(t)}"),
    quote('current-public-source/rouge/run_recognition.py', 'if len(values)==1:return next(iter(values))'),
    quote('current-public-source/rouge/app.py', "if member and not member.get('present',True):member=None")]
dump('initial-local-source-discovery089.json', {'version': 1, 'stage': 'Optional public path search',
    'actual_stderr': 'rg: /workspace/rougezhushou/app.py: No such file or directory (os error 2)',
    'command_exit_code': 0, 'path_guess_errors': 1, 'actual_public_path_used': 'rouge/app.py',
    'optional_first_multifile_tool_output_truncated': True,
    'resolution': 'Narrow exact source reads and complete file-byte snapshots, no inference from truncated output.',
    'product_or_state_operations': 0})
receipt = {'version': 1, 'status': 'PASS_SOURCE_PACKAGE_AND_5_SAVED_NATIVE_CASES_FORMAL_DRAFT_PENDING',
    'prepared_at_utc': datetime.now(timezone.utc).isoformat(), 'source_base_commit': summary['base_commit'],
    'actual_current_HEAD_at_public_source_snapshot': actual_head, 'current_clean_state_claimed': False,
    'source_manifest_sha256': sha(manifest_path.read_bytes()), 'source_handoff_sha256': sha(handoff_path.read_bytes()),
    'all38_source_manifest_files_byte_hash_verified_and_preserved': True, 'source_input_bindings': bindings,
    'current_public_source_bindings': current_sources, 'saved_case_reviews': groups,
    'cross_case_UUID_or_time_normalization': False, 'cross_case_full_state_equality_claimed': False,
    'observed_source_method_counts_not_new_calls': {'constructors': 5, 'seed_apply': 5, 'subject_apply': 5, 'actual_apply_entries': 10},
    'recognizer_crew_producer_contract': 'near_number returns int(text) unique candidate or integer zero, else None; roster/map routing assigns that return or None, never bool',
    'actual_alias_failure': 'Observed False/empty and True/subset become full roster because len(unique IDs)==crew accepts bool-int equality, write bool into remembered crew and mark omitted members departed',
    'fix_authorization_boundary': 'Only exclude bool immediately after the local crew read by treating it as None. Preserve previous known state crew count, process incoming members and all other observations normally; no early return or new exception.',
    'existing_other_crew_guard': 'restore_origin_discovery_buffs already requires type(crew) is int; keep unchanged',
    'old_priority': 'Empty/stale capture and cross-run gates precede personal-buff validation/repair and all later state merges; authorized local late guard must not move or change those checks.',
    'old_nonbool_values_contract': 'None/int0/int1 and every other nonbool keep prior behavior; this is not a new global count validator.',
    'static_UI_training_scope': 'recruited_operator_ids/current_operator_state gate present membership; departed run member falls back to account observations, affecting training/skill/personal source selection statically.',
    'damage_numeric_P1_buff_or_actual_live_departure_mechanism_validation': False,
    'source_quotes': source_quotes, 'real_local_files_accessed': False,
    'reviewer_new_calls': {'RunState_constructor': 0, 'RunState_apply': 0, 'production_helper': 0,
        'damage_or_app_API': 0, 'formatter': 0, 'tests': 0, 'Qt': 0, 'Wine': 0, 'network': 0, 'tracked_changes': 0},
    'author_final_product_freeze_received': False,
    'next': 'Wait for final product freeze and root-assigned temporary-state/test budget; no automatic execution.'}
dump('source-preparation-review089.json', receipt)
print(json.dumps({'status': receipt['status'], 'file_count_verified': 38, 'saved_cases_verified': 5,
    'receipt_sha256': sha((ROOT / 'source-preparation-review089.json').read_bytes()), 'new_RunState_calls': 0}))
