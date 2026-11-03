"""Independent source-only byte and saved36 review; no package imports/API calls."""
import ast
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent
AUTHOR = OUT.with_name('p2-remaining-boolean-consumers-086-source')
ROOT = Path('/workspace/rougezhushou')
BASE = 'b5a40f30683bfc0945decaabbd4db5914c28427f'
canon = lambda v: json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)
sha = lambda data: hashlib.sha256(data).hexdigest()
manifest_bytes = (AUTHOR / 'archivable-public-manifest.json').read_bytes()
assert sha(manifest_bytes) == '43fb5c6cfd2806cca065c734bbc0e30e20dc2a447ff0a2ade5d45baa71647de8'
manifest = json.loads(manifest_bytes)
assert manifest['count'] == len(manifest['files']) == 28
for proof in manifest['files']:
    data = Path(proof['source_path']).read_bytes()
    assert sha(data) == proof['sha256'] and len(data) == proof['bytes']
    assert proof['archive_path'] == str(Path(proof['source_path']).relative_to(AUTHOR))
assert sha((AUTHOR / 'source-handoff.json').read_bytes()) == 'babbe184f0c7d69f546d257c780f6e059aaf463576338e1f7530a69920749a5f'
freeze = json.loads((AUTHOR / 'baseline-git-object-freeze.json').read_bytes())
assert freeze['base_commit'] == BASE and len(freeze['files']) == 125
specs = [BASE + ':' + r['path'] for r in freeze['files']]
batch = subprocess.run(['git', 'cat-file', '--batch'], cwd=ROOT,
    input=('\n'.join(specs) + '\n').encode(), capture_output=True, check=True).stdout
offset = 0
for proof in freeze['files']:
    end = batch.index(b'\n', offset); header = batch[offset:end].split()
    assert header[1] == b'blob' and header[0].decode() == proof['git_blob']
    length = int(header[2]); raw = batch[end + 1:end + 1 + length]; offset = end + 2 + length
    assert raw == (AUTHOR / 'baseline' / proof['path']).read_bytes()
    assert sha(raw) == proof['sha256'] and len(raw) == proof['bytes']
assert offset == len(batch)
excerpts = json.loads((AUTHOR / 'frozen-source-excerpt-byte-proof.json').read_bytes())
for proof in excerpts['files']:
    original = subprocess.check_output(['git', 'show', BASE + ':' + proof['git_path']], cwd=ROOT)
    data = (AUTHOR / 'source-excerpts' / proof['git_path']).read_bytes()
    assert original == data and sha(data) == proof['sha256'] and len(data) == proof['bytes']
assert len(excerpts['files']) == 8
tables = {}
for proof in json.loads((AUTHOR / 'original-source-hash-receipt.json').read_bytes()):
    data = Path(proof['source_path']).read_bytes()
    assert sha(data) == proof['sha256'] and len(data) == proof['bytes']
    assert proof['source_commit'] == 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'
    tables[proof['table']] = json.loads(data)
