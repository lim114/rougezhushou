"""Bounded source/report lead audit, six real public calls, no model changes."""
from pathlib import Path
import copy
import hashlib
import io
import json
import subprocess
import sys
import tarfile

OUT = Path(__file__).resolve().parent
REPO = Path('/workspace/rougezhushou')
BASE = 'c950fbc800245f7f784d6070f7126890352ffcc9'
GAME = 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'
OP = 'char_1029_yato2'
MODULE = 'uniequip_002_yato2'


def sha(data): return hashlib.sha256(data).hexdigest()


def save(name, obj):
    with (OUT / name).open('x', encoding='utf-8') as stream:
        json.dump(obj, stream, ensure_ascii=False, indent=2, allow_nan=False); stream.write('\n')


paths = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', BASE, 'rouge'], cwd=REPO, text=True).splitlines()
paths = [rel for rel in paths if rel.endswith(('.py', '.json'))]
archive = subprocess.check_output(['git', 'archive', '--format=tar', BASE, *paths], cwd=REPO)
package = OUT / 'fixed-public-package'
package.mkdir()
with tarfile.open(fileobj=io.BytesIO(archive)) as stream:
    for member in stream:
        if not member.isfile(): continue
        assert member.name in paths
        target = package / member.name
        target.parent.mkdir(parents=True, exist_ok=True)
        content = stream.extractfile(member).read()
        with target.open('xb') as file: file.write(content)
source = {rel: {'bytes': (package / rel).stat().st_size, 'sha256': sha((package / rel).read_bytes())} for rel in paths}
originals = {
    'character_table': (REPO / '.cache/p2-s1-binding/character_table.json', '68e3a3b5ee0d407ce234afaa5867c6fda6379a6843c7d5317a7bbda4779f8697'),
    'battle_equip_table': (Path('/workspace/.continuation/p2-after-070-source-audit/originals/battle_equip_table.json'), '006687f201a823abf31c6a1c57b2269099bd3ea375c2ec3ae5595cc98a1ec460'),
    'uniequip_table': (Path('/workspace/.continuation/p2-after-070-source-audit/originals/uniequip_table.json'), 'b508483cc87c03d8313f4dd8dfc1b9195bc50385a8dfec51d17e657cb26ffad9'),
}
raw = {}; raw_hashes = []
for kind, (path, expected) in originals.items():
    content = path.read_bytes()
    assert sha(content) == expected
    raw[kind] = json.loads(content)
    raw_hashes.append({'kind': kind, 'path': str(path), 'bytes': len(content), 'sha256': expected})
metadata = raw['uniequip_table']['equipDict'][MODULE]
assert metadata['charId'] == OP and metadata['tmplId'] is None
assert metadata['unlockEvolvePhase'] == 'PHASE_2' and metadata['unlockLevel'] == 60
assert metadata['typeName1'] == 'EXE' and metadata['typeName2'] == 'X'
profile = json.loads((package / 'rouge/data/catalog.json').read_text())['operators'][OP]
normalized = next(module for module in profile['modules'] if module['id'] == MODULE)
assert normalized['unlock_elite'] == 2 and normalized['unlock_level'] == 60
phases = raw['battle_equip_table'][MODULE]['phases']
for original, level in zip(phases, normalized['levels']):
    assert original['parts'] == level['parts']
assert len(phases) == 3
extra_candidates = []
for index, value in [(1, .03), (2, .05)]:
    part = phases[index]['parts'][1]
    for candidate in part['addOrOverrideTalentDataBundle']['candidates']:
        assert candidate['name'] == '鬼人强化状态' and candidate['talentIndex'] == 1
        assert candidate['prefabKey'] == '2'
        parameters = {entry['key']: entry['value'] for entry in candidate['blackboard']}
        assert parameters['yato2_e_002[atk].atk'] == value
        extra_candidates.append({'selector': f'battle_equip_table.{MODULE}.phases[{index}].parts[1].addOrOverrideTalentDataBundle',
                                 'stage': index + 1, 'candidate': candidate})
