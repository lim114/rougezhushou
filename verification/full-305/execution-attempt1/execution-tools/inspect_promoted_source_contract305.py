"""Additional read-only public source API inspection; does not alter READY."""
import json
from full305_common import BASE, ROOT, public, sha, write_new, runner_snapshot, native_source_snapshot, input_bindings
from declare_freeze305 import native_selected_names, public_manifest_closure


def main():
    prepared = json.loads((BASE / 'prepared-inputs-final.json').read_bytes())
    scripts = {**prepared['p3_scripts'], 'p3_305': 'scripts/verify_relic_exchange_flow_window_305.py'}
    old = json.loads(public('verification/full-290/source-freeze-final-A3.json').read_bytes())
    selected = set(old['supplemental_public_inputs_sha256']); rows = {}; errors = []
    for key, name in sorted(scripts.items(), key=lambda pair: int(pair[0].split('_')[1])):
        try:
            names, options = native_selected_names(name, int(key.split('_')[1]), prepared)
            selected.update(names); rows[key] = {'script': name, 'script_sha256': sha(public(name)), 'selected_count': len(names), **options}
        except (KeyError, ValueError, OSError) as error:
            errors.append({'component': key, 'type': type(error).__name__, 'message': str(error)})
    binding_path = 'verification/sections/303-preparation/historical-source-inputs/local-public-bindings.json'
    bindings = json.loads(public(binding_path).read_bytes())['bindings']
    selected.add(binding_path); selected.update(row['public_path'] for row in bindings)
    local = input_bindings(bindings)
    guard = json.loads((BASE / 'template-legacy/current-source-guard.json').read_bytes())
    selected.update(name for name in guard['source_additional_sha256'] if not name.startswith('.cache/'))
    try: expanded, historical = public_manifest_closure(selected)
    except (KeyError, ValueError, OSError) as error:
        expanded = set(); historical = []; errors.append({'component': 'public_manifest_closure', 'type': type(error).__name__, 'message': str(error)})
    actual = runner_snapshot(); native = native_source_snapshot(); common = set(actual['source_sha256']) & set(native)
    if (any(actual['source_sha256'][name] != native[name] for name in common)
            or set(actual['source_sha256']) - common != {'CORE_0.70_VERIFICATION.json'}
            or set(native) - common != {'tests/offline_scope_retirement.py'}):
        errors.append({'component': 'maintained_native_relationship', 'message': 'Original full/native CORE/helper relationship changed.'})
    value = {'section': 305, 'kind': 'POST_PROMOTION_READ_ONLY_INPUT_API_PREFLIGHT_NO_FREEZE_OR_TEST',
        'controller_ready_sha256': sha(BASE / 'CONTROLLER_READY.json'), 'rows': rows,
        'actual_maintained_selector_count': len(actual['selectors']), 'current_source_files': len(actual['source_sha256']),
        'public_supplement_closure_count_before_explicit_legacy_local_counterparts': len(expanded),
        'historical_manifest_bindings': historical, 'actual048_local_public_pairs_verified': len(local),
        'errors': errors, 'final305_native_source_can_still_change_before_root_freeze': True,
        'tests_Qt_windows_sourcefreeze_activation_or_Git_started': False}
    write_new(BASE / 'promoted-source-contract-preflight.json', value)
    print(json.dumps({'components': len(rows), 'selectors': len(actual['selectors']), 'current_sources': len(actual['source_sha256']),
                      'public_closure': len(expanded), 'local_public_pairs': len(local), 'errors': errors,
                      'tests_Qt_or_freeze_started': False}, ensure_ascii=False))
    return 1 if errors else 0


if __name__ == '__main__': raise SystemExit(main())