assert len(tables) == 4
closure = json.loads((AUTHOR / 'original-eight-owner-closure.json').read_bytes())
catalog = json.loads((AUTHOR / 'baseline/rouge/data/catalog.json').read_bytes())['operators']
ranks = modules = named = hidden = 0
sp_fields = {'spType': 'sp_type', 'spCost': 'sp_cost', 'initSp': 'initial_sp', 'increment': 'sp_increment', 'maxChargeTime': 'max_charges'}
for owner_id, proof in closure['operators'].items():
    raw = tables['character_table'][owner_id]; local = catalog[owner_id]
    assert proof['name'] == raw['name'] == local['name']
    assert proof['original_trait_description'] == raw['description']
    assert proof['original_trait'] == raw.get('trait') == local['trait']
    assert len(raw['skills']) == len(local['skills']) == len(proof['skills']) == 3
    for number, (binding, current, captured) in enumerate(zip(raw['skills'], local['skills'], proof['skills'], strict=True), 1):
        assert captured['number'] == number and captured['character_binding'] == binding
        assert captured['skill_id'] == binding['skillId'] == current['id']
        assert current['unlock_elite'] == int(binding['unlockCond']['phase'][-1])
        levels = tables['skill_table'][binding['skillId']]['levels']
        assert levels == captured['original_levels'] and len(levels) == len(current['levels']) == 10
        for original, projected in zip(levels, current['levels'], strict=True):
            assert {b['key']: b['value'] for b in original['blackboard']} == projected['values']
            assert original['description'] == projected['description'] and original['duration'] == projected['duration']
            assert original['durationType'] == projected['duration_type']
            for source_key, local_key in sp_fields.items():
                assert original['spData'][source_key] == projected[local_key], (owner_id, number, source_key)
            ranks += 1
    assert len(raw['talents']) == len(local['talents']) == len(proof['talents'])
    for index, (group, candidates, captured) in enumerate(zip(raw['talents'], local['talents'], proof['talents'], strict=True)):
        assert captured['talent_index'] == index and captured['original_group'] == group
        originals = [t for t in group.get('candidates') or [] if t['name']]
        assert len(originals) == len(candidates) == captured['catalog_named_candidate_count']
        hidden += sum(not t['name'] for t in group.get('candidates') or [])
        for original, current in zip(originals, candidates, strict=True):
            assert original['name'] == current['name'] and original['description'] == current['description']
            assert {b['key']: b['value'] for b in original['blackboard']} == current['values']
            assert int(original['unlockCondition']['phase'][-1]) == current['phase']
            assert original['unlockCondition']['level'] == current['level'] and original['requiredPotentialRank'] == current['potential_rank']
            named += 1
    assert len(local['modules']) == len(proof['module_binding_parts'])
    for current, captured in zip(local['modules'], proof['module_binding_parts'], strict=True):
        meta = tables['uniequip_table']['equipDict'][current['id']]
        phases = tables['battle_equip_table'][current['id']]['phases']
        assert captured['module_id'] == current['id'] and captured['identity'] == meta
        assert meta['charId'] == owner_id and meta['tmplId'] is None
        assert int(meta['unlockEvolvePhase'][-1]) == current['unlock_elite'] and meta['unlockLevel'] == current['unlock_level']
        assert captured['original_parts_per_level'] == [p['parts'] for p in phases]
        assert len(phases) == len(current['levels']) == 3
        assert all(r['parts'] == l['parts'] for r, l in zip(phases, current['levels'], strict=True))
        modules += 1
assert ranks == 240 and modules == 12 and len(closure['operators']) == 8
plan = json.loads((AUTHOR / 'source-first-public-probe-plan.json').read_bytes())['scenarios']
fields = {k for row in plan for k in row if k not in ('operator', 'skill', 'skill_rank', 'elite', 'base_attack', 'timing_mode')}
assert len(fields) == 12
ast_saved = json.loads((AUTHOR / 'frozen-public-consumer-ast.json').read_bytes())['consumers']
rebuilt = []
for name in ('rouge/operator_engine.py', 'rouge/reporting.py', 'rouge/estimate.py', 'rouge/damage.py', 'rouge/run_modifiers.py'):
    text = (AUTHOR / 'source-excerpts' / name).read_text(); tree = ast.parse(text); parents = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node): parents[child] = node
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'get'
                and node.args and isinstance(node.args[0], ast.Constant) and node.args[0].value in fields): continue
        chain = []; parent = node
        while parent in parents:
            parent = parents[parent]
            if isinstance(parent, (ast.FunctionDef, ast.If)):
                chain.append({'kind': type(parent).__name__, 'line': parent.lineno,
                    'name_or_test': parent.name if isinstance(parent, ast.FunctionDef) else ast.unparse(parent.test)})
        rebuilt.append({'path': name, 'field': node.args[0].value, 'line': node.lineno, 'expression': ast.unparse(node),
            'parent_chain': chain, 'source_line': text.splitlines()[node.lineno - 1]})
assert rebuilt == ast_saved and len(rebuilt) == 17
options_tree = ast.parse((AUTHOR / 'source-excerpts/rouge/operator_options.py').read_text())
options = ast.literal_eval(next(n.value for n in options_tree.body if isinstance(n, ast.Assign)
    and any(isinstance(t, ast.Name) and t.id == 'OPTIONS' for t in n.targets)))
qt = json.loads((AUTHOR / 'actual-qt-producer-static-closure.json').read_bytes())
actual_options = []
for owner, rows in options.items():
    for key, label, default, maximum, skills in rows:
        if key in fields:
            assert type(default) is bool
            actual_options.append({'owner': owner, 'field': key, 'label': label, 'default': default, 'maximum': maximum,
                'skills': skills, 'producer_value_type': 'bool'})
