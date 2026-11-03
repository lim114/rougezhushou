"""Append a SOURCE PLAN095 seal; stdlib only, no project imports or execution.

--seal writes only three new external JSON receipts and refuses existing outputs.
--verify reads the completed seal. Neither mode runs the collector or any runner.
Manifest hashes original six files, this sealer and diagnostic; handoff hashes
that manifest. The handoff's own digest is reported outside this hash chain.
"""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path('/workspace/rougezhushou')
OUT = Path(__file__).resolve().parent
BASE91 = '59961ec3d633ac91b01014fb06b357d45e5979f7'
OLD090_SHA = '9f7f2d192496f01a4e542cdbbfc1be9932381a6373eb3b46c8fefb2a965e62d9'
FROZEN = {
    'MIGRATION_PLAN.md': (8560, '54cb186d036cceb0d1f92e3169df36bc18b5cbae8e3cc51b19d51b93500d4081'),
    'collect_source_plan.py': (11094, '53697f55c68f1ce0fbfbffba4609e80417dea2a76ab1f9b19b0b409e8aea7cd2'),
    'legacy-calculation-and-saved089-dependencies.json': (10163, '9c1f2d60eab5490f503b1b05fda474ade1f711fdd2b0e420d1cb7b3f667aa133'),
    'original-runner-and-source-index.json': (6959, '313911a5d3967bb143c27d22aaad10fe4cef70b9acfd95d24562ba6359a0808f'),
    'read-preparation-diagnostics.json': (954, 'e4fc3e11131673a255f9236908c3a144825ade05dc8b6cb069003e0a4f4dce33'),
    'visibility-single-predicate-inverse-proof.json': (4840, 'ba53a798645287e5208694b2604c8e4a755cadcfe7f747f7f619f54abe2cd6e6'),
}
DIAG = 'sealing-fault-boundaries-source-plan095.json'
MANIFEST = 'public-artifacts-manifest-source-plan095.json'
HANDOFF = 'final-handoff-source-plan095.json'
GENERATED = (DIAG, MANIFEST, HANDOFF)
STATUS = 'SEALED_SOURCE_PLAN_ONLY_NOT_FULL095_VALIDATION'


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def git(*args):
    return subprocess.check_output(['git', '--no-optional-locks', '-C', str(ROOT), *args])


def schema(value):
    if isinstance(value, dict):
        return {key: schema(item) for key, item in value.items()}
    if isinstance(value, list):
        return {'type': 'array', 'length': len(value), 'item_schema': schema(value[0]) if value else None}
    return type(value).__name__


def descriptor(name):
    path = OUT / name
    require(path.is_file() and not path.is_symlink(), 'Missing/non-regular source artifact: ' + name)
    raw = path.read_bytes()
    row = {'path': str(path), 'name': name, 'bytes': len(raw), 'sha256': sha(raw)}
    if path.suffix == '.json':
        value = json.loads(raw)
        row['json_schema'] = schema(value)
    else:
        row['media_type'] = 'text/markdown' if path.suffix == '.md' else 'text/x-python'
    return row


def write_new(name, value):
    raw = (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + chr(10)).encode('utf-8')
    with (OUT / name).open('xb') as stream:
        stream.write(raw)


