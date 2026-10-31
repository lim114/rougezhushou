"""A source-bound current-document overlay for one moving reward enemy.

No reference is a spawn, kill or grant. The original fixed reward data remains
independent; invalid current-document qualifications never borrow grade zero.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = 'research/runtime-reference-loaders-20261031/moving-rewards/source-manifest.json'
MANIFEST_SHA256 = '5b23e8f5dbcbe30e537f57825c3c40abb7f140a843d7e45564ed327b94452383'
DATA = 'rouge/data/moving-reward-current-reference.json'
ENTITY = 'enemy_2152_shezlc'


def source_data():
    """Freshly verify fixed public files, even after an earlier valid call."""
    try:
        raw_manifest = (ROOT / MANIFEST).read_bytes()
        if hashlib.sha256(raw_manifest).hexdigest() != MANIFEST_SHA256:
            return None
        manifest = json.loads(raw_manifest)
        blobs = {}
        for relative, expected in manifest['files'].items():
            path = ROOT / relative
            if not path.resolve().is_relative_to(ROOT.resolve()) or not path.is_file():
                return None
            raw = path.read_bytes()
            if len(raw) != expected['bytes'] or hashlib.sha256(raw).hexdigest() != expected['sha256']:
                return None
            blobs[relative] = raw
        data = json.loads(blobs[DATA])
        if (data['entity_id'] != ENTITY or data['source']['revision'] != '435751'
                or data['documented_levels'] != [0, 1, 2]):
            return None
        return data
    except (OSError, ValueError, KeyError, TypeError):
        return None


def _reference_qualification(refs):
    reasons = []
    bad = []
    levels = []
    if type(refs) is not list or not refs:
        return {'all_qualified': False, 'reference_count': len(refs) if type(refs) is list else None,
                'invalid_reference_indices': [],
                'reasons': [{'index': None, 'reason': 'nonempty_reference_list_required'}]}, []
    for index, ref in enumerate(refs):
        row_reasons = []
        if type(ref) is not dict:
            row_reasons.append('reference_not_exact_object')
        else:
            raw = ref.get('raw')
            if type(raw) is not dict:
                row_reasons.append('raw_not_exact_object')
            else:
                if type(raw.get('id')) is not str or raw['id'] != ENTITY:
                    row_reasons.append('entity_identity_not_exact')
                if raw.get('useDb') is not True:
                    row_reasons.append('use_db_not_explicitly_true')
                if type(raw.get('level')) is not int or raw['level'] not in (0, 1, 2):
                    row_reasons.append('grade_missing_or_unsupported')
                if 'overwrittenData' not in raw or raw['overwrittenData'] is not None:
                    row_reasons.append('explicit_null_override_required')
                if not row_reasons:
                    levels.append(raw['level'])
        if row_reasons:
            bad.append(index)
            reasons.extend({'index': index, 'reason': value} for value in row_reasons)
    return {'all_qualified': not bad, 'reference_count': len(refs),
            'invalid_reference_indices': bad, 'reasons': reasons}, sorted(set(levels))


def moving_reward_rule(refs):
    """Return conditional per-enemy documentation, with strict fixed-ref gates.

    ``refs`` uses the existing ``moving_enemy_refs`` shape: a nonempty list of
    objects containing an exact ``raw`` DB reference. Extra diagnostic fields
    are ignored, never copied into output or interpreted as qualification.
    """
    data = source_data()
    qualification, levels = _reference_qualification(refs)
    source_valid = data is not None
    qualified = source_valid and qualification['all_qualified']
    by_level = data['documented_outcomes_by_level'] if data else {}
    quantities = {}
    for condition in ('defeated', 'reached_route_end'):
        values = [by_level[str(level)][condition] for level in levels] if qualified else []
        quantities[condition] = (values[0] if values and all(value == values[0] for value in values)
                                 else None)
    quantity_consensus = qualified and all(value is not None for value in quantities.values())
    multiple_levels = quantity_consensus and len(levels) > 1
    scope_notice = (
        '资料中各候选等级的条件奖励数量相同；尚未确认本局实际等级、是否出现或领取，不按引用数累加。'
        if multiple_levels else
        '仅为资料中的条件奖励；本局是否出现、击倒或漏过以及实际领取均未确认。'
        if quantity_consensus else
        '无法确认敌人身份、对应等级或关卡是否改动了它；数量暂时未知，不沿用等级0或忽略未确认的候选。')
    labels = {'defeated': '该移动敌人被击倒，战斗结束后额外获得源石锭',
              'reached_route_end': '该移动敌人到达自身路径终点，战斗结束后扣除源石锭'}
    return {'entity_id': ENTITY, 'name': '恶笼草（移动敌人）',
            'source_valid': source_valid,
            'reference_qualification': qualification,
            'referenced_levels': levels,
            'documented_levels': [0, 1, 2] if source_valid else [],
            'all_fixed_level_candidates_documented': qualified,
            'documented_base_level_matches_reference': qualified and levels == [0],
            'action_level_binding_unique': qualified and len(levels) == 1,
            'all_candidate_quantities_agree': quantity_consensus,
            'candidate_level_consensus': multiple_levels,
            'quantity_source': deepcopy(data['source']) if data else None,
            'outcomes': [{'condition': condition, 'condition_label': labels[condition],
                          'resource': 'gold', 'quantity': quantities[condition],
                          'actual_quantity': None, 'quantity_is_total': False}
                         for condition in ('defeated', 'reached_route_end')],
            'quantity_scope_notice': scope_notice,
            'actual_reward': None, 'actual_spawn_level': None,
            'actual_reward_total': None, 'actual_defeated_count': None,
            'actual_route_end_count': None, 'probability': None,
            'current_rogue6_server_script_verified': False,
            'complete_effective_level_binding_known': False}
