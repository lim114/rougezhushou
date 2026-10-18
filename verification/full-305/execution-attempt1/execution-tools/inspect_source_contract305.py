"""Read selected source APIs/historical name scopes; no tests, Qt or freeze."""
import ast
import json
from pathlib import Path
from full305_common import BASE, ROOT, public, sha, write_new
from declare_freeze305 import native_selected_names, public_manifest_closure


def main():
    prepared = json.loads((BASE / 'prepared-inputs-final.json').read_bytes())
    scripts = {**prepared['p3_scripts'], 'p3_305': 'scripts/verify_relic_exchange_flow_window_305.py'}
    # The two reviewed full305 maintenance candidates are not promoted here.
    # Collect their code as canonical-identity input APIs, with __file__ set to
    # intended public path; actual declaration later only accepts promoted bytes.
    selected = set(); rows = {}; errors = []
    for key, name in sorted(scripts.items(), key=lambda pair: int(pair[0].split('_')[1])):
        try:
            candidate = BASE / 'candidate' / name
            path = candidate if candidate.exists() else public(name)
            raw = path.read_bytes(); tree = ast.parse(raw)
            top_imports = [node for node in tree.body if isinstance(node, (ast.Import, ast.ImportFrom))]
            if any('PySide' in ast.dump(node) for node in top_imports): raise ValueError('Qt import excluded from source-only preflight.')
            api = {'__file__': str(ROOT / name), '__name__': '_305_static_selected_input_scope_only'}
            if any(isinstance(node, ast.FunctionDef) and node.name == 'bound_files' for node in tree.body):
                exec(compile(raw, str(path), 'exec'), api)
                names = set(api['bound_files']())
            else:
                previous = prepared['prior_p3_actual_receipts_for_scope_only'][key.split('_')[1]]
                old = json.loads(public(previous).read_bytes())
                names = set(old.get('source_sha256_before', old.get('loaded_source_sha256', old.get('source_sha256', {}))))
            names.add(name)
            # An unpromoted reviewed maintenance candidate has canonical public
            # identity but no public file yet. All other source inputs must exist.
            for entry in names:
                if entry == name and candidate.exists(): continue
                public(entry)
            selected.update(names)
            rows[key] = {'canonical': name, 'source_names': sorted(names), 'names': len(names), 'script_sha256': sha(path),
                         'scope_only_no_previous_PASS_reused': True}
        except (KeyError, ValueError, OSError) as error:
            errors.append({'component': key, 'type': type(error).__name__, 'message': str(error)})
    unpromoted = {name for name in selected if (BASE / 'candidate' / name).is_file() and not (ROOT / name).is_file()}
    try:
        expanded, history = public_manifest_closure(selected - unpromoted)
    except (KeyError, ValueError, OSError) as error:
        expanded = set(); history = []; errors.append({'component': 'manifest_closure', 'type': type(error).__name__, 'message': str(error)})
    value = {'section': 305, 'kind': 'READ_ONLY_SELECTED_SOURCE_CONTRACT_PREFLIGHT_NOT_FREEZE_OR_TEST',
        'rows': rows, 'manifest_closure_source_count': len(expanded), 'historical_manifest_bindings': history, 'errors': errors,
        'unpromoted_reviewed_candidates': sorted(unpromoted), 'tests_Qt_windows_sourcefreeze_or_activation_started': False}
    write_new(BASE / 'selected-source-contract-preflight.json', value)
    print(json.dumps({'components': len(rows), 'source_closure': len(expanded), 'errors': errors, 'tests_Qt_started': False}, ensure_ascii=False))
    return 1 if errors else 0


if __name__ == '__main__': raise SystemExit(main())
