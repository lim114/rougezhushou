"""Root explicit final305 declaration after functional necessary/native success."""
import argparse
import ast
import json
from pathlib import Path

from full305_common import BASE, ROOT, FREEZE, git, native, public, runner_snapshot, native_source_snapshot, sha, tool_pins, write_new, input_bindings, now


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


def native_selected_names(relative, section, prepared):
    script = public(relative); raw = script.read_bytes()
    namespace = {'__file__': str(script), '__name__': '_305_declared_selected_input_api_only'}
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
        names = set(source_map(record, 'source_sha256_before'))
    names.add(relative)
    text = raw.decode('utf8')
    return names, {'accepts_visible_ms': '--visible-ms' in text, 'visible_ms': 60000,
                   'source_name_origin': 'bound_files API' if callable(namespace.get('bound_files')) else 'old actual source-name scope; all bytes fresh305'}


def public_manifest_closure(names):
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
                if sha(selected) != expected: raise ValueError('Explicit manifest authority drift: ' + relative)
                if isinstance(value, dict) and 'bytes' in value and selected.stat().st_size != value['bytes']:
                    raise ValueError('Manifest source size drift: ' + relative)
                if relative not in names: names.add(relative); queue.append(relative)
    return names


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--declare-final305-full-inputs', action='store_true')
    for name in ('expected-parent-commit', 'section305-native', 'necessary-receipt', 'window-receipt', 'window-process-receipt'):
        parser.add_argument('--' + name, required=True)
    args = parser.parse_args()
    if not args.declare_final305_full_inputs: raise ValueError('Root explicit declaration required; no implicit freeze.')
    native(); tool_pins()
    if git('branch', '--show-current') != 'codex/p2-development' or git('rev-parse', 'HEAD') != args.expected_parent_commit:
        raise ValueError('Actual current305 parent/branch changed.')
    if FREEZE.exists(): raise FileExistsError('Never overwrite declared input freeze; use a reviewed new attempt.')
    prepared = json.loads((BASE / 'prepared-inputs.json').read_bytes())
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
    scripts = dict(prepared['p3_scripts'])
    if not args.section305_native.startswith('scripts/') or not args.section305_native.endswith('_305.py'):
        raise ValueError('Canonical public305 native script required.')
    scripts['p3_305'] = args.section305_native
    if len(scripts) != 20: raise ValueError('All original five and all subsequent native ranges through305 must be explicit.')
    supplemental = set(old['supplemental_public_inputs_sha256'])
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
    archive = json.loads(public('verification/full-290/legacy-retry-attempt4/archive-manifest.json').read_bytes())
    by_hash = {}
    for name, value in archive['files'].items():
        by_hash.setdefault(value['sha256'], []).append('verification/full-290/legacy-retry-attempt4/' + name)
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
    supplemental = public_manifest_closure(supplemental)
    supplement_map = {name: sha(public(name)) for name in sorted(supplemental)}
    record = {'section': 305, 'root_declared': True, 'declared_at': now(), 'parent_commit': args.expected_parent_commit,
              **actual, 'supplemental_public_inputs_sha256': supplement_map,
              'legacy_native_source_sha256': native_sources, 'legacy_external_additional_sha256': legacy_extra,
              'local_public_input_bindings': bindings, 'local_public_input_sha256': locals_before,
              'p3_scripts': scripts, 'p3_script_options': script_options, 'p3_script_selected_paths': script_selected,
              'template_bundle_sha256': prepared['template_bundle_sha256'], 'functional_validation': refs,
              'preparation_ready_sha256': sha(BASE / 'CONTROLLER_READY.json'),
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
