"""Root explicit final305 declaration after functional necessary/native success."""
import argparse
import ast
import json
from pathlib import Path

from full305_common import BASE, ROOT, PYTHON, FREEZE, READY_PATH, git, native, public, runner_snapshot, native_source_snapshot, sha, tool_pins, write_new, input_bindings, now


def source_map(record, key):
    value = record[key]
    if type(value) is not dict or not value: raise ValueError('Nonempty actual source map required.')
    return {name: entry['sha256'] if isinstance(entry, dict) else entry for name, entry in value.items()}


def functional_receipts(necessary_name, window_name, process_name):
    necessary_path = public(necessary_name); window_path = public(window_name); process_path = public(process_name)
    necessary = json.loads(necessary_path.read_bytes()); window = json.loads(window_path.read_bytes()); process = json.loads(process_path.read_bytes())
    before = source_map(necessary, 'source_sha256_before'); after = source_map(necessary, 'source_sha256_after')
    if necessary.get('exit_code') != 0 or before != after:
        raise ValueError('Root final305 actual necessary0/source-stable receipt required.')
    for name, expected in after.items():
        if sha(public(name)) != expected: raise ValueError('Functional necessary source changed: ' + name)
    wb = source_map(window, 'source_sha256_before'); wa = source_map(window, 'source_sha256_after')
    if window.get('passed') is not True or wb != wa:
        raise ValueError('Root final305 actual successful source-stable native receipt required.')
    for name, expected in wa.items():
        if sha(public(name)) != expected: raise ValueError('Functional native source changed: ' + name)
    if (process.get('section') != 305 or process.get('exit_code') != 0 or process.get('child_primary_exit') != 0
            or process.get('timed_out') is not False or process.get('owned_job_no_live_execution_verified') is not True
            or process.get('window_receipt_sha256') != sha(window_path)):
        raise ValueError('Root actual305 owned native child/supervisor0/job-empty receipt required.')
    return {'necessary': {'path': necessary_name, 'sha256': sha(necessary_path)},
            'native': {'path': window_name, 'sha256': sha(window_path)},
            'native_process': {'path': process_name, 'sha256': sha(process_path)}}


def repaired_native296_receipts(window_name, process_name):
    """Require the separate actual regression before another complete full run."""
    script_name = 'scripts/verify_battle_entry_references_window_296_full305.py'
    script = public(script_name)
    if sha(script) != sha(BASE / 'candidate' / script_name):
        raise ValueError('The exact reviewed new296 canonical must be promoted first.')
    window_path = public(window_name); process_path = public(process_name)
    window = json.loads(window_path.read_bytes()); process = json.loads(process_path.read_bytes())
    before = source_map(window, 'source_sha256_before'); after = source_map(window, 'source_sha256_after')
    proof = json.loads((BASE / 'native296-reviewed-preparation/static-proof.json').read_bytes())
    if set(before) != set(proof['all_adapted_selected_sources']) or before != after:
        raise ValueError('Actual repaired296 must retain the complete reviewed selected closure, stable before/after.')
    if any(sha(public(name)) != expected for name, expected in after.items()):
        raise ValueError('Actual repaired296 selected source differs from current public bytes.')
    if (window.get('section') != 296 or window.get('kind') != 'isolated_native_windows_fixed_battle_entry_references'
            or window.get('passed') is not True or window.get('failure') is not None
            or window.get('qpa') != 'windows' or window.get('qt_exit_code') != 0
            or window.get('verification_window_closed') is not True
            or window.get('temporary_state_root') is not True
            or window.get('private_state_read_copied_or_restored') is not False
            or window.get('game_operated') is not False or window.get('game_captures') != 0
            or window.get('chat_sent') is not False or window.get('chat_attempted') is not False):
        raise ValueError('Actual isolated native repaired296 regression0 is required, not static proof or a prior PASS.')
    attempts = window.get('external_operation_attempts')
    if type(attempts) is not dict or not attempts or any(type(value) is not int or value != 0 for value in attempts.values()):
        raise ValueError('Repaired296 actual external-operation counters must all be zero.')
    pb = source_map(process, 'source_sha256_before'); pa = source_map(process, 'source_sha256_after')
    child = process.get('child_argv')
    if (process.get('section') not in (296, 305) or process.get('kind') != 'actual_native_window_owned_process_execution'
            or process.get('status') != 'completed' or process.get('exit_code') != 0
            or process.get('child_primary_exit') != 0 or process.get('timed_out') is not False
            or process.get('owned_job_no_live_execution_verified') is not True
            or process.get('owned_popen_retained') is not True
            or process.get('window_receipt_sha256') != sha(window_path)
            or pb != after or pa != after or type(child) is not list
            or child[:6] != [str(PYTHON), '-B', '-X', 'utf8', str(script), '--receipt']):
        raise ValueError('Actual repaired296 retained owned supervisor/child0/job-empty/source/argv receipt required.')
    return {'native296_regression': {'path': window_name, 'sha256': sha(window_path)},
            'native296_regression_process': {'path': process_name, 'sha256': sha(process_path)}}


