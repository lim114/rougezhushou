"""Root explicit source binding only; never starts the prepared Windows fixture."""
import argparse
import ast
import json
import re
from pathlib import Path
from full305_common import BASE, ROOT, FREEZE, validate_freeze, sha, write_new


def bytes_json(value): return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf8')


def assert_ast(raw):
    tree = ast.parse(raw.decode('utf8'))
    return [ast.dump(node, include_attributes=False) for node in sorted((node for node in ast.walk(tree) if isinstance(node, ast.Assert)), key=lambda node: (node.lineno, node.col_offset))]


def replace_assignment(raw, name, value):
    replacement = (name + ' = ' + repr(value)).encode('ascii')
    result, count = re.subn(rb'(?m)^' + name.encode('ascii') + rb'\s*=\s*[^\r\n]+', lambda match: replacement, raw)
    if count != 1: raise ValueError('Unique binding literal required: ' + name)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--activate', action='store_true')
    parser.add_argument('--expected-parent-commit', required=True); parser.add_argument('--freeze-sha256', required=True)
    args = parser.parse_args()
    if not args.activate: raise ValueError('Root explicit activation required.')
    data = validate_freeze(args.expected_parent_commit, args.freeze_sha256)
    master_path = BASE / 'activation305.json'
    if master_path.exists(): raise FileExistsError('Never overwrite an activated bundle.')
    master = {'section': 305, 'status': 'CURRENT305_SOURCE_BOUND_NOT_EXECUTED', 'root_freeze_sha256': args.freeze_sha256,
              'tested_worktree_parent_commit': args.expected_parent_commit, 'bundles': {}, 'actual_pass_claimed': False}
    for mode in ('legacy', 'current'):
        template = BASE / ('template-' + mode); bound = BASE / ('bound-' + mode)
        if bound.exists(): raise FileExistsError('Never overwrite a bound or executed capsule.')
        bound.mkdir()
        contents = {name: (template / name).read_bytes() for name in data['template_bundle_sha256'][mode]}
        if mode == 'legacy':
            guard = json.loads(contents['current-source-guard.json'])
            additional = {**data['legacy_external_additional_sha256'], **data['supplemental_public_inputs_sha256'],
                          'CORE_0.70_VERIFICATION.json': data['source_sha256']['CORE_0.70_VERIFICATION.json']}
            guard.update(source_sha256=data['legacy_native_source_sha256'], source_additional_sha256=additional,
                         root_freeze_sha256=args.freeze_sha256, tested_worktree_parent_commit=args.expected_parent_commit,
                         actual_section=305, actual305_execution_authority_not_old_raw_label=True)
            contents['current-source-guard.json'] = bytes_json(guard)
            from hashlib import sha256
            guard_sha = sha256(contents['current-source-guard.json']).hexdigest()
            window = replace_assignment(contents['window.py'], '_SOURCE125_GUARD_SHA256', guard_sha)
            window = replace_assignment(window, '_SOURCE125_MAINTAINED_COUNT', len(data['legacy_native_source_sha256']))
            if assert_ast(window) != assert_ast(contents['window.py']): raise ValueError('Original862 assertion AST/order changed.')
            contents['window.py'] = window
            contents['launcher125.py'] = replace_assignment(contents['launcher125.py'], 'WINDOW_SHA256', sha256(window).hexdigest())
            contents['launcher125.py'] = replace_assignment(contents['launcher125.py'], 'SOURCE125_GUARD_SHA256', guard_sha)
            old_activation = b"HERE/'activation-final-A3.json'"
            old_status = b"'CURRENT290_FINAL_A3_BOUND_NOT_EXECUTED'"
        else:
            contents['source-freeze.json'] = FREEZE.read_bytes()
            for name in ('window.py', 'window29.py'):
                window = replace_assignment(contents[name], 'FREEZE_SHA256', args.freeze_sha256)
                if assert_ast(window) != assert_ast(contents[name]): raise ValueError('Original current30/29 assertions changed.')
                contents[name] = window
            old_activation = b"HERE/'activation275.json'"; old_status = b"'CURRENT290_SOURCE_BOUND_NOT_EXECUTED'"
        launcher = contents['launcher275.py']
        if launcher.count(old_activation) != 1 or launcher.count(old_status) != 1:
            raise ValueError('Unique original outer activation metadata required.')
        contents['launcher275.py'] = launcher.replace(old_activation, b"HERE/'activation305.json'").replace(old_status, b"'CURRENT305_SOURCE_BOUND_NOT_EXECUTED'")
        from hashlib import sha256
        tools = {name: sha256(raw).hexdigest() for name, raw in contents.items()}
        for name, raw in contents.items():
            target = bound / name; target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('xb') as stream: stream.write(raw)
        activation = {'section': 305, 'actual_section': 305, 'status': 'CURRENT305_SOURCE_BOUND_NOT_EXECUTED',
                      'binding_ready': True, 'runtime_executed': False, 'actual_pass_claimed': False,
                      'allowed_modes': ['legacy'] if mode == 'legacy' else ['current30', 'current29'],
                      'tested_worktree_parent_commit': args.expected_parent_commit,
                      'root_freeze_relative': FREEZE.relative_to(ROOT).as_posix(), 'root_freeze_sha256': args.freeze_sha256,
                      'execution_tools_sha256': tools, 'scope_not_reduced': True,
                      'historical_raw_labels_preserved_not_current_authority': True}
        write_new(bound / 'activation305.json', activation)
        master['bundles'][mode] = {'execution_tools_sha256': tools, 'activation_sha256': sha(bound / 'activation305.json')}
    validate_freeze(args.expected_parent_commit, args.freeze_sha256)
    write_new(master_path, master)
    print(json.dumps({'activation': str(master_path), 'sha256': sha(master_path), 'tests_or_Qt_windows_started': False}))


if __name__ == '__main__': main()
