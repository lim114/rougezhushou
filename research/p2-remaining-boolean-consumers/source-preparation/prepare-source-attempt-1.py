"""Read-only source closure for a later section; never changes tracked files."""
import ast
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path('/workspace/rougezhushou')
OUT = Path(__file__).resolve().parent
BASE = 'b5a40f30683bfc0945decaabbd4db5914c28427f'
GAME = 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'
OWNERS = {
    'char_4228_closur': [('reinforcement_blocks_target', 2)],
    'char_437_mizuki': [('enemy_below_half', 2)],
    'char_206_gnosis': [('frozen_at_skill_end', 3)],
    'char_4087_ines': [('ines_first_deployment', 3)],
    'char_4182_oblvns': [('ranged_attack', 2), ('organ_mode', 2), ('fever', 2)],
    'char_1048_orchd2': [('power_coating', 1), ('double_charge', 1)],
    'char_1041_angel2': [('steal_success', 2), ('delivery_coordinate', 3)],
    'char_1035_wisdel': [('overload', 2)],
}
FIELDS = {field for entries in OWNERS.values() for field, _ in entries}
RAW = {
    'character_table': (ROOT/'.cache/p2-s1-binding/character_table.json', '68e3a3b5ee0d407ce234afaa5867c6fda6379a6843c7d5317a7bbda4779f8697'),
    'skill_table': (ROOT/'.cache/p2-s1-binding/skill_table.json', '86f4aa64c785f39727edd06d6dd8a4f27f371c8e4ace5345ba0dc61dee1386ca'),
    'battle_equip_table': (Path('/workspace/.continuation/p2-after-070-source-audit/originals/battle_equip_table.json'), '006687f201a823abf31c6a1c57b2269099bd3ea375c2ec3ae5595cc98a1ec460'),
    'uniequip_table': (Path('/workspace/.continuation/p2-after-070-source-audit/originals/uniequip_table.json'), 'b508483cc87c03d8313f4dd8dfc1b9195bc50385a8dfec51d17e657cb26ffad9'),
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def save(name, value):
    path = OUT/name
    with path.open('x', encoding='utf-8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write('\n')


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args])


def bb(rows):
    return {row['key']: row['value'] for row in rows}


