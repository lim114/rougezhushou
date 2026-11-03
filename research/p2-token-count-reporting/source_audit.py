"""Read only pinned public tables and archived token reference receipts."""
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path('/workspace/rougezhushou')
OUT = Path(__file__).resolve().parent
OP = 'char_110_deepcl'
TOKEN = 'token_10001_deepcl_tentac'
MODULE = 'uniequip_002_deepcl'
COMMIT = 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'

def load(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))

def receipt(path):
    p = ROOT / path
    b = p.read_bytes()
    return {'path': path, 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()

tracked = (
    'rouge/catalog.py', 'rouge/summons.py', 'rouge/operator_engine.py',
    'rouge/damage.py', 'rouge/reporting.py', 'rouge/relics.py',
    'rouge/data/catalog.json', 'rouge/data/summon-module-rules.json',
    'tests/test_summon_modules_038.py', 'tests/test_summon_limits_069.py',
    'tests/test_token_manual_attributes.py',
)
head_before = git('rev-parse', 'HEAD')
before = {p: receipt(p) for p in tracked}
historical = load('research/p2-token-manual-attributes/source-receipt.json')
characters = load('.cache/p2-s1-binding/character_table.json')
skills = load('.cache/p2-s1-binding/skill_table.json')
catalog = load('rouge/data/catalog.json')
profile = catalog['operators'][OP]
raw_receipts = {}
for name in ('character_table', 'skill_table'):
    observed = receipt(f'.cache/p2-s1-binding/{name}.json')
    expected = historical['pinned_sources'][name]
    assert observed['sha256'] == expected['sha256']
    assert observed['bytes'] == expected['bytes']
    raw_receipts[name] = {
        **observed, 'url': expected['url'], 'source_commit': COMMIT,
        'fresh_local_content_rehashed': True, 'refetched_this_audit': False,
        'matches_pinned_historical_receipt': True,
    }

skill_rows = []
for index, raw_binding in enumerate(characters[OP]['skills']):
    sid = raw_binding['skillId']
    normalized = profile['skills'][index]
    assert normalized['id'] == sid
    phase = int(raw_binding['unlockCond']['phase'].removeprefix('PHASE_'))
    assert normalized['unlock_elite'] == phase
    for rank_index, raw in enumerate(skills[sid]['levels']):
        blackboard = {v['key']: v['value'] for v in raw['blackboard']}
        norm = normalized['levels'][rank_index]
        assert norm['values'] == blackboard
        assert norm['duration'] == raw['duration']
        assert norm['description'] == raw['description']
        assert norm['sp_cost'] == raw['spData']['spCost']
        assert norm['initial_sp'] == raw['spData']['initSp']
        skill_rows.append({
            'skill_number': index + 1, 'rank': rank_index + 1,
            'binding_selector': f'character_table.{OP}.skills[{index}]',
            'unlock_condition': raw_binding['unlockCond'],
            'selector': f'skill_table.{sid}.levels[{rank_index}]',
            'name': raw['name'], 'description': raw['description'],
            'skill_type': raw['skillType'], 'duration_parameter_seconds': raw['duration'],
            'blackboard': blackboard, 'sp_data': raw['spData'],
            'catalog_parameters_match': True,
            'actual_token_presence_or_regeneration_events_verified': False,
        })

field_map = {
    'maxHp': 'hp', 'atk': 'attack', 'def': 'defense',
    'attackSpeed': 'attack_speed', 'magicResistance': 'resistance',
    'cost': 'deployment_cost', 'baseAttackTime': 'interval',
    'respawnTime': 'redeploy_seconds', 'blockCnt': 'block_count',
    'spRecoveryPerSec': 'sp_recovery',
}
token_rows = []
for phase_index, phase in enumerate(characters[TOKEN]['phases']):
    norm_phase = profile['tokens'][TOKEN]['phases'][phase_index]
    assert phase['maxLevel'] == norm_phase['max_level']
    for frame_index, frame in enumerate(phase['attributesKeyFrames']):
        norm = norm_phase['frames'][frame_index]
        selected = {k: frame['data'][k] for k in field_map}
        assert norm['level'] == frame['level']
        assert all(norm[v] == selected[k] for k, v in field_map.items())
        token_rows.append({
            'selector': f'character_table.{TOKEN}.phases[{phase_index}].attributesKeyFrames[{frame_index}].data',
            'elite': phase_index, 'level': frame['level'],
            'values': {**selected, 'maxDeployCount': frame['data']['maxDeployCount']},
            'catalog_cultivation_parameters_match': True,
        })

talent_rows = []
for owner in (OP, TOKEN):
    for talent_index, talent in enumerate(characters[owner]['talents']):
        for candidate_index, candidate in enumerate(talent['candidates']):
            talent_rows.append({
                'selector': f'character_table.{owner}.talents[{talent_index}].candidates[{candidate_index}]',
                'owner': owner, 'candidate': candidate,
                'raw_parameter_alone_proves_inventory_or_concurrent_semantics': False,
            })

hp_proof = load('.cache/research/summon-068/native-proof.json')
limit_proof = load('.cache/research/summon-limit-069/native-proof.json')
wang_receipt = load('research/p2-wang-token-module-reference/source-receipt.json')
archives = (
    'research/p2-token-manual-attributes/NOTE.md',
    'research/p2-token-manual-attributes/source-receipt.json',
    'research/p2-wang-token-module-reference/NOTE.md',
    'research/p2-wang-token-module-reference/source-receipt.json',
    '.cache/research/summon-068/REPORT.md',
    '.cache/research/summon-068/native-proof.json',
    '.cache/research/summon-068/deepcl-equip-prefabs.json',
    '.cache/research/summon-limit-069/REPORT.md',
    '.cache/research/summon-limit-069/native-proof.json',
    '.cache/research/summon-limit-069/equip-addition-cfg.json',
    '.cache/research/summon-limit-069/verified-native-fields.json',
)
archival_receipts = {p: receipt(p) for p in archives}
for p, expected in wang_receipt['historical_native_receipt_hashes'].items():
    if p in archival_receipts:
        assert archival_receipts[p]['sha256'] == expected
        archival_receipts[p]['matches_section42_historical_receipt'] = True
module = next(m for m in profile['modules'] if m['id'] == MODULE)
module_parameters = [x for x in wang_receipt['token_module_parameters'] if x['module_id'] == MODULE]
assert len(module_parameters) == 3
rule = load('rouge/data/summon-module-rules.json')[MODULE]
missing_originals = {}
for name in ('battle_equip_table', 'uniequip_table'):
    candidates = [f'.cache/game-data/{name}.json', f'.cache/p2-s1-binding/{name}.json']
    observed_presence = {p: (ROOT / p).exists() for p in candidates}
    assert not any(observed_presence.values())
    missing_originals[name] = {
        **historical['pinned_sources'][name],
        'known_original_cache_paths_present': observed_presence,
        'fresh_raw_file_rehash': False,
        'evidence_kind': 'historical_pinned_receipt_and_current_archived_extract',
    }
after = {p: receipt(p) for p in tracked}
head_after = git('rev-parse', 'HEAD')
out = {
    'scope': 'section63_readonly_deepcolor_selected_count_report_source_closure',
    'created_utc': datetime.now(timezone.utc).isoformat(),
    'source_commit': COMMIT,
    'root_observation': {
        'branch': git('branch', '--show-current'), 'head_before': head_before,
        'head_after': head_after,
        'tracked_status_after': git('status', '--short'),
        'head_changed_during_readonly_audit': head_before != head_after,
        'selected_source_hashes_before': before,
        'selected_source_hashes_after': after,
        'selected_source_hash_drift': [p for p in tracked if before[p] != after[p]],
        'interpretation': 'Live root checkout observations; an independent root commit is not a frozen draft baseline.',
    },
    'fresh_pinned_raw_tables': raw_receipts,
    'historical_raw_tables_not_available': missing_originals,
    'raw_skill_records': skill_rows,
    'raw_token_cultivation_records': token_rows,
    'raw_owner_and_token_talent_records': talent_rows,
    'existing_count_contract': {
        'origin': 'Existing public implementation, not a new game mechanic.',
        'selectors': ['rouge.operator_engine.Combat.value', 'rouge.operator_engine.Combat.option',
                      'rouge.operator_engine.Combat.plan char_110_deepcl branch',
                      'rouge.reporting skill detail summons/regeneration sections',
                      'rouge.reporting relic_token_* module model_count metric'],
        'field': 'summon_count', 'default': 1,
        'validation': 'float(raw); finite, nonnegative, integral, no greater than the existing token cap; returns float.',
        'legal_numeric_string_forms': ['0', '1', '1.0', '1e0'],
        'string_lexical_type_is_not_a_new_game_mechanism': True,
        'maximum_origin': 'Existing token_concurrent_limit when known; otherwise existing selected 召唤触手 cnt fallback.',
        'report_raw_uses_at_observed_head': ['summons.summon_count', 'regeneration.all_tokens_rate', 'relic_token_*.model_count'],
        'report_s1_per_token_rate': 'hp_recovery_per_sec * existing relic_regeneration_multiplier',
        'report_s1_all_selected_rate': 'same fixed per-token reference * validated selected count',
        'per_token_rate_depends_on_token_hp': False,
        's2_hp_recovery_per_sec_parameter_present': False,
        'preserve_existing_valid_integer_float_string_range_semantics': True,
        'new_bool_rejection_or_new_count_maximum_requested_by_sources': False,
        'paired_api_behavior_or_patch_validation_scope': 'Parent audit; not executed by this source-only helper.',
    },
    'module_qualification_and_existing_references': {
        'normalized_gate_selector': f'catalog.operators.{OP}.modules[id={MODULE}]',
        'normalized_unlock_elite': module['unlock_elite'],
        'normalized_unlock_level': module['unlock_level'],
        'normalized_gate_fresh_rechecked_against_original_uniequip_raw': False,
        'historical_original_gate_selector': f'uniequip_table.equipDict.{MODULE}',
        'historical_token_parameters': module_parameters,
        'existing_module_rule': rule,
        'eligible_module_levels': [1, 2, 3],
        'existing_reference_gate': 'Matching token, owner, module ID and stage, elite >= 2 and level >= 40.',
        'locked_E1_or_E2_level39_module_not_applied': True,
        'nominal_default_concurrent_limits_without_module': limit_proof['default_limits_without_module'],
        'nominal_default_E2_concurrent_limit_with_unlocked_SUM_Y': limit_proof['default_e2_limit_with_unlocked_SUM_Y'],
        'held_limit_source_is_distinct_from_concurrent_limit_source': True,
        'selected_count_is_not_actual_held_or_live_count': True,
        'current_stock_global_slots_tiles_and_deployment_events_known': False,
    },
    'archived_evidence_fresh_file_hashes': archival_receipts,
    'historical_hp_layer_proof_reused': {
        'receipt_passed_when_recorded': hp_proof['passed'],
        'bindings': hp_proof['bindings'], 'formula': hp_proof['formula'],
        'base_bundle_sha256_recorded': hp_proof['bundle_sha256'],
        'fresh_original_bundle_DLL_or_metadata_byte_verification': False,
        'current_hotfix_equivalence_proven': False,
        'live_panel_pair_verified': False,
    },
    'unknown_protection_to_preserve': {
        'current_SUM_Y_hp_composition_verified_from_historical_proof': rule['hp_composition_verified'],
        'selector': 'rouge.summons.token_attributes',
        'if_nonzero_module_hp_composition_unverified_and_other_HP_pct_or_changed_rune_HP_present': {
            'composite_hp': None, 'dependent_percentage_regeneration': None,
            'hp_composition_pending': True,
            'isolated_module_only_and_other_sources_only_references_preserved': True,
        },
        's1_fixed_regeneration_is_not_percentage_HP_regeneration': True,
        'count_normalization_cannot_close_unknown_HP_layer': True,
        'no_actual_token_lifecycle_or_first_regeneration_tick_source_added': True,
    },
    'conclusions': {
        'narrow_source_supported_scope': 'Use the existing validated selected count for existing Deepcolor report calculations and numeric selected-count metrics.',
        'game_mechanism_added': False, 'new_actual_quantity_or_event_clock_inference': False,
        'tracked_files_modified_by_helper': False, 'wine_or_gui_executed': False,
        'private_state_read': False, 'game_actions': 0, 'external_messages_sent': 0,
    },
}
OUT.mkdir(parents=True, exist_ok=True)
(OUT / 'source-closure.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({
    'output': str(OUT / 'source-closure.json'), 'head_before': head_before,
    'head_after': head_after, 'source_hash_drift': out['root_observation']['selected_source_hash_drift'],
    'raw_skill_records': len(skill_rows), 'raw_token_cultivation_records': len(token_rows),
    'fresh_raw_tables_match': True, 'historical_module_raw_rehashed': False,
}, ensure_ascii=False))