engine = (package / 'rouge/operator_engine.py').read_text()
reporting = (package / 'rouge/reporting.py').read_text()
assert "attack+=self.base*self.talent('鬼人强化状态','atk')" in engine
assert 'yato2_e_002[atk].atk' not in engine
assert "not self.module_parts" in engine
assert "'complete_definition':'complete仅表示所选藏品规则支持；不代表完整战斗模拟。'" in engine
assert "'计算状态：'+('支持范围内估算' if estimate['complete'] else '不完整（见待确认与适用范围）')" in reporting
prior = Path('/workspace/.continuation/p2-ordinary-module-lead-after-075/bounded-module-lead-review.json')
previous = json.loads(prior.read_text())
assert previous['deferred_exact_yato_lead']['module'] == MODULE
save('freeze082.json', {'fixed_commit': BASE, 'production_public_files': source,
                       'raw_hashes': raw_hashes, 'prior_negative_audit': {'path': str(prior), 'sha256': sha(prior.read_bytes())},
                       'pinned_game_commit': GAME, 'planned_public_calls': 6, 'tracked_edits': False,
                       'repeat_of_34_module_gate_or_102_static_attribute_audit': False})
save('raw-yato-selectors082.json', {'module_metadata': metadata, 'module_all_three_stages': raw['battle_equip_table'][MODULE],
                                  'base_original_talents': raw['character_table'][OP]['talents'], 'exact_extra_candidates': extra_candidates})

sys.path.insert(0, str(package))
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate
from rouge.reporting import format_report

original_catalog = copy.deepcopy(catalog())
rows = []
expected_unknown_note = '已计模组基础属性与适用天赋数据覆盖；未建模的新增模组特性/隐藏战斗脚本不自动推断。'
for stage in (2, 3):
    for skill in (1, 2, 3):
        s = {'operator': OP, 'skill': skill, 'skill_rank': 10, 'base_attack': 1000,
             'elite': 2, 'level': 60, 'potential': 1, 'module_id': MODULE, 'module_level': stage,
             'timing_mode': 'frames', 'window_seconds': 10}
        before = copy.deepcopy(s)
        result = calculate_damage(s)
        text = format_report(result)
        technical = format_report(result, technical=True)
        estimate_text = format_estimate(result)
        save(f'public-yato-stage{stage}-skill{skill}.json', {
            'scenario': s, 'result': result, 'report_text': text,
            'technical_report_text': technical, 'estimate_text': estimate_text,
            'actual_calculate_damage_calls_for_this_artifact': 1})
        assert s == before
        assert result['estimate']['complete'] is False
        assert expected_unknown_note in result['estimate']['notes']
        assert expected_unknown_note in text and expected_unknown_note in technical
        assert '计算状态：不完整（见待确认与适用范围）' in text
        assert '仅列当前身份/培养/模组适用的资料；已量化范围与未覆盖项见估算状态。' in text
        advertised = '技能期间攻击力额外+' + ('3%' if stage == 2 else '5%')
        assert advertised in text
        if skill in (2, 3):
            assert result['total_damage'] is None
            assert result['estimate']['skill']['duration_seconds'] is None
        rows.append({'scenario': s, 'result': result, 'report_text': text, 'technical_report_text': technical,
                     'estimate_text': estimate_text, 'reported_unknown_module_scope': True,
                     'reported_full_model_incomplete': True, 'selected_talent_source_description_visible': True})
assert len(rows) == 6 and catalog() == original_catalog
for rel, entry in source.items():
    assert sha((package / rel).read_bytes()) == entry['sha256']
save('public-yato082.json', rows)
save('yato-gap-review082.json', {
    'status': 'negative_no_confirmed_reporting_or_complete_defect', 'fixed_commit': BASE,
    'public_calls': 6, 'accepted': 6, 'errors': 0,
    'all_public_reports_already_mark_module_scope_unmodeled': True,
    'all_estimate_complete_flags_already_false': True,
    'top_level_complete_meaning': 'Selected relic-rule support only; source explicitly excludes complete battle-model meaning.',
    'trait_extra_three_five_percent_source_description_visible_as_data': True,
    'prior_native_defer_unchanged': True,
    'native_numeric_implementation_authorized': False,
    'restart_evidence_needed': previous['deferred_exact_yato_lead']['restart_evidence_needed'],
    'source_reference_enhancement_possible_but_not_confirmed_current_product_defect': True,
    'tracked_edits': False, 'qt_executed': False, 'wine_executed': False,
    'native_windows_executed': False, 'public_source_drift': False,
    'no_claim_of_hidden_or_null_prefab_runtime_attachment': True,
})
print(json.dumps({'status': 'negative_no_confirmed_reporting_or_complete_defect', 'actual_public_calls': 6,
                  'production_source_files_frozen': len(source), 'receipt_sha256': sha((OUT / 'yato-gap-review082.json').read_bytes())}))