def main():
    assert git('branch', '--show-current').decode().strip() == 'codex/p2-development'
    assert git('rev-parse', BASE).decode().strip() == BASE
    frozen = OUT/'baseline'
    frozen.mkdir()
    entries = []
    names = git('ls-tree', '-r', '--name-only', BASE, 'rouge').decode().splitlines()
    for name in names:
        if not name.endswith(('.py', '.json')):
            continue
        data = git('show', BASE+':'+name)
        target = frozen/name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        entries.append({'path': name, 'git_blob': git('rev-parse', BASE+':'+name).decode().strip(),
                        'sha256': digest(data), 'bytes': len(data)})
    save('baseline-git-object-freeze.json', {'base_commit': BASE, 'files': entries,
         'tracked_mutations': False, 'source_of_bytes': 'git show fixed commit, never working tree',
         'baseline_tree_not_required_as_archive_duplicate': True})
    raw = {}; receipts = []
    for key, (path, expected) in RAW.items():
        data = path.read_bytes()
        assert digest(data) == expected, key
        raw[key] = json.loads(data)
        receipts.append({'table': key, 'source_path': str(path), 'bytes': len(data),
                         'sha256': expected, 'source_commit': GAME,
                         'new_download': False, 'ordinary_module_audit_repeated': False})
    save('original-source-hash-receipt.json', receipts)
    cat = json.loads((frozen/'rouge/data/catalog.json').read_bytes())['operators']
    source = {}; skills_checked = 0; module_bindings = 0
    for owner in OWNERS:
        char = raw['character_table'][owner]
        profile = cat[owner]
        assert char['name'] == profile['name']
        skill_rows = []
        for number, (binding, local_skill) in enumerate(zip(char['skills'], profile['skills']), 1):
            assert binding['skillId'] == local_skill['id']
            assert int(binding['unlockCond']['phase'][-1]) == local_skill['unlock_elite']
            levels = raw['skill_table'][binding['skillId']]['levels']
            assert len(levels) == len(local_skill['levels']) == 10
            for original, local in zip(levels, local_skill['levels']):
                assert bb(original['blackboard']) == local['values']
                assert original['description'] == local['description']
                assert original['duration'] == local['duration']
                skills_checked += 1
            skill_rows.append({'number': number, 'character_binding': binding,
                               'skill_id': binding['skillId'], 'original_levels': levels})
        assert len(char['skills']) == len(profile['skills']) == 3
        talent_rows = []
        assert len(char['talents']) == len(profile['talents'])
        for index, (group, local_group) in enumerate(zip(char['talents'], profile['talents'])):
            candidates = group.get('candidates') or []
            assert len(candidates) == len(local_group), (owner,index)
            for original, local in zip(candidates, local_group):
                assert original['name'] == local['name']
                assert bb(original['blackboard']) == local['values']
                assert int(original['unlockCondition']['phase'][-1]) == local['phase']
                assert original['unlockCondition']['level'] == local['level']
                assert original['requiredPotentialRank'] == local['potential_rank']
            talent_rows.append({'talent_index': index, 'original_group': group})
        modules = []
        for module in profile['modules']:
            identity = raw['uniequip_table']['equipDict'][module['id']]
            assert identity['charId'] == owner and identity['tmplId'] is None
            assert int(identity['unlockEvolvePhase'][-1]) == module['unlock_elite']
            assert identity['unlockLevel'] == module['unlock_level']
            original_phases = raw['battle_equip_table'][module['id']]['phases']
            assert len(original_phases) == len(module['levels']) == 3
            assert all(a['parts'] == b['parts'] for a,b in zip(original_phases,module['levels']))
            modules.append({'module_id': module['id'], 'identity': identity,
                            'original_parts_per_level': [p['parts'] for p in original_phases]})
            module_bindings += 1
        source[owner] = {'name': char['name'], 'original_trait_description': char['description'],
                         'original_trait': char.get('trait'), 'skills': skill_rows,
                         'talents': talent_rows, 'module_binding_parts': modules}
    save('original-eight-owner-closure.json', {'source_commit': GAME, 'base_commit': BASE,
         'operators': source, 'skill_levels_checked': skills_checked,
         'module_bindings_checked': module_bindings, 'new_module_semantic_audit': False,
         'native_attachment_or_clock_inference': False, 'public_calls': 0})
    options_text = (frozen/'rouge/operator_options.py').read_text()
    ns = {}; exec(compile(options_text, 'frozen operator_options.py', 'exec'), ns)
    option_rows = []
    for owner, entries in ns['OPTIONS'].items():
        for key,label,default,maximum,skills in entries:
            if key in FIELDS:
                assert owner in OWNERS and type(default) is bool
                option_rows.append({'owner': owner,'field':key,'label':label,'default':default,
                                   'maximum':maximum,'skills':skills,'producer_value_type':'bool'})
    assert {x['field'] for x in option_rows} == FIELDS
    app_lines = (frozen/'rouge/app.py').read_text().splitlines()
    save('actual-qt-producer-static-closure.json', {'base_commit': BASE, 'options': option_rows,
         'construction_lines': [{'line':i+1,'text':app_lines[i]} for i in range(660,678)],
         'scenario_lines': [{'line':i+1,'text':app_lines[i]} for i in range(1033,1038)],
         'runtime_gui_called':False,'native_validation':False,
         'conclusion':'bool defaults construct QCheckBox; same owner and selected skill serializes isChecked bool. Visibility is not API consumer qualification.'})
    consumers = []
    for name in ('rouge/operator_engine.py','rouge/reporting.py','rouge/estimate.py','rouge/damage.py','rouge/run_modifiers.py'):
        text = (frozen/name).read_text()
        tree = ast.parse(text)
        parents = {}
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):parents[child] = node
        for node in ast.walk(tree):
            if not isinstance(node,ast.Call) or not isinstance(node.func,ast.Attribute) or node.func.attr != 'get':continue
            if not node.args or not isinstance(node.args[0],ast.Constant) or node.args[0].value not in FIELDS:continue
            chain = []; ancestor = node
            while ancestor in parents:
                ancestor = parents[ancestor]
                if isinstance(ancestor,(ast.FunctionDef,ast.If)):
                    chain.append({'kind':type(ancestor).__name__,'line':ancestor.lineno,
                                  'name_or_test':ancestor.name if isinstance(ancestor,ast.FunctionDef) else ast.unparse(ancestor.test)})
            consumers.append({'path':name,'field':node.args[0].value,'line':node.lineno,
                              'expression':ast.unparse(node),'parent_chain':chain,
                              'source_line':text.splitlines()[node.lineno-1]})
    assert set(c['field'] for c in consumers) == FIELDS
    save('frozen-public-consumer-ast.json', {'base_commit':BASE,'consumers':consumers,
         'caution':'else branches require manual enclosing-branch review; no runtime call is established by AST alone'})
    plan=[]
    for owner, entries in OWNERS.items():
        for field,skill in entries:
            for value in (False,True,'false'):
                plan.append({'operator':owner,'skill':skill,'skill_rank':10,'elite':2,
                             'base_attack':1000,'timing_mode':'frames',field:value})
    assert len(plan) == 36
    save('source-first-public-probe-plan.json', {'base_commit':BASE,'maximum_calls':36,
         'scenarios':plan,'purpose':'first bounded demonstration of existing actual truthiness, no draft, no matrix',
         'next_probe_process_must_verify_source_closure':True})
    save('source-preparation-complete.json', {'passed':True,'base_commit':BASE,'owners':8,
         'fields':12,'source_skill_levels':skills_checked,'module_bindings':module_bindings,
         'git_frozen_files':len(entries) if False else len(json.loads((OUT/'baseline-git-object-freeze.json').read_bytes())['files']),
         'public_calls':0,'gui_calls':0,'wine_calls':0,'tracked_mutations':False})
    print(json.dumps({'passed':True,'skill_levels':skills_checked,'module_bindings':module_bindings,'public_calls':0}))


if __name__ == '__main__':main()
