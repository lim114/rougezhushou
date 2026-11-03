"""Root explicit source binding only; never starts the prepared Windows fixture."""
import argparse
import ast
import json
import re
from pathlib import Path
from full335_common import BASE, ROOT, FREEZE, validate_freeze, sha, write_new


def bytes_json(value): return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf8')


def assert_ast(raw):
    tree = ast.parse(raw.decode('utf8'))
    return [ast.dump(node, include_attributes=False) for node in sorted((node for node in ast.walk(tree) if isinstance(node, ast.Assert)), key=lambda node: (node.lineno, node.col_offset))]


def replace_assignment(raw, name, value):
    replacement = (name + ' = ' + repr(value)).encode('ascii')
    result, count = re.subn(rb'(?m)^' + name.encode('ascii') + rb'\s*=\s*[^\r\n]+', lambda match: replacement, raw)
    if count != 1: raise ValueError('Unique binding literal required: ' + name)
    return result


def preservation(original, adapted, literals):
    before = ast.parse(original); after = ast.parse(adapted)
    for tree in (before, after):
        for node in tree.body:
            if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and node.targets[0].id in literals:
                node.value = ast.Constant(value=None)
    if ast.dump(before, include_attributes=False) != ast.dump(after, include_attributes=False):
        raise ValueError('Scope/observer/generator or any non-binding AST changed.')
    if assert_ast(original) != assert_ast(adapted): raise ValueError('Original assertions/order changed.')
    return {'all_nonbinding_AST_identical': True, 'assert_AST_count': len(assert_ast(original)), 'binding_names': sorted(literals)}


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--activate', action='store_true')
    parser.add_argument('--expected-parent-commit', required=True); parser.add_argument('--freeze-sha256', required=True)
    args = parser.parse_args()
    if not args.activate: raise ValueError('Root explicit activation required.')
    data = validate_freeze(args.expected_parent_commit, args.freeze_sha256)
    master_path = BASE / 'activation335.json'
    if master_path.exists(): raise FileExistsError('Never overwrite an activated bundle.')
    master = {'section': 335, 'status': 'CURRENT335_SOURCE_BOUND_NOT_EXECUTED', 'root_freeze_sha256': args.freeze_sha256,
              'tested_worktree_parent_commit': args.expected_parent_commit, 'bundles': {}, 'actual_pass_claimed': False,
              'preservation': {}}
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
                         actual_section=335, actual335_execution_authority_not_old_raw_label=True)
            contents['current-source-guard.json'] = bytes_json(guard)
            from hashlib import sha256
            guard_sha = sha256(contents['current-source-guard.json']).hexdigest()
            window = replace_assignment(contents['window.py'], '_SOURCE125_GUARD_SHA256', guard_sha)
            window = replace_assignment(window, '_SOURCE125_MAINTAINED_COUNT', len(data['legacy_native_source_sha256']))
            proof = preservation(contents['window.py'], window, {'_SOURCE125_GUARD_SHA256', '_SOURCE125_MAINTAINED_COUNT'})
            from hashlib import sha256
            text = window.decode('utf8'); tree = ast.parse(text)
            main_try = [node for node in tree.body if isinstance(node, ast.Try)
                        and sum(isinstance(item, ast.Assert) for item in ast.walk(node)) == 552]
            if len(main_try) != 1 or sha256(ast.get_source_segment(text, main_try[0]).encode('utf8')).hexdigest() != '11da3f02423dc96598480c85c31f3c8ba4672f6f4cd232741579ff45a7f87922':
                raise ValueError('Original552 physical main body changed.')
            proof.update(original552_physical_body_unchanged=True, original862_assertions=proof['assert_AST_count'] == 862)
            master['preservation']['legacy'] = proof
            contents['window.py'] = window
            contents['launcher125.py'] = replace_assignment(contents['launcher125.py'], 'WINDOW_SHA256', sha256(window).hexdigest())
            contents['launcher125.py'] = replace_assignment(contents['launcher125.py'], 'SOURCE125_GUARD_SHA256', guard_sha)
            old_activation = b"HERE/'activation-final-A3.json'"
            old_status = b"'CURRENT290_FINAL_A3_BOUND_NOT_EXECUTED'"
        else:
            contents['source-freeze.json'] = FREEZE.read_bytes()
            for name in ('window.py', 'window29.py'):
                window = replace_assignment(contents[name], 'FREEZE_SHA256', args.freeze_sha256)
                master['preservation'][name] = preservation(contents[name], window, {'FREEZE_SHA256'})
                contents[name] = window
            old_activation = b"HERE/'activation275.json'"; old_status = b"'CURRENT290_SOURCE_BOUND_NOT_EXECUTED'"
        launcher = contents['launcher275.py']
        if launcher.count(old_activation) != 1 or launcher.count(old_status) != 1:
            raise ValueError('Unique original outer activation metadata required.')
        contents['launcher275.py'] = launcher.replace(old_activation, b"HERE/'activation335.json'").replace(old_status, b"'CURRENT335_SOURCE_BOUND_NOT_EXECUTED'")
        from hashlib import sha256
        tools = {name: sha256(raw).hexdigest() for name, raw in contents.items()}
        for name, raw in contents.items():
            target = bound / name; target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('xb') as stream: stream.write(raw)
        activation = {'section': 335, 'actual_section': 335, 'status': 'CURRENT335_SOURCE_BOUND_NOT_EXECUTED',
                      'binding_ready': True, 'runtime_executed': False, 'actual_pass_claimed': False,
                      'allowed_modes': ['legacy'] if mode == 'legacy' else ['current30', 'current29'],
                      'tested_worktree_parent_commit': args.expected_parent_commit,
                      'root_freeze_relative': FREEZE.relative_to(ROOT).as_posix(), 'root_freeze_sha256': args.freeze_sha256,
                      'execution_tools_sha256': tools, 'scope_not_reduced': True,
                      'historical_raw_labels_preserved_not_current_authority': True}
        write_new(bound / 'activation335.json', activation)
        master['bundles'][mode] = {'execution_tools_sha256': tools, 'activation_sha256': sha(bound / 'activation335.json')}
    validate_freeze(args.expected_parent_commit, args.freeze_sha256)
    write_new(master_path, master)
    print(json.dumps({'activation': str(master_path), 'sha256': sha(master_path), 'tests_or_Qt_windows_started': False}))


if __name__ == '__main__': main()
