"""Read pinned git blobs and original data; never import project runtime."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path('/workspace/rougezhushou')
OUT = Path('/workspace/.continuation/p2-module-source-gap-082-alternate')
COMMIT = 'c950fbc800245f7f784d6070f7126890352ffcc9'
GAME_COMMIT = 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def write(name, value):
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

files = {}
for name in ('rouge/operator_engine.py', 'rouge/operator_options.py', 'rouge/reporting.py',
             'rouge/catalog.py', 'rouge/estimate.py', 'rouge/data/catalog.json',
             'PROJECT_PROGRESS.md', 'AGENTS.md'):
    raw = subprocess.check_output(['git', '-C', str(ROOT), 'show', COMMIT + ':' + name])
    path = OUT / 'fixed-current' / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    files[name] = {'commit': COMMIT, 'bytes': len(raw), 'sha256': sha(raw),
                   'git_blob': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', COMMIT + ':' + name]).decode().strip()}

originals = {}
for table, path, expected in (
    ('battle_equip_table', Path('/workspace/.continuation/p2-after-070-source-audit/originals/battle_equip_table.json'),
     '006687f201a823abf31c6a1c57b2269099bd3ea375c2ec3ae5595cc98a1ec460'),
    ('uniequip_table', Path('/workspace/.continuation/p2-after-070-source-audit/originals/uniequip_table.json'),
     'b508483cc87c03d8313f4dd8dfc1b9195bc50385a8dfec51d17e657cb26ffad9')):
    raw = path.read_bytes()
    assert sha(raw) == expected, (table, sha(raw))
    originals[table] = {'path': str(path), 'bytes': len(raw), 'sha256': sha(raw), 'game_commit': GAME_COMMIT}
    originals[table]['data'] = json.loads(raw)

catalog = json.loads((OUT / 'fixed-current/rouge/data/catalog.json').read_bytes())
engine = (OUT / 'fixed-current/rouge/operator_engine.py').read_text()
reporting = (OUT / 'fixed-current/rouge/reporting.py').read_text()
options = (OUT / 'fixed-current/rouge/operator_options.py').read_text()
for name in ('rouge/operator_engine.py', 'rouge/operator_options.py', 'rouge/reporting.py'):
    ast.parse((OUT / 'fixed-current' / name).read_text())

leads = []
for oid, module_id, needles, boundary, restart in (
    ('char_1041_angel2', 'uniequip_002_angel2',
     ('angel2_tr[e].hp_ratio', 'angel2_tr[e].sp_recovery_per_sec', '生命值高于80%'),
     'Original TRAIT states HP above80% and natural SP +0.25/s. Existing controls do not expose this module HP condition; generic relic current_hp_ratio is not proof of this module\'s HP coverage. Do not change natural SP, first charge, cycle, or recovery blockers from this raw parameter.',
     'Matching-version native ability attachment and HP-condition sampling/coverage, plus composition with other natural-SP sources and actual blocker behavior; source-only display may instead expose exact raw condition with actual activation unknown.'),
    ('char_1046_sbell2', 'uniequip_002_sbell2',
     ('max_valid_stack_cnt', 'sbell2_equip_1_1_p1', '范围内敌人越多造成的伤害越高'),
     'DISPLAY provides maximum15%; distinct hidden TALENT index-1/prefab10 provides damage_scale0.03 and max_valid_stack_cnt5. Existing single-target acquisition/windows and snow counts do not prove the number of enemies in range or native stack update/composition. Do not multiply output by1.15 or infer per-enemy stacks.',
     'Matching-version hidden ability attachment, exact stack acquisition/cap/update and scope, and final damage-composition layer; source-only display must preserve distinct DISPLAY and hidden-TALENT selectors without treating arithmetic0.03x5 as native proof.'),
    ('char_4204_mantra', 'uniequip_002_mantra',
     ('对处于元素爆发期间的敌人造成的伤害提升至110%', 'mantra_equip_1_1_p1'),
     'TRAIT states damage_scale1.1 during elemental burst. Current enemy_in_neural_break is an initial scenario flag and the engine can create neural-burst events; neither establishes this module\'s native attachment, target coverage or applicable damage streams. Do not multiply all damage or buildup and do not treat an initial flag as full-window coverage.',
     'Matching-version TRAIT attachment, applicable damage types/components and composition, element-burst condition acquisition/coverage/expiry and damage-to-buildup ordering; source-only display may expose parameter and explicit actual application unknown.'),
):
    p = catalog['operators'][oid]
    m = next(x for x in p['modules'] if x['id'] == module_id)
    original = originals['battle_equip_table']['data'][module_id]
    equip = originals['uniequip_table']['data']['equipDict'][module_id]
    assert m['unlock_elite'] == int(equip['unlockEvolvePhase'][-1])
    assert m['unlock_level'] == equip['unlockLevel']
    phase_parts = []
    for phase_index, phase in enumerate(original['phases']):
        assert m['levels'][phase_index]['parts'] == phase['parts']
        phase_parts.append({'selector': 'battle_equip_table.' + module_id + '.phases[' + str(phase_index) + '].parts',
                            'stage': phase_index+1, 'parts': phase['parts']})
    findings = []
    for needle in needles:
        findings.append({'needle': needle,
            'engine_line_numbers': [i for i, line in enumerate(engine.splitlines(), 1) if needle in line],
            'reporting_line_numbers': [i for i, line in enumerate(reporting.splitlines(), 1) if needle in line],
            'options_line_numbers': [i for i, line in enumerate(options.splitlines(), 1) if needle in line]})
    leads.append({'owner': oid, 'name': p['name'], 'module_id': module_id,
        'classification': 'possible_source_parameter_presentation_only; not_confirmed_product_defect',
        'original_equip_selector': 'uniequip_table.equipDict.' + module_id,
        'original_equip': equip, 'normalized_module': m,
        'original_stage_parts': phase_parts, 'string_reference_static_search': findings,
        'generic_boundary': 'Applicable modules already receive the generic unmodeled-trait/hidden-script note; estimate.complete excludes all nonempty module_parts. No existing claim of full module mechanism coverage was established.',
        'boundary': boundary, 'restart_evidence_needed': restart,
        'numeric_change_authorized': False, 'actual_activation': None,
        'attachment_verified': False, 'composition_verified': False})

write('exact-condition-source-candidates.json', {
    'game_commit': GAME_COMMIT, 'fixed_product_commit': COMMIT,
    'original_files': [{k:v for k,v in x.items() if k != 'data'} for x in originals.values()],
    'candidates': leads})

assert "已计模组基础属性与适用天赋数据覆盖；未建模的新增模组特性/隐藏战斗脚本不自动推断。" in engine
assert 'and not self.module_parts' in engine
write('readonly-review.json', {
    'status': 'three_source_parameter_candidates_only_no_confirmed_product_defect',
    'fixed_product_commit': COMMIT, 'fixed_public_files': files,
    'checked_generic_module_note': True,
    'checked_nonempty_module_parts_excluded_from_estimate_complete': True,
    'new_api_calls': 0, 'tests_executed': 0, 'gui_executed': False, 'wine_executed': False,
    'native_game_executed': False, 'tracked_edits': False,
    'method': 'Read-only git show blobs, JSON comparisons for only3 targeted modules, AST syntax parse and exact-string static source search; no project-runtime import or public calculation.',
    'no_rerun': 'Prior34-module/102-stage static-attribute/gate negative audit and section55 qualification matrix reused as evidence; not repeated. Targeted3-module raw parts equality is a source-selector check only.',
    'excluded_completed': ['Mei MAR-X', 'Gnosis ISW-A', 'Mizuki hidden identity modules', 'Orchid redeploy', 'Cammou/drone attack speed', 'Deepcolor and Wang known direct token fields'],
    'deferred_to_parent': ['Yato EXE-X stage2/3 attachment and composition'],
    'confirmed_product_defects': [],
    'numeric_change_authorized': False,
    'scope_limits': ['No output reproduction or user-facing runtime report validation.',
                    'Exact string absence is only a static lack of dedicated binding evidence, not proof of an arbitrary mechanism being absent.',
                    'Current version hot updates, game attachment and actual activation remain unknown.'],
    'preserved_preparation_diagnostics': [{'command': 'rg rouge/options.py rouge/app.py',
        'missing_path': 'rouge/options.py', 'actual_file_discovered': 'rouge/operator_options.py',
        'impact': 'A guessed readonly filename emitted an error; no dependent mutation or public call; corrected by rg --files.'}],
})

review_bytes = (OUT / 'readonly-review.json').read_bytes()
source_bytes = (OUT / 'exact-condition-source-candidates.json').read_bytes()
print(json.dumps({'passed_static_source_closure': True, 'confirmed_product_defects': 0,
    'source_parameter_candidates': len(leads), 'new_api_calls': 0,
    'receipt_sha256': sha(review_bytes), 'source_candidates_sha256': sha(source_bytes)}))
