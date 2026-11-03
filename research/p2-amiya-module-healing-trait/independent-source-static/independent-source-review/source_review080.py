"""Independent, source-only medical Amiya ratio review. No product API calls."""
from pathlib import Path
import hashlib
import json
import subprocess

OUT = Path(__file__).resolve().parent
REPO = Path('/workspace/rougezhushou')
BASE = '4b1e4d1f0bd9c60bc87523d6ac05c61f77f2a52b'
GAME = 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'
OP = 'char_1037_amiya3'
MODULE = 'uniequip_002_amiya3'
FILES = {
    'char_patch_table': (Path('/workspace/.continuation/p2-after-076-condition-eligibility-audit/char_patch_table.json'), 'd1850d5aeec1a9246a0531e88c167e66745644957662c8272fc764f54904c57e'),
    'skill_table': (REPO / '.cache/p2-s1-binding/skill_table.json', '86f4aa64c785f39727edd06d6dd8a4f27f371c8e4ace5345ba0dc61dee1386ca'),
    'battle_equip_table': (Path('/workspace/.continuation/p2-after-070-source-audit/originals/battle_equip_table.json'), '006687f201a823abf31c6a1c57b2269099bd3ea375c2ec3ae5595cc98a1ec460'),
    'uniequip_table': (Path('/workspace/.continuation/p2-after-070-source-audit/originals/uniequip_table.json'), 'b508483cc87c03d8313f4dd8dfc1b9195bc50385a8dfec51d17e657cb26ffad9'),
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def save(name, data):
    target = OUT / name
    with target.open('x', encoding='utf-8') as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    return {'path': str(target), 'bytes': target.stat().st_size, 'sha256': sha(target.read_bytes())}


raw = {}
receipts = []
for kind, (path, expected) in FILES.items():
    content = path.read_bytes()
    actual = sha(content)
    assert actual == expected, (kind, actual, expected)
    raw[kind] = json.loads(content)
    receipts.append({'kind': kind, 'path': str(path), 'bytes': len(content), 'sha256': actual, 'pinned_hash_matches': True})

source_files = {}
for rel in ['rouge/data/catalog.json', 'rouge/operator_engine.py', 'rouge/drone_traits.py',
            'research/p2-amiya-phase-reference/NOTE.md',
            'research/p2-module-qualification-notes/NOTES.md',
            'tests/test_amiya_phase_reference.py']:
    content = subprocess.check_output(['git', 'show', BASE + ':' + rel], cwd=REPO)
    source_files[rel] = content
    receipts.append({'kind': 'fixed_git_blob', 'commit': BASE, 'path': rel,
                     'bytes': len(content), 'sha256': sha(content)})
catalog = json.loads(source_files['rouge/data/catalog.json'])['operators'][OP]
patch = raw['char_patch_table']
character = patch['patchChars'][OP]
assert OP in patch['infos']['char_002_amiya']['tmplIds']
assert patch['patchDetailInfoList'][OP]['infoParam'] == '医疗'
assert character['profession'] == 'MEDIC'
assert character['subProfessionId'] == 'incantationmedic'
assert '50%' in character['description']
assert catalog['trait'] == character['trait']
base_candidate = character['trait']['candidates'][0]
assert len(character['trait']['candidates']) == 1
assert base_candidate['blackboard'] == [{'key': 'scale', 'value': 0.5, 'valueStr': None}]
assert base_candidate['unlockCondition'] == {'phase': 'PHASE_0', 'level': 1}
assert base_candidate['requiredPotentialRank'] == 0

metadata = raw['uniequip_table']['equipDict'][MODULE]
assert metadata['charId'] == 'char_002_amiya'
assert metadata['tmplId'] == OP
assert MODULE in raw['uniequip_table']['charEquip'][OP]
assert metadata['unlockEvolvePhase'] == 'PHASE_2' and metadata['unlockLevel'] == 50
assert metadata['typeName1'] == 'INC' and metadata['typeName2'] == 'X'
normalized = next(item for item in catalog['modules'] if item['id'] == MODULE)
assert normalized['unlock_elite'] == 2 and normalized['unlock_level'] == 50
original_module = raw['battle_equip_table'][MODULE]
assert len(original_module['phases']) == len(normalized['levels']) == 3
checked = []
for index, phase in enumerate(original_module['phases']):
    level = normalized['levels'][index]
    assert phase['equipLevel'] == level['level'] == index + 1
    assert phase['parts'] == level['parts']
    assert {b['key']: b['value'] for b in phase['attributeBlackboard']} == level['attributes']
    traits = [part for part in phase['parts'] if part['target'] == 'TRAIT_DATA_ONLY']
    assert len(traits) == 1
    part = traits[0]
    assert part['isToken'] is False
    assert part['resKey'] is None
    assert part['validInGameTag'] is None and part['validInMapTag'] is None
    candidates = part['overrideTraitDataBundle']['candidates']
    assert len(candidates) == 1
    candidate = candidates[0]
    assert candidate['blackboard'] == [{'key': 'scale', 'value': 0.6, 'valueStr': None}]
    assert candidate['overrideDescripton'] == base_candidate['overrideDescripton']
    assert candidate['additionalDescription'] is None
    assert candidate['unlockCondition'] == {'phase': 'PHASE_2', 'level': 50}
    assert candidate['requiredPotentialRank'] == 0
    checked.append({'stage': index + 1, 'selector': f'battle_equip_table.{MODULE}.phases[{index}].parts[0]',
                    'base_scale': 0.5, 'override_scale': 0.6, 'identical_full_trait_template': True,
                    'same_existing_ratio_parameter_replacement': True,
                    'runtime_attachment_verified': False})

skill_objects = {}
skill_checks = []
for index, skill in enumerate(character['skills']):
    sid = skill['skillId']
    original = raw['skill_table'][sid]
    product = catalog['skills'][index]
    assert product['id'] == sid
    assert len(original['levels']) == len(product['levels']) == 10
    for rank, (level, normalized_level) in enumerate(zip(original['levels'], product['levels']), 1):
        assert level['description'] == normalized_level['description']
        assert {b['key']: b['value'] for b in level['blackboard']} == normalized_level['values']
        skill_checks.append({'skill': sid, 'rank': rank, 'description_and_parameters_equal': True})
    skill_objects[sid] = original

engine = source_files['rouge/operator_engine.py'].decode('utf-8')
start = engine.index("        elif op in ('char_002_amiya','char_1001_amiya2','char_1037_amiya3'):")
end = engine.index("        elif op=='char_1044_hsgma2':", start)
medical_block = engine[start:end]
assert medical_block.count("damage_healing('咒愈师伤害转治疗',.5*min(1,healing_targets))") == 3
assert "'opening_healing_reference':components[0]['total']*.5*min(1,healing_targets)," in medical_block
known_limits = [
    'This review establishes the original same-parameter replacement reference, not a native module attachment or script execution proof.',
    'Existing medical S2 opening damage and linked healing remain conditional source references; raw trait wording does not independently establish actual opening-heal trigger order.',
    'Actual opening/buff/healing chain order, skill end and follow-up phase clocks remain unverified.',
    'Actual friendly acquisition, range/adjacency, effective received healing and other friendly maximum HP remain outside this source review.',
    'The ratio replacement is not multiplication/addition of 0.5 and 0.6 and does not establish relic stacking order.',
    'The independent regeneration talent and S1 additional attack-scaled area heal are separate parameters; this trait ratio review does not change them.',
    'No API, test, Qt, Wine, Windows, game, capture or chat execution was performed by this reviewer.',
]
selector_receipt = save('original-selectors.json', {
    'pinned_game_commit': GAME,
    'form_binding': patch['infos']['char_002_amiya'],
    'medical_form_detail': patch['patchDetailInfoList'][OP],
    'medical_form_identity': {key: character[key] for key in ['name', 'profession', 'subProfessionId', 'description', 'trait']},
    'raw_module_metadata': metadata,
    'raw_medical_char_equip': raw['uniequip_table']['charEquip'][OP],
    'raw_module_all_three_stages': original_module,
    'raw_medical_skills': skill_objects,
})
legacy_paths = [
    Path('/workspace/.continuation/p2-ordinary-module-lead-after-075/bounded-module-lead-review.json'),
    Path('/workspace/.continuation/p2-amiya-regeneration-talent-qualification-079/NOTE.md'),
    Path('/workspace/.continuation/p2-cargo58-independent/NOTE.md'),
    Path('/workspace/.continuation/p2-after-070-source-audit/NOTE.md'),
]
legacy = [{'path': str(path), 'bytes': path.stat().st_size, 'sha256': sha(path.read_bytes())} for path in legacy_paths]
result = save('source-review080.json', {
    'status': 'confirmed_same_trait_percentage_replacement_reference_with_native_boundaries',
    'independent': True, 'fixed_product_commit': BASE, 'pinned_game_commit': GAME,
    'tracked_edits': False, 'public_api_calls': 0, 'tests_run': 0,
    'qt_executed': False, 'wine_executed': False, 'native_windows_executed': False,
    'new_network_requests': 0,
    'verified_raw_and_fixed_product_inputs': receipts,
    'medical_form_binding_original': True,
    'base_trait_is_fifty_percent_not_forty_percent': True,
    'catalog_base_trait_exact_original': True,
    'all_three_stage_complete_parts_and_attributes_match_original': True,
    'same_trait_percentage_replacement_checks': checked,
    'all_twenty_medical_skill_ranks_description_and_parameters_match': skill_checks,
    'current_implementation_source_findings': {
        'fixed_baseline_medical_block': medical_block,
        'hardcoded_half_ratio_dependency_sites': 3,
        'hardcoded_half_ratio_opening_reference_sites': 1,
        'scope': 'normal attacks, existing S1 dependency, existing S2 dependency/opening reference',
        'selected_talents_returns_eligible_module_parts': True,
        'no_numerical_public_defect_result_claimed_from_static_read': True,
    },
    'prior_readonly_research_inputs': legacy,
    'prior_work_boundary': 'Section 45 already keeps medical S2 linked healing and opening references conditional. Section 55 and the ordinary 34-module audit established metadata/parts equality, not consumption of this exact ratio. Section 79 fixes own regeneration qualification, a separate parameter.',
    'mechanics_decision': 'Sufficient original evidence to use 0.6 as the eligible INC-X same-trait ratio parameter in the existing offline reference, selecting exactly the reviewed owner/part/candidate and preserving all native unknowns. No source support for 0.5*0.6, 0.5+0.6, or treating the override as a global healing modifier.',
    'remaining_unknowns': known_limits,
    'raw_selector_artifact': selector_receipt,
    'preparation_diagnostics': [
        {'operation': 'First broad text search', 'exit_code': 2, 'reason': 'Included nonexistent docs path and minified JSON in an overbroad result; it did not run a product API or change files. Replaced with exact source paths and parsed selectors.'},
        {'operation': 'Initial patchDetailInfoList schema inspection', 'exit_code': 1, 'error': "AttributeError: 'str' object has no attribute 'get'", 'reason': 'Iterated the original mapping as though it were a list of dicts. Read its actual dict schema and exact char_1037_amiya3 selector. No source/API conclusion used that failed probe.'},
    ],
})
print(json.dumps(result, ensure_ascii=False))