def native_selected_names(relative, section, prepared):
    script = public(relative); raw = script.read_bytes()
    namespace = {'__file__': str(script), '__name__': '_305_declared_selected_input_api_only'}
    tree = ast.parse(raw)
    if any(isinstance(node, ast.FunctionDef) and node.name == 'bound_files' for node in tree.body):
        exec(compile(raw, str(script), 'exec'), namespace)
    if callable(namespace.get('bound_files')):
        values = namespace['bound_files']()
        names = set(values)
        if any(sha(public(name)) != expected for name, expected in values.items()):
            raise ValueError('Selected input API changed during collection: ' + relative)
    else:
        # Old286-290 producers declared their source maps only in actual main.
        # Preserve that exact prior source-name scope and fresh-hash current bytes;
        # the old PASS value is not reused by this input collection.
        prior = prepared['prior_p3_actual_receipts_for_scope_only'][str(section)]
        record = json.loads(public(prior).read_bytes())
        key = next(key for key in ('source_sha256_before', 'loaded_source_sha256', 'source_sha256') if key in record)
        names = set(source_map(record, key))
    names.add(relative)
    text = raw.decode('utf8')
    return names, {'accepts_visible_ms': '--visible-ms' in text, 'visible_ms': 60000,
                   'source_name_origin': 'bound_files API' if callable(namespace.get('bound_files')) else 'old actual source-name scope; all bytes fresh305'}


