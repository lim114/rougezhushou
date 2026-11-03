"""Root-only exact local correction of the new107 test's legacy boundary control.

Root alone may execute this sealed Source. The actual failed related run and
original twelve-call diagnosis are preserved. No product/timing/registry write.
"""
import argparse
import ast
from collections import Counter
from copy import deepcopy
import datetime
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path('/workspace/rougezhushou')
BASE = Path('/workspace/.continuation')
TEST = 'tests/test_aglna_gravity_weight_107.py'
OLD_TEST_SHA = '62766f1d8cae2b4ef4618ae4f90dddb0c1e9ce8d165f272f1d0fc9caa3b87e8c'
NEW_TEST_SHA = '2c5eab4be5f484ca3eaf45d19eeb1f1067661a36c42ea41297a5ad1ec22ecc51'
OLD_GUARD_SHA = '9f06db822007088a569ab571abb1b950bdc9701ad3eaa366603b713c80f9d897'
FAILED_LINUX_SHA = '6f407da19b0899d77331bd23a9eb3abab92edb8fd4413aab5fa7e8042147ae82'
DIAGNOSIS_SHA = 'a4748413342aab7a5ee896beabadafd74553c82fdcc045bd68c8f942b777172b'
PUBLICATION_SHA = 'dbd3335c8041ca7995212c040de31155482715c4ca5e901105e580a5db995de8'
NEW_MF_SHA = '6fca6062da9338b8d116d0402d91b807e00edf8a72f007340490bb9f4b649115'
TRANSPORT_SHA = 'f496c48e7bec87edc966dfc85230e06009329473164774ad8383ef16d7314365'
NEW_REVIEW_SHA = '13c8b59a0c7797620c9bd57dfbdf41982bf4669fe7f87f75d9b6494b09a95bc2'
CHANGED_METHOD = 'test_locked_talent_empty_enemies_and_zero_windows_do_not_create_hits'
ADDED_METHOD = 'test_continuous_empty_ranges_preserve_existing_reference_without_weight_hit_changes'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def sources():
    return {p.relative_to(ROOT).as_posix(): sha(p.read_bytes())
            for directory in ('rouge', 'tests', 'scripts')
            for p in sorted((ROOT / directory).rglob('*'))
            if p.is_file() and p.suffix in ('.py', '.json') and '__pycache__' not in p.parts}