def verify_frozen_sources():
    records = []
    for name, (size, digest) in FROZEN.items():
        row = descriptor(name)
        require((row['bytes'], row['sha256']) == (size, digest), 'Frozen original changed: ' + name)
        records.append(row)
    index = json.loads((OUT / 'original-runner-and-source-index.json').read_bytes())
    require(index['source_baseline91'] == BASE91, 'Wrong saved source baseline')
    source = {}
    for row in index['read_only_repository_inputs']:
        raw = git('show', BASE91 + ':' + row['repository_path'])
        require((len(raw), sha(raw)) == (row['bytes'], row['sha256']), 'Pinned repository source changed: ' + row['repository_path'])
        require(git('rev-parse', BASE91 + ':' + row['repository_path']).decode().strip() == row['git_blob'], 'Pinned git blob mismatch')
        source[row['repository_path']] = raw
    for row in index['read_only_external_inputs']:
        raw = Path(row['source_path']).read_bytes()
        require((len(raw), sha(raw)) == (row['bytes'], row['sha256']), 'Historical external source mismatch: ' + row['source_path'])
    proof = json.loads((OUT / 'visibility-single-predicate-inverse-proof.json').read_bytes())
    raw = source['verification/full-090/wine-ui-runner.py']
    require(len(raw) == 729181 and sha(raw) == OLD090_SHA, 'Wrong full090 runner')
    require(raw == Path(index['read_only_external_inputs'][0]['source_path']).read_bytes(), 'Final-gate runner differs')
    text = raw.decode('utf-8')
    require(text.count(proof['before']) == 1, 'Visibility predicate not unique')
    preview = text.replace(proof['before'], proof['after'])
    require(sha(preview.encode()) == proof['preview_sha256'] and preview.replace(proof['after'], proof['before']).encode() == raw, 'Saved single-predicate inverse mismatch')
    require("levels'][requested090['skill_rank']-1]" in text.splitlines()[3009], 'Requested rank source mismatch')
    tree = ast.parse(text)
    assignments = {target.id: node for node in ast.walk(tree) if isinstance(node, ast.Assign) for target in node.targets if isinstance(target, ast.Name)}
    rows = ast.literal_eval(assignments['rows090'].value)
    catalog = json.loads(source['rouge/data/catalog.json'])
    section88 = []
    for row in rows:
        if row['section'] != 88:
            continue
        scenario = row['input']
        sp = catalog['operators'][scenario['operator']]['skills'][scenario['skill']-1]['levels'][scenario['skill_rank']-1]['sp_type']
        section88.append({'historical_pair_id': row['pair_id'], 'operator': scenario['operator'], 'skill': scenario['skill'], 'rank': scenario['skill_rank'], 'checked': row['widget_checked'], 'sp_type': sp, 'legacy_expected_visible': sp == 'INCREASE_WHEN_ATTACK', 'section91_expected_visible': sp in ('INCREASE_WHEN_ATTACK', 'INCREASE_WITH_TIME')})
    require(section88 == proof['old_full090_section88_rows'] and sum(r['legacy_expected_visible'] != r['section91_expected_visible'] for r in section88) == 6, 'Section88 saved source proof mismatch')
    legacy = json.loads((OUT / 'legacy-calculation-and-saved089-dependencies.json').read_bytes())
    states = ast.literal_eval(assignments['saved89_states090'].value)
    contracts = ast.literal_eval(assignments['expected89_contract090'].value.generators[0].iter)
    require(len(states) == 5 and len(contracts) == 10 and len(rows) == legacy['legacy_52_request_rows'] == 52, 'Saved089/legacy row count mismatch')
    require(list(states[0]) == legacy['saved089_run_states']['keys'] and list(contracts[0]) == legacy['saved089_expected_consumer_contract']['keys'], 'Saved089 record schema mismatch')
    require(sorted({k for row in states for k in row['state']['operators']}) == legacy['saved089_run_states']['only_roster_owners'] == ['char_151_myrtle', 'mechanist'], 'Saved089 owners mismatch')
    lines = text.splitlines()
    for key, first, last in [('projection',1014,1020), ('same_call_text_native',3015,3033), ('saved089_actions',3083,3092), ('saved089_native_guards',3101,3127), ('old_deepcolor_fixed_rates',2030,2038)]:
        require(chr(10).join(lines[first-1:last]) == legacy['excerpts'][key], 'Saved source excerpt mismatch: ' + key)
    return records, {'repository_inputs_verified': len(source), 'external_inputs_verified': len(index['read_only_external_inputs']), 'full090_runner_bytes': len(raw), 'full090_runner_sha256': OLD090_SHA, 'single_predicate_source_inverse_verified': True, 'section88_rows': 8, 'visibility_changed_natural_rows': 6, 'visibility_unchanged_mechanist_rows': 2, 'saved089_states': 5, 'saved089_consumer_rows': 10, 'saved089_contains_damage_golden': False, 'numeric_projection_excludes_notes_report': True, 'same_current_formatter_native_guards_are_not_old_text_goldens': True}


