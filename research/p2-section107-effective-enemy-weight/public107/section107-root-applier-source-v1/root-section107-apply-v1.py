"""Root-only exact section107 application, prepared as Source until actual Gold.

Only engine local segment + one new test + one cloud selector are writable.
Full available selector union automatically includes cloud MODULES; its original
helper/NEW_MODULES stays byte-for-byte unchanged. No product imports are needed.
"""
import argparse
import ast
from copy import deepcopy
import datetime
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path('/workspace/rougezhushou')
BASE = Path('/workspace/.continuation')
PACKET = BASE / 'section107-coupled-weight-consumer-source-v1'
SELECTOR = 'tests.test_aglna_gravity_weight_107'
TEST_PATH = 'tests/test_aglna_gravity_weight_107.py'
ENGINE_PATH = 'rouge/operator_engine.py'
CLOUD_PATH = 'scripts/verify_cloud.py'
FULL_PATH = 'scripts/verify_full_available.py'
MANIFEST_SHA = '7e8e213b4ca82b4b08bd2b924198e8fefacff26385ce71b85746f4c0a5616b10'
TRANSPORT_SHA = '6066dce8003d68a58ad71fc4210a9beb9495225b05b392f2d9ae57eeb9624522'
TEST_SHA = '62766f1d8cae2b4ef4618ae4f90dddb0c1e9ce8d165f272f1d0fc9caa3b87e8c'
ORIGINAL_SHA = '0a38276dda0ee3e6640f203cc61397686b6e83c365656578b6896dc461563d00'
CONSUMER_REVIEW_SHA = '6365cd6375c7008fe225448cd7c837492c9bf80a7be318addc74841144143e6b'
PREVIEW_REVIEW_SHA = 'e53b520bfd5df419e5a24b1a5c62d60779ff6932e055f5c96b6c24d3cd187a00'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_bytes())


def source_map():
    return {p.relative_to(ROOT).as_posix(): sha(p.read_bytes())
            for folder in ('rouge', 'tests', 'scripts')
            for p in sorted((ROOT / folder).rglob('*'))
            if p.is_file() and p.suffix in ('.py', '.json') and '__pycache__' not in p.parts}


def unique_assignment(tree, name):
    rows = [n for n in tree.body if isinstance(n, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == name for t in n.targets)]
    assert len(rows) == 1, name
    return rows[0]


def literal_assignment(raw, name):
    return ast.literal_eval(unique_assignment(ast.parse(raw), name).value)


def verify_engine_AST(original, candidate):
    old_tree = ast.parse(original)
    new_tree = ast.parse(candidate)
    extra = ast.parse("weight+=self.s.get('_relic_enemy_effects',{}).get('weight_delta',0)").body[0]
    key = ast.dump(extra, include_attributes=False)
    additions = [n for n in ast.walk(new_tree) if isinstance(n, ast.AugAssign)
                 and ast.dump(n, include_attributes=False) == key]
    assert len(additions) == 1
    assert not any(isinstance(n, ast.AugAssign) and ast.dump(n, include_attributes=False) == key
                   for n in ast.walk(old_tree))
    added = additions[0]
    removed = 0
    for node in ast.walk(new_tree):
        for field, values in ast.iter_fields(node):
            if isinstance(values, list) and any(value is added for value in values):
                setattr(node, field, [value for value in values if value is not added])
                removed += 1
    assert removed == 1
    assert ast.dump(old_tree, include_attributes=False) == ast.dump(new_tree, include_attributes=False)


def verify_cloud_AST(original, candidate):
    old_tree = ast.parse(original)
    new_tree = ast.parse(candidate)
    old_assignment = unique_assignment(old_tree, 'MODULES')
    new_assignment = unique_assignment(new_tree, 'MODULES')
    old = ast.literal_eval(old_assignment.value)
    new = ast.literal_eval(new_assignment.value)
    assert type(old) is type(new) is tuple and len(old) == 117 and len(new) == 118
    assert SELECTOR not in old and new == (SELECTOR,) + old
    new_assignment.value = deepcopy(old_assignment.value)
    assert ast.dump(old_tree, include_attributes=False) == ast.dump(new_tree, include_attributes=False)
    return old, new