def method_delta(old, new):
    a, b = ast.parse(old), ast.parse(new)
    def methods(tree, count):
        found = [n for n in ast.walk(tree)
                 if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')]
        assert len(found) == len({n.name for n in found}) == count
        return {n.name: n for n in found}
    am, bm = methods(a, 11), methods(b, 12)
    assert set(bm) - set(am) == {ADDED_METHOD} and set(am) - set(bm) == set()
    unchanged = set(am) - {CHANGED_METHOD}
    assert len(unchanged) == 10
    old_lines, new_lines = old.splitlines(keepends=True), new.splitlines(keepends=True)
    for name in unchanged:
        assert ast.dump(am[name], include_attributes=False) == ast.dump(bm[name], include_attributes=False)
        assert old_lines[am[name].lineno - 1:am[name].end_lineno] == new_lines[bm[name].lineno - 1:bm[name].end_lineno]
    assert ast.dump(am[CHANGED_METHOD], include_attributes=False) != ast.dump(bm[CHANGED_METHOD], include_attributes=False)
    def assertion_calls(node):
        return Counter(ast.dump(n, include_attributes=False) for n in ast.walk(node)
                       if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                       and isinstance(n.func.value, ast.Name) and n.func.value.id == 'self'
                       and n.func.attr.startswith('assert'))
    assert assertion_calls(am[CHANGED_METHOD]) == assertion_calls(bm[CHANGED_METHOD])
    assert sum(assertion_calls(am[CHANGED_METHOD]).values()) == 4
    for tree, remove in ((a, {id(am[CHANGED_METHOD])}),
                         (b, {id(bm[CHANGED_METHOD]), id(bm[ADDED_METHOD])})):
        removed = 0
        for node in ast.walk(tree):
            for field, value in ast.iter_fields(node):
                if isinstance(value, list):
                    kept = [item for item in value if id(item) not in remove]
                    removed += len(value) - len(kept)
                    setattr(node, field, kept)
        assert removed == len(remove)
    assert ast.dump(a, include_attributes=False) == ast.dump(b, include_attributes=False)
    return {'old_methods': 11, 'new_methods': 12, 'unchanged_old_methods': sorted(unchanged),
            'changed_old_method': CHANGED_METHOD, 'added_method': ADDED_METHOD,
            'all_four_old_assertion_calls_AST_preserved': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--correction-packet', required=True)
    parser.add_argument('--new-independent-review', required=True)
    args = parser.parse_args()
    target = BASE / 'resume107-applied-source-v2.json'
    assert not target.exists(), 'Do not overwrite any actual guard'
    assert subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip() == 'codex/p2-development'
    guard_path = BASE / 'resume107-applied-source-v1.json'
    guard_raw = guard_path.read_bytes()
    assert sha(guard_raw) == OLD_GUARD_SHA
    old = json.loads(guard_raw)
    assert old['section'] == 107 and old['source_count'] == len(old['source_sha256']) == 750
    assert sources() == old['source_sha256'] and old['source_sha256'][TEST] == OLD_TEST_SHA
    assert set(old['source_additional_sha256']) == {'CORE_0.70_VERIFICATION.json'}
    core_path = ROOT / 'CORE_0.70_VERIFICATION.json'
    core_raw = core_path.read_bytes()
    assert sha(core_raw) == old['source_additional_sha256']['CORE_0.70_VERIFICATION.json']
    cp_raw = (ROOT / 'DEVELOPMENT_CHECKPOINT.json').read_bytes()
    cp = json.loads(cp_raw)
    assert cp['completed_sections'] == 106 and cp['next_section'] == 107
    assert cp['full_validation_due'] is False and cp['next_full_validation_after'] == 110
    assert cp['current_batch_commit_policy']['next_full_validation_after'] == 110
    assert cp['last_full_validation'] == cp['current_full105_checkpoint']
    assert cp['last_full_validation']['after_section'] == 105
    assert cp['last_full_validation']['batch_validation_closed'] is True
    assert cp['last_full_validation']['available_checks_passed'] is True
    assert cp['last_full_validation']['full095_deferred_preserved'] is True
    publication_raw = (BASE / 'section106-publication-v1.json').read_bytes()
    assert sha(publication_raw) == PUBLICATION_SHA
    publication = json.loads(publication_raw)
    assert publication['local_HEAD'] == publication['remote_HEAD'] == old['baseline_HEAD']
    assert publication['clean'] is True and publication['commit_primary_exit'] == publication['push_primary_exit'] == 0
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() == publication['local_HEAD']
    failed_path = BASE / 'resume107-related-linux-v1.json'
    failed_raw = failed_path.read_bytes()
    assert sha(failed_raw) == FAILED_LINUX_SHA
    assert (BASE / 'resume107-related-linux-v1.exit-code').read_bytes() == b'1\n'
    failed = json.loads(failed_raw)
    assert failed['available_checks_passed'] is False and failed['tests_run'] == 222 and failed['tests_passed'] == 219
    assert failed['failures'] == 1 and failed['errors'] == 0 and failed['skipped'] == 1 and failed['unavailable_parent_count'] == 1
    assert failed['source_sha256'] == failed['source_after'] == old['source_sha256'] and failed['source_drift'] == []
    assert failed['source_additional_sha256'] == failed['source_additional_after'] == old['source_additional_sha256']
    diag_path = BASE / 'root-section107-empty-diagnostic-v1.json'
    diag_raw = diag_path.read_bytes()
    assert sha(diag_raw) == DIAGNOSIS_SHA and (BASE / 'root-section107-empty-diagnostic-v1.exit-code').read_bytes() == b'0\n'
    diagnosis = json.loads(diag_raw)
    assert diagnosis['kind'] == 'ROOT_ACTUAL_107_EMPTY_BOUNDARY_DIAGNOSIS' and len(diagnosis['rows']) == 12
    assert diagnosis['Source_750_CORE_unchanged'] is diagnosis['new_test_failure_preserved'] is True
    assert diagnosis['product_modified'] is False
    packet = Path(args.correction_packet).resolve()
    review_path = Path(args.new_independent_review).resolve()
    assert ROOT not in packet.parents and packet != ROOT and ROOT not in review_path.parents
    manifest_raw = (packet / 'SOURCE_MANIFEST.json').read_bytes()
    assert sha(manifest_raw) == NEW_MF_SHA
    manifest = json.loads(manifest_raw)
    assert manifest['STOPWRITE'] is True and manifest['Runtime_executed'] is manifest['product_pass'] is False
    assert set(manifest['files']) == {'AUTHOR_SOURCE_CHECK.json', 'README.md', 'exact-local-transport.json', 'local-test.diff', Path(TEST).name}
    assert {p.name for p in packet.iterdir() if p.is_file()} == set(manifest['files']) | {'SOURCE_MANIFEST.json'}
    for name, pin in manifest['files'].items():
        raw = (packet / name).read_bytes()
        assert len(raw) == pin['bytes'] and sha(raw) == pin['sha256']
    new_raw = (packet / Path(TEST).name).read_bytes()
    transport_raw = (packet / 'exact-local-transport.json').read_bytes()
    review_raw = review_path.read_bytes()
    assert sha(new_raw) == NEW_TEST_SHA and sha(transport_raw) == TRANSPORT_SHA and sha(review_raw) == NEW_REVIEW_SHA
    review = json.loads(review_raw)
    assert review['status'] == 'NO_SOURCE_BLOCKER_RUNTIME_PENDING' and review['Source_only'] is True
    assert review['runtime_pass'] is False and review['issues'] == []
    assert review['packet_manifest']['sha256'] == NEW_MF_SHA and review['candidate_test']['sha256'] == NEW_TEST_SHA
    transport = json.loads(transport_raw)
    assert transport['STOPWRITE'] is True and transport['Runtime_executed'] is transport['product_pass'] is False
    assert len(transport['replacements']) == 1
    change = transport['replacements'][0]
    assert change['path'] == TEST and change['before_sha256'] == OLD_TEST_SHA and change['after_sha256'] == NEW_TEST_SHA
    assert change['before_bytes'] == 13845 and change['after_bytes'] == 15991 and change['exact_occurrences'] == 1
    current = (ROOT / TEST).read_bytes()
    before, after = change['before'].encode(), change['after'].encode()
    assert len(current) == 13845 and sha(current) == OLD_TEST_SHA and current.count(before) == 1
    composed = current.replace(before, after, 1)
    assert composed == new_raw and composed.count(after) == 1 and composed.replace(after, before, 1) == current
    delta = method_delta(current, new_raw)
    compile(new_raw, TEST, 'exec')
    assert sources() == old['source_sha256'] and guard_path.read_bytes() == guard_raw and core_path.read_bytes() == core_raw
    assert (ROOT / 'DEVELOPMENT_CHECKPOINT.json').read_bytes() == cp_raw
    # The only tracked write, after every frozen-source and actual-evidence gate.
    (ROOT / TEST).write_bytes(composed)
    after_sources = sources()
    assert set(after_sources) == set(old['source_sha256']) and len(after_sources) == 750
    assert {name for name in after_sources if after_sources[name] != old['source_sha256'][name]} == {TEST}
    assert after_sources[TEST] == NEW_TEST_SHA and (ROOT / TEST).read_bytes() == new_raw
    assert guard_path.read_bytes() == guard_raw and core_path.read_bytes() == core_raw
    assert (ROOT / 'DEVELOPMENT_CHECKPOINT.json').read_bytes() == cp_raw
    final = deepcopy(old)
    final.update(status='ACTUALLY_REPAIRED_TEST_CONTRACT_RUNTIME_PENDING', source_sha256=after_sources,
        test_source_sha256=NEW_TEST_SHA, runtime_checks_passed_claimed=False,
        test_repaired_at_Beijing=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
        test_repair_prior_guard_sha256=sha(guard_raw), test_repair_original_test_sha256=OLD_TEST_SHA,
        test_repair_candidate_source_sha256=sha(new_raw), test_repair_candidate_manifest_sha256=sha(manifest_raw),
        test_repair_exact_transport_sha256=sha(transport_raw), test_repair_independent_source_review_sha256=sha(review_raw),
        test_repair_applier_source_sha256=sha(Path(__file__).read_bytes()),
        preserved_failed_Linux_receipt_sha256=sha(failed_raw), preserved_actual_empty_diagnosis_sha256=sha(diag_raw),
        test_repair_method_delta=delta, only_test_changed_from_prior_applied_guard=True,
        window_source_sha256_semantics='Historical actual healthy Gold runner; fresh candidate metadata/compatibility must be bound separately.',
        test_repair_scope='New regression-test contract correction from actual legacy boundary evidence. Only test changes, 11 to12 methods; no timing/product/registry modification.')
    with target.open('x', encoding='utf-8') as handle:
        json.dump(final, handle, ensure_ascii=False, indent=2)
        handle.write('\n')
    print(json.dumps({'guard': str(target), 'source_count': 750, 'only_changed_path': TEST,
                      'test_methods': 12, 'runtime_pass_claimed': False}))


if __name__ == '__main__':
    main()