def main():
    require(sys.argv[1:] in (['--seal'], ['--verify']), 'Use --seal or --verify')
    records, checks = verify_frozen_sources()
    if sys.argv[1] == '--verify':
        manifest = json.loads((OUT / MANIFEST).read_bytes())
        require(manifest['status'] == STATUS and manifest['original_frozen_files'] == records, 'Manifest original seal mismatch')
        for row in manifest['sealed_payload_files']:
            require(descriptor(row['name']) == row, 'Sealed payload mismatch: ' + row['name'])
        handoff = json.loads((OUT / HANDOFF).read_bytes())
        require(handoff['manifest'] == descriptor(MANIFEST) and handoff['status'] == STATUS and handoff['section095_completed'] is False, 'Handoff seal mismatch')
        print(json.dumps({'status': STATUS, 'read_only_seal_verified': True, 'handoff': descriptor(HANDOFF)}, ensure_ascii=False))
        return
    require(not any((OUT / name).exists() for name in GENERATED), 'Existing/partial seal; never overwrite or treat it as completed')
    observed_head = git('rev-parse', 'HEAD').decode().strip()
    branch = git('branch', '--show-current').decode().strip()
    require(branch == 'codex/p2-development', 'Unexpected active branch')
    diag = {'schema_version': 1, 'status': STATUS, 'original_directory_file_count_before_resume': 6, 'previous_interrupted_seal_files_were_absent': ['seal_plan.py', MANIFEST, HANDOFF], 'original_preparation_diagnostics': descriptor('read-preparation-diagnostics.json'), 'observed_source_checks': checks, 'observed_root_head_at_seal': observed_head, 'observed_root_branch_at_seal': branch, 'pinned_source_baseline91': BASE91, 'original_six_files_unchanged': True, 'project_imports_API_helpers_formatter_tests_Qt_Wine_network': 0, 'project_product_attempts': 0, 'root_tracked_mutations_by_this_task': 0, 'historical_runner_or_archive_copies': 0, 'collector_executions_on_resume': 0, 'boundary_checks_not_fault_injected': ['Frozen original digest mismatch stops sealing', 'Pinned git/external digest or saved proof mismatch stops sealing', 'Any existing generated receipt stops sealing; partial output is never a completed handoff', 'No migration/runtime/root review success follows from source checks'], 'qualification': {'91_notes_and_92_window_length': 'Qualified report/text deltas; preserve numerical projection and same-current native guards', 'saved089': 'Five public RunState observations and ten training/label/crew/roster contracts; current update_operator computes using actual current code', 'render_existing_result': 'render_damage and report-bearing format_estimate only format an existing report; cannot add 91/92 fields to old results', '4217_4283_and_730': 'Historical records/guard provenance, no claim all values/text/source unchanged', 'full095_runtime': 'Pending actual committed 91-95 head, migration and source inverse; full startup/control/explicit/render/restore call ledger', '93_94_and_final95_counts': 'Unknown; not prevalidated'}, 'failure_scope': 'Previous interruption and broad/truncated source reads are preparation failures, not product failures', 'runtime_status': 'NOT_RUN', 'code_migration_status': 'NOT_IMPLEMENTED', 'root_review_status': 'PENDING'}
    write_new(DIAG, diag)
    payload = records + [descriptor('seal_plan.py'), descriptor(DIAG)]
    manifest = {'schema_version': 1, 'status': STATUS, 'scope': 'External source-plan freeze; not a full095 runner or validation receipt', 'pinned_source_baseline91': BASE91, 'original_frozen_files': records, 'sealed_payload_files': payload, 'payload_file_count': len(payload), 'hash_chain': 'Payload -> manifest -> final handoff; manifest and handoff do not self-hash; final handoff digest is supplied out of band', 'excluded_archives': 'No 729181-byte runner copy or full090 archive copy', 'section095_completed': False, 'runtime_status': 'NOT_RUN', 'code_migration_status': 'NOT_IMPLEMENTED', 'root_review_status': 'PENDING'}
    write_new(MANIFEST, manifest)
    handoff = {'schema_version': 1, 'status': STATUS, 'path': str(OUT / HANDOFF), 'manifest': descriptor(MANIFEST), 'source_plan': descriptor('MIGRATION_PLAN.md'), 'source_sealer': descriptor('seal_plan.py'), 'sealing_diagnostics': descriptor(DIAG), 'original_frozen_file_count': 6, 'sealed_payload_file_count': len(payload), 'total_directory_files_after_seal': 10, 'source_plan_seal_completed': True, 'section095_completed': False, 'runtime_status': 'NOT_RUN', 'code_migration_status': 'NOT_IMPLEMENTED', 'root_review_status': 'PENDING', 'next_required': ['Root reviews this source-only plan', 'After 91-95 committed source is final, bind actual source count, exact migrated runner deltas and full source inverse', 'Measure full startup/control/explicit/render/restore runtime call ledger on current code; execute real regressions and window validation'], 'stop_writing_after_handoff': True}
    write_new(HANDOFF, handoff)
    require(records == [descriptor(name) for name in FROZEN], 'Original six files changed during sealing')
    print(json.dumps({'status': STATUS, 'manifest': descriptor(MANIFEST), 'handoff': descriptor(HANDOFF), 'section095_completed': False}, ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, RuntimeError, subprocess.CalledProcessError) as error:
        print(json.dumps({'status': 'SOURCE_SEAL_FAILED_NOT_FULL095_VALIDATION', 'error': str(error)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