def selector_union(full_raw, cloud_modules, core_raw):
    tree = ast.parse(full_raw)
    extra = ast.literal_eval(unique_assignment(tree, 'NEW_MODULES').value)
    assert type(extra) is tuple and len(extra) == 41
    mains = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'main']
    assert len(mains) == 1
    imports = [n for n in ast.walk(mains[0]) if isinstance(n, ast.ImportFrom)
               and n.module == 'verify_cloud' and [(v.name, v.asname) for v in n.names] == [('MODULES', None)]]
    assert len(imports) == 1
    assignments = [n for n in ast.walk(mains[0]) if isinstance(n, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == 'selectors' for t in n.targets)]
    assert len(assignments) == 1
    known = ast.parse("list(dict.fromkeys(historical['test_modules'] + list(NEW_MODULES) + list(MODULES)))", mode='eval').body
    assert ast.dump(assignments[0].value, include_attributes=False) == ast.dump(known, include_attributes=False)
    historical = json.loads(core_raw)['test_modules']
    assert type(historical) is list
    return list(dict.fromkeys(historical + list(extra) + list(cloud_modules)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--gold-dir', required=True)
    parser.add_argument('--gold-exit', required=True)
    parser.add_argument('--runner', required=True)
    args = parser.parse_args()
    receipt_path = BASE / 'resume107-applied-source-v1.json'
    assert not receipt_path.exists()
    assert subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip() == 'codex/p2-development'
    assert not subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip()
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    publication_path = BASE / 'section106-publication-v1.json'
    publication_raw = publication_path.read_bytes()
    publication = json.loads(publication_raw)
    assert publication['section'] == 106 and publication['kind'] == 'ACTUAL_COMMIT_PUSH_REMOTE_EQUAL_CLEAN'
    assert publication['local_HEAD'] == publication['remote_HEAD'] == head
    assert publication['commit_primary_exit'] == publication['push_primary_exit'] == 0
    assert publication['clean'] is True and publication['source_files'] == 749 and publication['next_section'] == 107
    checkpoint = read_json(ROOT / 'DEVELOPMENT_CHECKPOINT.json')
    assert checkpoint['completed_sections'] == 106 and checkpoint['next_section'] == 107
    assert checkpoint['full_validation_due'] is False
    closure = read_json(ROOT / 'verification/full-105/closure.json')
    assert checkpoint['last_full_validation'] == checkpoint['current_full105_checkpoint'] == closure
    assert closure['after_section'] == 105 and closure['batch_validation_closed'] is True
    assert closure['status'] == 'PASSED_AVAILABLE_MAINTAINED_AND_BOUNDED_GUI_SCOPE'
    assert closure['available_checks_passed'] is True and closure['source_files'] == 748
    assert closure['actual_gui_checks'] == 4283 and closure['saved_states'] == 52
    assert closure['actual_gui_attempts'] == 2 and closure['full095_deferred_preserved'] is True
    assert checkpoint['next_full_validation_after'] == checkpoint['current_batch_commit_policy']['next_full_validation_after'] == 110
    guard_path = BASE / 'resume106-applied-source-v1.json'
    guard_raw = guard_path.read_bytes()
    guard = json.loads(guard_raw)
    assert guard['section'] == 106 and guard['source_count'] == 749
    assert len(guard['source_sha256']) == 749 and source_map() == guard['source_sha256']
    assert set(guard['source_additional_sha256']) == {'CORE_0.70_VERIFICATION.json'}
    core_raw = (ROOT / 'CORE_0.70_VERIFICATION.json').read_bytes()
    assert sha(core_raw) == guard['source_additional_sha256']['CORE_0.70_VERIFICATION.json']

    original_path = BASE / 'section107-original-weight-actual-linux-v1/observations.json'
    original_raw = original_path.read_bytes()
    assert sha(original_raw) == ORIGINAL_SHA
    original_exit = BASE / 'section107-original-weight-actual-linux-v1.exit-code'
    assert original_exit.read_bytes() == b'0\n'
    original = json.loads(original_raw)
    assert original['observation_only'] is True and original['product_pass'] is False
    assert original['observation_complete'] is original['source_and_CORE_unchanged'] is True
    assert original['source_before'] == original['source_after'] and len(original['source_before']) == 748
    assert original['CORE_before'] == original['CORE_after'] == sha(core_raw)
    assert original['planned_calculation_cases'] == 14 and original['planned_previews'] == 2
    assert original['actual_explicit_consumer_calls'] == 74 and original['actual_explicit_public_loader_calls'] == 1
    assert original['actual_native_records'] == 89 and original['consumer_error_count'] == original['blocked_phase_count'] == 0
    assert original['source_before'][ENGINE_PATH] == guard['source_sha256'][ENGINE_PATH]

    gold_dir = Path(args.gold_dir).resolve()
    gold_exit = Path(args.gold_exit).resolve()
    runner_path = Path(args.runner).resolve()
    assert gold_dir != ROOT and ROOT not in gold_dir.parents
    assert runner_path != ROOT and ROOT not in runner_path.parents
    gold_path = gold_dir / 'receipt.json'
    gold_raw = gold_path.read_bytes()
    gold = json.loads(gold_raw)
    runner_raw = runner_path.read_bytes()
    assert gold_exit.read_bytes() == b'0\n'
    assert gold['kind'] == 'ROOT_ACTUAL_107_REAL_MAINWINDOW'
    assert gold['passed'] is gold['workflow_complete'] is True and gold['phase'] == 'gold'
    assert gold['runner_sha256'] == sha(runner_raw)
    assert literal_assignment(runner_raw, 'COUNT') == len(gold['rows']) == 13
    assert literal_assignment(runner_raw, 'ORIGINAL_SHA') == gold['original_receipt_sha256'] == ORIGINAL_SHA
    assert literal_assignment(runner_raw, 'TRANSPORT_SHA') == gold['transport_sha256'] == TRANSPORT_SHA
    assert literal_assignment(runner_raw, 'TEST_SHA') == TEST_SHA
    assert gold['original_raw_exit_sha256'] == sha(original_exit.read_bytes())
    assert gold['source_guard_sha256'] == sha(guard_raw)
    assert gold['source_before'] == gold['source_after'] == guard['source_sha256']
    assert gold['source_additional_before'] == gold['source_additional_after'] == guard['source_additional_sha256']
    assert gold['source_drift'] == gold['Qt_errors'] == []
    assert gold['native_windows_verified'] is gold['private_state_access'] is gold['game_chat_sampling_executed'] is False

    manifest_raw = (PACKET / 'packet-manifest.json').read_bytes()
    assert sha(manifest_raw) == MANIFEST_SHA
    manifest = json.loads(manifest_raw)
    assert len(manifest['files']) == 6 and manifest['author_Runtime_executed'] is False
    assert manifest['product_pass'] is manifest['section_complete'] is False
    for item in manifest['files']:
        raw = (PACKET / item['path']).read_bytes()
        assert len(raw) == item['bytes'] and sha(raw) == item['sha256'], item['path']
    for relative, want in (
        ('section107-coupled-weight-consumer-independent-source-v1/review.json', CONSUMER_REVIEW_SHA),
        ('section107-coupled-weight-preview-independent-source-v1/review.json', PREVIEW_REVIEW_SHA)):
        review_raw = (BASE / relative).read_bytes()
        assert sha(review_raw) == want
        assert json.loads(review_raw)['status'] == 'NO_SOURCE_BLOCKER_RUNTIME_PENDING'
    transport_raw = (PACKET / 'exact-local-transports.json').read_bytes()
    assert len(transport_raw) == 1262 and sha(transport_raw) == TRANSPORT_SHA
    transport = json.loads(transport_raw)
    assert len(transport['changes']) == 1
    change = transport['changes'][0]
    assert change['path'] == ENGINE_PATH and change['old_count'] == 1
    engine_original = (ROOT / ENGINE_PATH).read_bytes()
    assert len(engine_original) == change['bytes_before'] and sha(engine_original) == change['sha256_before']
    before = change['old'].encode('utf-8')
    after = change['new'].encode('utf-8')
    assert engine_original.count(before) == 1 and engine_original.count(after) == 0
    engine_candidate = engine_original.replace(before, after, 1)
    assert engine_candidate.count(after) == 1 and engine_candidate.replace(after, before, 1) == engine_original
    assert len(engine_candidate) == change['bytes_after_source_composition']
    assert sha(engine_candidate) == change['sha256_after_source_composition']
    verify_engine_AST(engine_original, engine_candidate)
    assert not (ROOT / TEST_PATH).exists()
    test_raw = (PACKET / 'test_aglna_gravity_weight_107.py').read_bytes()
    assert len(test_raw) == 13845 and sha(test_raw) == TEST_SHA
    test_methods = [n for n in ast.walk(ast.parse(test_raw)) if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')]
    assert len(test_methods) == 11
    cloud_original = (ROOT / CLOUD_PATH).read_bytes()
    needle = b'MODULES = (\n'
    insert = b'    "tests.test_aglna_gravity_weight_107",\n'
    assert cloud_original.count(needle) == 1 and insert not in cloud_original
    cloud_candidate = cloud_original.replace(needle, needle + insert, 1)
    assert cloud_candidate.replace(needle + insert, needle, 1) == cloud_original
    old_modules, new_modules = verify_cloud_AST(cloud_original, cloud_candidate)
    full_raw = (ROOT / FULL_PATH).read_bytes()
    old_union = selector_union(full_raw, old_modules, core_raw)
    new_union = selector_union(full_raw, new_modules, core_raw)
    assert SELECTOR not in old_union and new_union.count(SELECTOR) == 1
    assert len(old_union) == 240 and len(new_union) == 241
    assert [item for item in new_union if item != SELECTOR] == old_union
    outputs = {ENGINE_PATH: engine_candidate, TEST_PATH: test_raw, CLOUD_PATH: cloud_candidate}
    assert len(outputs) == 3 and FULL_PATH not in outputs
    for name, raw in outputs.items():
        compile(raw, name, 'exec')
    compile(runner_raw, str(runner_path), 'exec')
    # All real receipts/source checks/compile preflight precede the first write.
    assert source_map() == guard['source_sha256']
    assert (ROOT / FULL_PATH).read_bytes() == full_raw
    assert (ROOT / 'CORE_0.70_VERIFICATION.json').read_bytes() == core_raw
    for name, raw in outputs.items():
        (ROOT / name).write_bytes(raw)
    sources = source_map()
    assert len(sources) == 750 and set(sources) - set(guard['source_sha256']) == {TEST_PATH}
    assert set(guard['source_sha256']) - set(sources) == set()
    assert {name for name in guard['source_sha256'] if sources[name] != guard['source_sha256'][name]} == {ENGINE_PATH, CLOUD_PATH}
    assert all(sources[name] == sha(raw) for name, raw in outputs.items())
    assert (ROOT / FULL_PATH).read_bytes() == full_raw
    assert (ROOT / 'CORE_0.70_VERIFICATION.json').read_bytes() == core_raw
    assert len(literal_assignment((ROOT / CLOUD_PATH).read_bytes(), 'MODULES')) == 118
    receipt = {
        'section': 107, 'status': 'ACTUALLY_APPLIED_RUNTIME_PENDING', 'baseline_HEAD': head,
        'actual_prior_publication': publication, 'actual_prior_publication_sha256': sha(publication_raw),
        'applied_at_Beijing': datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
        'source_sha256': sources, 'source_additional_sha256': guard['source_additional_sha256'],
        'source_count': 750, 'changed_paths': sorted(outputs),
        'applier_source_sha256': sha(Path(__file__).read_bytes()),
        'prior_complete_source_guard_sha256': sha(guard_raw),
        'candidate_packet_manifest_sha256': sha(manifest_raw),
        'exact_local_transport_sha256': sha(transport_raw),
        'consumer_independent_source_review_sha256': CONSUMER_REVIEW_SHA,
        'preview_independent_source_review_sha256': PREVIEW_REVIEW_SHA,
        'original_actual_weight_observations_sha256': sha(original_raw),
        'original_observation_source_count': 748,
        'actual_healthy_Gold_receipt_path': str(gold_path),
        'actual_healthy_Gold_receipt_sha256': sha(gold_raw),
        'actual_healthy_Gold_source_count': 749, 'actual_healthy_Gold_windows': len(gold['rows']),
        'test_source_sha256': sha(test_raw), 'window_source_sha256': sha(runner_raw),
        'cloud_selectors_before': len(old_modules), 'cloud_selectors_after': len(new_modules),
        'full_NEW_MODULES_unchanged': True, 'full_helper_source_sha256_unchanged': sha(full_raw),
        'full_selector_union_before': len(old_union), 'full_selector_union_after': len(new_union),
        'registry_choice': 'Cloud-only prepend. The unchanged full main imports cloud MODULES and merges it with historical and NEW_MODULES; no redundant full helper append.',
        'scope': ['Original base declaration validation preserved', 'Only existing prepared signed weight_delta added once to qualified talent consumer', 'New11 actual API test methods; execution pending'],
        'runtime_checks_passed_claimed': False, 'native_windows_verified': False,
    }
    with receipt_path.open('x', encoding='utf-8') as stream:
        json.dump(receipt, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps({'section': 107, 'applied': True, 'source_files': len(sources), 'cloud_selectors': len(new_modules), 'changed_paths': sorted(outputs)}))


if __name__ == '__main__':
    main()
