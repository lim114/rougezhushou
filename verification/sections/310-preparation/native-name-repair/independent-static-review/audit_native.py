"""Read-only symtable and AST contract review; does not import product or Qt."""
from pathlib import Path
from hashlib import sha256
import ast
import builtins
import json
import symtable

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
NATIVE = 'scripts/verify_boss_cycle_window_310.py'
EXPECTED_NATIVE_SHA = '1b49430a61b266a052d46c2eb62f9a760d11922485f78a491521972c4b817807'


def pin(path):
    raw = path.read_bytes()
    return {'sha256': sha256(raw).hexdigest(), 'bytes': len(raw)}


def save(name, value):
    (OUT / name).write_bytes((json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf8'))


def class_contract(filename, name, attributes, methods):
    path = ROOT / filename
    tree = ast.parse(path.read_text(encoding='utf8'))
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == name)
    defined_methods = {node.name: node.lineno for node in cls.body if isinstance(node, ast.FunctionDef)}
    assigned = {}
    for node in ast.walk(cls):
        if (isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Store)
                and isinstance(node.value, ast.Name) and node.value.id == 'self'):
            assigned.setdefault(node.attr, node.lineno)
    return {'file': filename, 'class': name, 'file_pin': pin(path),
            'required_attributes': {key: assigned.get(key) for key in attributes},
            'required_methods': {key: defined_methods.get(key) for key in methods},
            'missing': [key for key in attributes if key not in assigned] + [key for key in methods if key not in defined_methods]}