def public_manifest_closure(names):
    # This immutable manifest is intentionally replayed as rejected historical
    # authority by the299 compatibility tests; its two obsolete code guards
    # are evidence, not assertions that those old bytes are current production.
    old_manifest = 'research/p3-battle-event-references-296/source-manifest.json'
    historical = {name: 'verification/sections/298-preparation/before/' + name
                  for name in ('rouge/event_planning.py', 'rouge/node_catalog.py')}
    historical_bindings = []
    names = set(names); queue = list(names); seen = set()
    while queue:
        name = queue.pop()
        if name in seen: continue
        seen.add(name)
        path = public(name)
        if path.name not in ('source-manifest.json', 'source-artifacts.json', 'source-authority.json'): continue
        data = json.loads(path.read_bytes())
        for mapping_key in ('files', 'runtime_files', 'build_authority_files'):
            values = data.get(mapping_key)
            if not isinstance(values, dict): continue
            for member, value in values.items():
                if not isinstance(member, str): raise ValueError('Manifest member identity required.')
                expected = value.get('sha256') if isinstance(value, dict) else value if isinstance(value, str) else None
                if type(expected) is not str or len(expected) != 64: continue
                relative = member if member.split('/')[0] in ('rouge', 'tests', 'scripts', 'research', 'verification') else (Path(name).parent / member).as_posix()
                selected = public(relative)
                authority = selected
                if sha(selected) != expected:
                    if (name != old_manifest or sha(path) != 'c6a7d1294e48b6fec896f736d56baa0c09f25f3365de471cc11c88d74705de21'
                            or relative not in historical):
                        raise ValueError('Explicit manifest authority drift: ' + relative)
                    counterpart = historical[relative]; authority = public(counterpart)
                    if sha(authority) != expected: raise ValueError('Exact old296 historical input drift.')
                    historical_bindings.append({'manifest': name, 'member': relative,
                        'historical_public_path': counterpart, 'historical_sha256': expected,
                        'current_sha256': sha(selected), 'role': 'old rejected guard INPUT, never execute historical code'})
                    if counterpart not in names: names.add(counterpart); queue.append(counterpart)
                if isinstance(value, dict) and 'bytes' in value and authority.stat().st_size != value['bytes']:
                    raise ValueError('Manifest source size drift: ' + relative)
                if relative not in names: names.add(relative); queue.append(relative)
    return names, historical_bindings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--declare-final305-full-inputs', action='store_true')
    for name in ('expected-parent-commit', 'section305-native', 'necessary-receipt', 'window-receipt', 'window-process-receipt'):
        parser.add_argument('--' + name, required=True)
    parser.add_argument('--maintenance-receipt', required=True)
    parser.add_argument('--first-archive-sha256', required=True)
    parser.add_argument('--native296-receipt', required=True)
    parser.add_argument('--native296-process-receipt', required=True)
    args = parser.parse_args()
    if not args.declare_final305_full_inputs: raise ValueError('Root explicit declaration required; no implicit freeze.')
    native(); tool_pins()
    from attempt2_lineage import first_closed_archive
    lineage = first_closed_archive(args.first_archive_sha256)
    if git('branch', '--show-current') != 'codex/p2-development' or git('rev-parse', 'HEAD') != args.expected_parent_commit:
        raise ValueError('Actual current305 parent/branch changed.')
    if FREEZE.exists(): raise FileExistsError('Never overwrite declared input freeze; use a reviewed new attempt.')
    prepared = json.loads((BASE / 'prepared-inputs-final.json').read_bytes())
    actual = runner_snapshot()
    old = json.loads(public('verification/full-290/source-freeze-final-A3.json').read_bytes())
    if actual['selectors'][:len(old['selectors'])] != old['selectors']:
        raise ValueError('The complete original430 ordered prefix must be retained.')
    new_tests = sorted(name for name in actual['source_sha256'] if name.startswith('tests/test_') and name.endswith('.py') and name not in old['source_sha256'])
    if any('tests.' + Path(name).stem not in actual['selectors'] for name in new_tests):
        raise ValueError('Every new public test module through305 must be in actual maintained API.')
    native_sources = native_source_snapshot()
    common = set(native_sources) & set(actual['source_sha256'])
    if (any(native_sources[name] != actual['source_sha256'][name] for name in common)
            or set(actual['source_sha256']) - common != {'CORE_0.70_VERIFICATION.json'}
            or set(native_sources) - common != {'tests/offline_scope_retirement.py'}):
        raise ValueError('Original typed-auditor full/native source relationship changed; do not weaken it.')
    refs = functional_receipts(args.necessary_receipt, args.window_receipt, args.window_process_receipt)
    refs.update(repaired_native296_receipts(args.native296_receipt, args.native296_process_receipt))
    maintenance_path=public(args.maintenance_receipt);maintenance=json.loads(maintenance_path.read_bytes())
    maintenance_before=source_map(maintenance,'source_sha256_before');maintenance_after=source_map(maintenance,'source_sha256_after')
    if maintenance.get('exit_code')!=0 or maintenance_before!=maintenance_after or any(sha(public(name))!=value for name,value in maintenance_after.items()):
        raise ValueError('Root actual source-stable maintenance check0 required before new full input declaration.')
    refs['maintenance']={'path':args.maintenance_receipt,'sha256':sha(maintenance_path)}
    scripts = dict(prepared['p3_scripts'])
    if not args.section305_native.startswith('scripts/') or not args.section305_native.endswith('_305.py'):
        raise ValueError('Canonical public305 native script required.')
    scripts['p3_305'] = args.section305_native
    scripts = dict(sorted(scripts.items(), key=lambda pair: int(pair[0].split('_')[1])))
    if len(scripts) != 20: raise ValueError('All original five and all subsequent native ranges through305 must be explicit.')
    supplemental = set(old['supplemental_public_inputs_sha256'])
    supplemental.update(reference['path'] for key,reference in lineage.items() if isinstance(reference,dict) and 'path' in reference)
    script_options = {}; script_selected = {}
    for name, relative in scripts.items():
        if relative not in actual['source_sha256']: raise ValueError('Canonical native must be promoted before freeze: ' + relative)
        selected, options = native_selected_names(relative, int(name.split('_')[1]), prepared)
        script_selected[name] = sorted(selected); script_options[name] = options; supplemental.update(selected)
    bindings_path = 'verification/sections/303-preparation/historical-source-inputs/local-public-bindings.json'
    historical_bindings = json.loads(public(bindings_path).read_bytes())['bindings']
    supplemental.add(bindings_path)
    supplemental.update(row['public_path'] for row in historical_bindings)
    # Legacy originals keep their exact historical public dependency paths.
    # For local cache inputs record the public captured-byte counterpart and
    # verify BOTH paths, rather than claiming they read only public files.
    guard = json.loads((BASE / 'template-legacy/current-source-guard.json').read_bytes())
    by_hash = {}
    # Exact successful legacy tools plus the original A2 controller/preparation
    # sources captured there. Both manifests are immutable actual originals;
    # search scope is explicit, not arbitrary old history or a private scan.
    archive_refs = {
        'verification/full-290/legacy-retry-attempt4/archive-manifest.json': 'f307d8b47ea246c0983853b78b60cbd14246f68c0766b688d64cf242aaac5929',
        'verification/full-290/execution-attempt2/archive-manifest.json': '4c8b281bbaccc955636f95ef6d2ff461427c07107237e58ef732457adc0640aa'}
    for manifest_name, expected_sha in archive_refs.items():
        path = public(manifest_name)
        if sha(path) != expected_sha: raise ValueError('Exact290 captured public dependency manifest changed.')
        supplemental.add(manifest_name)
        archive = json.loads(path.read_bytes())
        for name, value in archive['files'].items():
            by_hash.setdefault(value['sha256'], []).append((Path(manifest_name).parent / name).as_posix())
    bindings = list(historical_bindings); legacy_extra = {}
    for name, old_sha in guard['source_additional_sha256'].items():
        if name.startswith('.cache/'):
            candidates = by_hash.get(old_sha, [])
            choices = [value for value in candidates if Path(value).name == Path(name).name]
            if not choices: raise ValueError('No exact public captured counterpart for original cache input: ' + name)
            selected = sorted(choices, key=lambda value: ('executed-legacy-bundle/' not in value, len(value), value))[0]
            counterpart = public(selected)
            row = {'local_path': name, 'public_path': selected, 'sha256': old_sha, 'bytes': counterpart.stat().st_size}
            bindings.append(row); supplemental.add(selected)
            legacy_extra[name] = old_sha
        else:
            supplemental.add(name); legacy_extra[name] = sha(public(name))
    deduplicated = {}
    for row in bindings:
        if row['local_path'] in deduplicated and deduplicated[row['local_path']] != row:
            raise ValueError('Conflicting local/public input mapping.')
        deduplicated[row['local_path']] = row
    bindings = list(deduplicated.values()); locals_before = input_bindings(bindings)
    supplemental, historical_manifest_bindings = public_manifest_closure(supplemental)
    supplement_map = {name: sha(public(name)) for name in sorted(supplemental)}
    record = {'section': 305, 'actual_validation_attempt': 2, 'first_attempt_lineage': lineage,
              'root_declared': True, 'declared_at': now(), 'parent_commit': args.expected_parent_commit,
              **actual, 'supplemental_public_inputs_sha256': supplement_map,
              'legacy_native_source_sha256': native_sources, 'legacy_external_additional_sha256': legacy_extra,
              'local_public_input_bindings': bindings, 'local_public_input_sha256': locals_before,
              'historical_manifest_bindings': historical_manifest_bindings,
              'p3_scripts': scripts, 'p3_script_options': script_options, 'p3_script_selected_paths': script_selected,
              'template_bundle_sha256': prepared['template_bundle_sha256'], 'functional_validation': refs,
              'preparation_ready_sha256': sha(READY_PATH),
              'original_typed_auditor_sha256': sha(BASE / 'template-legacy/audit_full261_saved_readback.py'),
              'Linux_WSL_Wine_or_original_private_Windows_verified': False,
              'future_execution_PASS_is_not_a_freeze_prerequisite': True,
              'prior290_results_are_lineage_not305_PASS': True}
    if runner_snapshot() != actual or input_bindings(bindings) != locals_before:
        raise ValueError('Declared inputs changed during root collection.')
    write_new(FREEZE, record)
    print(json.dumps({'source_freeze': str(FREEZE), 'sha256': sha(FREEZE),
                      'selectors': len(actual['selectors']), 'sources': len(actual['source_sha256']),
                      'supplemental_inputs': len(supplement_map), 'native_components': len(scripts),
                      'actual_tests_Qt_windows_or_activation_started': False}, ensure_ascii=False))


if __name__ == '__main__': main()