assert canon(actual_options) == canon(qt['options'])
app_lines = (AUTHOR / 'source-excerpts/rouge/app.py').read_text().splitlines()
for proof in qt['construction_lines'] + qt['scenario_lines']:
    assert app_lines[proof['line'] - 1] == proof['text']

def decode(tree):
    tag = tree['type']
    if tag == 'dict':
        assert set(tree) == {'type', 'items'}
        pairs = [(decode(k), decode(v)) for k, v in tree['items']]
        assert len({k for k, v in pairs}) == len(pairs)
        return dict(pairs)
    if tag in ('list', 'tuple'):
        assert set(tree) == {'type', 'items'}
        values = [decode(v) for v in tree['items']]
        return tuple(values) if tag == 'tuple' else values
    assert set(tree) == {'type', 'value'}
    expected = {'NoneType': type(None), 'bool': bool, 'int': int, 'float': float, 'str': str}[tag]
    assert type(tree['value']) is expected, (tag, type(tree['value']).__name__)
    return tree['value']

rows = [json.loads(line) for line in (AUTHOR / 'first-public-probes.jsonl').read_text().splitlines()]
summary = json.loads((AUTHOR / 'first-public-probe-summary.json').read_bytes())
assert len(rows) == len(plan) == 36 and len(summary['groups']) == 12
for index, (row, scenario) in enumerate(zip(rows, plan, strict=True), 1):
    assert row['index'] == index and canon(row['input']) == canon(scenario)
    assert row['outcome'] == 'accepted' and row['input_unchanged'] is row['catalog_unchanged'] is True
    assert canon(row['input_typed_before']) == canon(row['input_typed_after'])
    assert canon(decode(row['input_typed_before'])) == canon(scenario)
    assert canon(decode(row['result_typed'])) == canon(row['result'])
    assert set(row['reports']) == {'estimate', 'user', 'technical'}
    assert all(type(text) is str and text for text in row['reports'].values())
groups = []
for index in range(12):
    a, b, c = rows[index * 3:index * 3 + 3]
    flag = next(k for k in a['input'] if k in fields)
    assert type(a['input'][flag]) is bool and a['input'][flag] is False
    assert type(b['input'][flag]) is bool and b['input'][flag] is True
    assert type(c['input'][flag]) is str and c['input'][flag] == 'false'
    assert canon(a['result_typed']) != canon(b['result_typed'])
    assert canon(b['result_typed']) == canon(c['result_typed']) and canon(b['result']) == canon(c['result'])
    assert canon(b['reports']) == canon(c['reports'])
    proof = summary['groups'][index]
    assert proof['field'] == flag and proof['operator'] == a['input']['operator'] and proof['skill'] == a['input']['skill']
    assert proof['bool_values_differ'] and proof['text_false_exactly_equals_true'] and proof['text_false_reports_exactly_equal_true']
    groups.append({'operator': a['input']['operator'], 'field': flag, 'skill': a['input']['skill'],
        'false_true_whole_native_tree_different': True, 'text_false_true_native_JSON_three_texts_identical': True})
receipt = {'status': 'PASS_SOURCE_AND_SAVED_ONLY', 'base_commit': BASE, 'authors_frozen_manifest_28_exact': True,
    'frozen_git_blob_files_verified': 125, 'core_source_excerpts_git_bytes_verified': 8,
    'original_tables_full_byte_hashes_rechecked': 4, 'raw_owner_closures': 8, 'raw_skill_ranks': ranks,
    'blackboard_description_duration_durationType_all_five_SP_fields_exact': True,
    'raw_module_identity_parts_bindings': modules, 'original_hidden_candidates_preserved_count': hidden,
    'catalog_named_candidate_bindings': named, 'no102_module_semantic_audit_repeated': True,
    'exact_AST_get_sites': 17, 'flag_count': 12, 'actual_Qt_producer_static_only_verified': True,
    'saved_36_inputs_native_tree_result_binding_and_three_reports_recompared': True, 'groups': groups,
    'first_source_probe_calls_repeated': 0, 'new_calculate_damage_calls': 0, 'new_helper_calls': 0,
    'tests_GUI_Wine_product_draft_tracked_changes': False,
    'scope': 'Only qualified E2 no-module frame scenarios with False/True/text false; broader qualification, normal/module impact, nontext aliases and old-error priority remain later product-validation work.',
    'unknown_native_clock_attachment_hidden_scripts_inferred': False}
(OUT / 'source-saved-review086.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k: v for k, v in receipt.items() if k != 'groups'}, ensure_ascii=False))