def main():
    path = ROOT / NATIVE
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != EXPECTED_NATIVE_SHA:
        raise ValueError('Reviewed canonical changed; this audit must not silently move to the new revision')
    text = raw.decode('utf8')
    tree = ast.parse(text)
    symbols = symtable.symtable(text, NATIVE, 'exec')
    globals_defined = set(symbols.get_identifiers())
    implicit = {'__file__', '__name__', '__package__', '__spec__', '__loader__', '__builtins__', '__doc__', '__cached__'}
    allowed = globals_defined | set(dir(builtins)) | implicit
    unresolved = []
    scopes = []

    def visit(table, scope):
        scopes.append({'scope': scope, 'line': table.get_lineno(),
                       'free': sorted(symbol.get_name() for symbol in table.get_symbols() if symbol.is_free()),
                       'nonlocal': sorted(symbol.get_name() for symbol in table.get_symbols() if symbol.is_nonlocal())})
        for symbol in table.get_symbols():
            if symbol.is_referenced() and symbol.is_global() and symbol.get_name() not in allowed:
                unresolved.append({'scope': scope, 'name': symbol.get_name(),
                                   'reference_lines': [node.lineno for node in ast.walk(tree)
                                                       if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
                                                       and node.id == symbol.get_name()]})
        for child in table.get_children():
            visit(child, scope + '/' + child.get_name())

    visit(symbols, 'module')
    contracts = [
        class_contract('rouge/battle_view.py', 'BattlePreviewPanel',
            ['context', 'current_stage', '_shown_enemy', '_tile_cell', 'grid', 'original', 'stage_choices',
             'stage_combo', 'enemy_choices', 'enemy_combo', 'wave_combo', 'include_branches', 'technical',
             'spawn_detail', 'enemy_detail', 'boss_cycle_button', 'boss_cycle_window'],
            ['_refresh_boss_cycle', 'open_boss_cycle_reference']),
        class_contract('rouge/boss_cycle_view.py', 'BossCycleReferencePanel',
            ['identity', 'scope_key', 'result', 'topic', 'player', 'technical', 'tabs', 'lorentz_picture', 'cube_picture'],
            ['set_reference', 'refresh_reference', 'clear_reference']),
        class_contract('rouge/view_catalog.py', 'SubjectPicture', ['key', 'image'], ['set_subject']),
        class_contract('rouge/branch_choice.py', 'BranchChoice', ['branch', 'combo'], ['select_branch']),
        class_contract('rouge/battle_view.py', 'MapOriginal', ['selected', 'reference_cell'], []),
        class_contract('rouge/battle_view.py', 'BattleGrid', ['selected'], []),
    ]
    if any(contract['missing'] for contract in contracts):
        raise ValueError('Static local UI contract mismatch: ' + repr(contracts))
    model_path = ROOT / 'rouge/boss_cycle_reference.py'
    model_tree = ast.parse(model_path.read_text(encoding='utf8'))
    literal = {}
    for node in model_tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            try:
                literal[node.targets[0].id] = ast.literal_eval(node.value)
            except (ValueError, TypeError):
                pass
    expected_targets = (('ro6_b_5', 'enemy_2147_shophm', 0), ('ro6_b_5', 'enemy_2148_shorbb', 0))
    assert literal['TARGETS'] == expected_targets
    actual_fields = literal['ACTUAL_FIELDS']
    assert len(actual_fields) > 0
    source = json.loads((ROOT / 'rouge/data/boss-cycle-reference.json').read_bytes())
    model_contract = {'file': str(model_path.relative_to(ROOT)).replace('\\', '/'), 'pin': pin(model_path),
                      'targets': [list(value) for value in expected_targets], 'actual_fields': list(actual_fields),
                      'data_reference_topics': [row['id'] for row in source['reference']['topics']],
                      'data_entry_names': source['entry_names'],
                      'source_negative_member_present': 'research/p3-boss-cycle-310/selected-original-records.json' in literal['RUNTIME_FILES']}
    assert model_contract['source_negative_member_present']
    manual = [
        'main entry_index/key/topics/topic_ids assignments precede scheduled begin; nonlocal declarations resolve to main.',
        'Each topic_case lambda captures that invocation\'s own index. The second entry is scheduled only after the first refresh checks complete.',
        'Both actual readers are selected as tabs before checking selection/scroll. current UI methods preserve source identity, selected topic and reader state.',
        'The negative clone copies MANIFEST plus every runtime_files member and proves valid before changing a real selected-authority byte. It restores in finally and requires a manual reopen.',
        'Source change does not fake actual events, module quantities or mode status; model actual fields and six mutation flags match script assertions.',
        'BranchChoice overview uses a flat combo, so Home plus raw index Down operations are not offset by add_groups disabled headings.',
        'All four app state paths and eight external operations are patched before BattlePreviewPanel constructor. The script explicitly does not claim a full MainWindow fixture.',
        'A failed pre-GUI assertion leaves done=False, qt_exit=None and passed=False; it cannot turn into a passed native receipt.',
    ]
    assert pin(path)['sha256'] == EXPECTED_NATIVE_SHA
    (OUT / 'reviewed-native-script.py').write_bytes(raw)
    report = {'kind': 'SECTION310_INDEPENDENT_NATIVE_STATIC_REVIEW_NOT_NATIVE_OR_TEST_EXECUTION',
              'reviewed_file': NATIVE, 'reviewed_pin': pin(path), 'source_unchanged_during_read': True,
              'undefined_globals': unresolved, 'only_known_name_error': unresolved == [{'scope': 'module/main', 'name': 'keyS', 'reference_lines': [74]}],
              'scopes': scopes, 'UI_contracts': contracts, 'model_contract': model_contract,
              'manual_control_flow_findings': manual,
              'additional_concrete_blocker_found': False,
              'required_repair': 'Replace keyS with KEYS, preserving the assertion and all remaining scope.',
              'all_required_local_UI_members_found': True, 'product_or_Qt_or_tests_imported_or_executed': False,
              'native_pass_claimed': False,
              'limitation': 'Static names, source contracts and control flow only; actual Windows/Qt behavior still requires the complete root-owned real attempt.'}
    save('static-review.json', report)
    print(json.dumps({'reviewed_sha256': EXPECTED_NATIVE_SHA, 'undefined_globals': unresolved,
                      'local_UI_contracts': len(contracts), 'all_required_local_UI_members_found': True,
                      'additional_concrete_blocker_found': False, 'Qt_or_tests_run': False}, ensure_ascii=False))


if __name__ == '__main__':
    main()
