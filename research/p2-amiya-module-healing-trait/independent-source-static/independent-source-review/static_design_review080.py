"""Review frozen section 80 source design without calling the public product."""
from pathlib import Path
import hashlib
import json
import subprocess

PARENT = Path('/workspace/.continuation/p2-amiya-trait-scale-080')
OUT = Path(__file__).resolve().parent
REPO = Path('/workspace/rougezhushou')
BASE = '4b1e4d1f0bd9c60bc87523d6ac05c61f77f2a52b'


def sha(data):
    return hashlib.sha256(data).hexdigest()


inputs = []
contents = {}
for rel in ['rouge/operator_engine.py', 'rouge/catalog.py', 'rouge/damage.py', 'rouge/data/catalog.json']:
    baseline = (PARENT / 'baseline' / rel).read_bytes()
    draft = (PARENT / 'draft' / rel).read_bytes()
    expected = subprocess.check_output(['git', 'show', BASE + ':' + rel], cwd=REPO)
    assert baseline == expected, rel
    if rel != 'rouge/operator_engine.py':
        assert draft == baseline, rel
    inputs.append({'path': rel, 'baseline_sha256': sha(baseline), 'draft_sha256': sha(draft),
                   'baseline_matches_fixed_git_blob': True,
                   'draft_equals_baseline': draft == baseline})
    contents[rel] = (baseline, draft)

baseline, draft = contents['rouge/operator_engine.py']
added = '''            if op=='char_1037_amiya3':
                # The reviewed INC-X data-only bundle replaces this same trait ratio.
                healing_scale=next(b['value'] for b in self.p['trait']['candidates'][0]['blackboard'] if b['key']=='scale')
                if self.s.get('module_id')=='uniequip_002_amiya3':
                    for part in self.module_parts:
                        if (part.get('target')=='TRAIT_DATA_ONLY' and not part.get('isToken') and
                                part.get('validInGameTag') is None and part.get('validInMapTag') is None):
                            candidate=part['overrideTraitDataBundle']['candidates'][0]
                            healing_scale=next(b['value'] for b in candidate['blackboard'] if b['key']=='scale')
'''.replace('\n', '\r\n').encode('utf-8')
assert draft.count(added) == 1
assert draft.count(b"damage_healing('") >= 3
assert draft.count("damage_healing('咒愈师伤害转治疗',healing_scale*min(1,healing_targets))".encode()) == 3
assert draft.count(b"'opening_healing_reference':components[0]['total']*healing_scale*min(1,healing_targets),") == 1
reverted = draft.replace(added, b'').replace(
    "damage_healing('咒愈师伤害转治疗',healing_scale*min(1,healing_targets))".encode(),
    "damage_healing('咒愈师伤害转治疗',.5*min(1,healing_targets))".encode()).replace(
    b"'opening_healing_reference':components[0]['total']*healing_scale*min(1,healing_targets),",
    b"'opening_healing_reference':components[0]['total']*.5*min(1,healing_targets),")
assert reverted == baseline
engine = draft.decode('utf-8')
catalog_code = contents['rouge/catalog.py'][1].decode('utf-8')
damage = contents['rouge/damage.py'][1].decode('utf-8')
assert "self.talents,self.module_parts=selected_talents(self.p,scenario)" in engine
assert "if module and elite>=module['unlock_elite'] and level>=module['unlock_level']:" in engine
assert "parts=module['levels'][scenario['module_level']-1]['parts']" in engine
assert "not isinstance(module_level,int) or isinstance(module_level,bool) or not 1<=module_level<=len(module['levels'])" in catalog_code
assert "raise ValueError('模组身份或等级尚无可用规则。')" in catalog_code
assert damage.index('attributes=operator_attributes(') < damage.index('result=calculate_extended(scenario,attributes)')
assert damage.index('def _prepare_damage(') < damage.index('def _evaluate_damage_once(')
profile = json.loads(contents['rouge/data/catalog.json'][1])['operators']['char_1037_amiya3']
assert len(profile['trait']['candidates']) == 1
assert profile['trait']['candidates'][0]['unlockCondition'] == {'phase': 'PHASE_0', 'level': 1}
assert profile['trait']['candidates'][0]['requiredPotentialRank'] == 0
module = next(m for m in profile['modules'] if m['id'] == 'uniequip_002_amiya3')
assert module['unlock_elite'] == 2 and module['unlock_level'] == 50
for stage in module['levels']:
    parts = [p for p in stage['parts'] if p['target'] == 'TRAIT_DATA_ONLY']
    assert len(parts) == 1
    candidates = parts[0]['overrideTraitDataBundle']['candidates']
    assert len(candidates) == 1
    assert candidates[0]['unlockCondition'] == {'phase': 'PHASE_2', 'level': 50}
    assert candidates[0]['requiredPotentialRank'] == 0

receipt = {
    'status': 'passed_source_design_only',
    'fixed_product_commit': BASE,
    'source_closure_receipt': {'path': str(OUT / 'source-review080.json'),
                              'sha256': sha((OUT / 'source-review080.json').read_bytes())},
    'reviewed_parent_draft': str(PARENT / 'draft'),
    'inputs': inputs,
    'whole_engine_inverse_reconstruction_equals_baseline': True,
    'only_nine_line_medical_ratio_selection_and_four_ratio_use_sites': True,
    'medical_owner_and_reviewed_module_identity_restricted': True,
    'module_parts_from_existing_module_elite_level_gate': True,
    'all_pinned_candidates_unique_and_candidate_gates_match_module_gate': True,
    'no_new_global_native_attachment_or_stacking_claim': True,
    'existing_invalid_module_identity_level_error_path_unchanged_before_engine': True,
    'invalid_module_level_zero_public_execution_verified': False,
    'public_api_calls': 0,
    'tests_run': 0,
    'qt_executed': False,
    'wine_executed': False,
    'native_windows_executed': False,
    'remaining_action': 'Root/author must validate accepted and rejected public behavior, including gate boundaries and module_level 0. Static order establishes the unchanged path but does not claim execution.',
    'limits': 'Candidate[0] is justified only for these exact pinned unique base/override bundles. This receipt does not authorize broad application to future multi-candidate traits or a general null-prefab attachment rule.',
}
target = OUT / 'static-design-review080.json'
with target.open('x', encoding='utf-8') as stream:
    json.dump(receipt, stream, ensure_ascii=False, indent=2)
    stream.write('\n')
print(json.dumps({'path': str(target), 'bytes': target.stat().st_size, 'sha256': sha(target.read_bytes())}))
