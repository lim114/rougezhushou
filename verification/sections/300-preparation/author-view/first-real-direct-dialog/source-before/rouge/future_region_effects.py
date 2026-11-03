"""Exact red-moss choices and alternative next-region document effects.

This module reads fixed public sources. It never changes a run or evaluates an
actual weather modifier, eligibility, a random reward, or a combat statistic.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
DATA = 'rouge/data/future-region-effects.json'
MANIFEST = 'research/p3-future-region-effects-300/source-manifest.json'
DATA_SHA256 = 'ef6d699cb48318f9bab1895fa84d8bc78dcb64439a51a9da6b14f9c34ac7a367'
MANIFEST_SHA256 = '1bbc5d7eb9b872cc2ed4b0857b011c4ffbdd05b440372a9e060932531ab39894'
SELECTED_AUTHORITY = 'research/p3-future-region-effects-300/selected-authority-records.json'
EVENT_ID = 'community_group_009'
ACTUAL_FIELDS = ('actual_choice', 'actual_weather', 'actual_phase', 'actual_affected_nodes', 'actual_reward', 'actual_quantity')
_parsed_packet = None


def _sha(raw): return hashlib.sha256(raw).hexdigest()


def _canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf8')


def _same_json(value, expected):
    if type(value) is not type(expected): return False
    if type(expected) is dict:
        return value.keys() == expected.keys() and all(type(k) is str and _same_json(value[k], expected[k]) for k in value)
    if type(expected) is list:
        return len(value) == len(expected) and all(_same_json(a, b) for a, b in zip(value, expected))
    return value == expected


def _source_path(relative):
    if type(relative) is not str: raise ValueError('Source path must be text.')
    path = PurePosixPath(relative)
    if path.is_absolute() or '..' in path.parts or '\\' in relative or ':' in relative:
        raise ValueError('Invalid source path.')
    result = ROOT.joinpath(*path.parts)
    if not result.resolve().is_relative_to(ROOT.resolve()): raise ValueError('Source escaped root.')
    return result


def _valid_schema(packet, current):
    if type(packet) is not dict or packet.get('schema') != 'future_region_effects_v1': return False
    if packet['event_id'] != EVENT_ID or packet['event_title'] != '呼吸的红苔': return False
    if packet['current_server_verified'] is not False or packet['entry_restored'] is not False: return False
    if packet['calculation_applied'] is not False or packet['run_state_updated'] is not False: return False
    expected = packet['expected_event']
    if not _same_json(current, expected): return False
    phases = packet['phases']
    if len(phases) != 3 or [(p['phase'], p['attack_percent'], p['max_hp_percent']) for p in phases] != [
            ('early', 10, 10), ('middle', 15, 20), ('late', 20, 30)]: return False
    rows = packet['choices']
    if len(rows) != 2: return False
    for index, row in enumerate(rows):
        key = EVENT_ID + ':scene:0:choice:' + str(index)
        if row['reference_id'] != key or row['choice_key'] != key or row['scene_key'] != EVENT_ID + ':scene:0': return False
        if not _same_json(row['catalog_choice'], expected['scenes'][0]['choices'][index]): return False
        if not _same_json(row['game_choice_ids'], [] if index == 0 else ['choice_ro6_normal3_2']): return False
        if row['entry_restored'] is not False or any(row[k] is not None for k in ACTUAL_FIELDS): return False
        if not _same_json(row['future_region_reference']['phases'], phases): return False
        reward = row['conditional_victory_reward']
        if any(reward[k] is not None for k in ('quantity_reference', 'complete_pool', 'actual_received')): return False
    return True


def _verified_packet():
    global _parsed_packet
    try:
        manifest_raw = _source_path(MANIFEST).read_bytes()
        if _sha(manifest_raw) != MANIFEST_SHA256: return None
        manifest = json.loads(manifest_raw)
        if (manifest['schema'] != 'future_region_effects_source_manifest_v1' or manifest['data_file'] != DATA
                or manifest['data_sha256'] != DATA_SHA256 or manifest['event_id'] != EVENT_ID
                or manifest['selected_authority_file'] != SELECTED_AUTHORITY
                or manifest['runtime_reads_primary_table'] is not False
                or manifest['runtime_verifies_complete_original_bytes'] is not False): return None
        # Selected complete records are freshly checked on each query. Complete
        # 17.9MB originals remain pinned build inputs, not repeated runtime I/O.
        selected_raw = {}
        for relative, pin in manifest['runtime_files'].items():
            if not _same_json(pin, manifest['files'][relative]): return None
            value = _source_path(relative).read_bytes()
            if type(pin['bytes']) is not int or len(value) != pin['bytes'] or _sha(value) != pin['sha256']: return None
            if relative in (DATA, SELECTED_AUTHORITY, 'rouge/data/node-catalog.json'): selected_raw[relative] = value
        if _sha(selected_raw[DATA]) != DATA_SHA256: return None
        authority = json.loads(selected_raw[SELECTED_AUTHORITY])
        if authority['schema'] != 'future_region_selected_authority_v1' or authority['event_id'] != EVENT_ID: return None
        current_catalog = json.loads(selected_raw['rouge/data/node-catalog.json'])
        current = next(e for e in current_catalog['events'] if e['id'] == EVENT_ID)
        key = (DATA_SHA256, MANIFEST_SHA256)
        if _parsed_packet is None or _parsed_packet[0] != key:
            packet = json.loads(selected_raw[DATA])
            if not _valid_schema(packet, current): return None
            _parsed_packet = (key, _sha(_canonical(packet)), packet)
        elif _sha(_canonical(_parsed_packet[2])) != _parsed_packet[1]: return None
        packet = _parsed_packet[2]
        if not _valid_schema(packet, current): return None
        if not all(_same_json(packet[k], authority[k]) for k in ('expected_event','source','source_reference')): return None
        # A warm legacy catalog is a separate read; compare the complete object,
        # including descriptions, attributes, absent original IDs and all scenes.
        from . import node_catalog
        if not _same_json(node_catalog._event(EVENT_ID), packet['expected_event']): return None
        return deepcopy(packet)
    except (OSError, ValueError, TypeError, KeyError, AttributeError, IndexError, UnicodeError, StopIteration, RecursionError):
        return None


def source_data():
    """Freshly verified full fixed reference packet, or None."""
    return _verified_packet()


def _context(mode, difficulty):
    return {'mode': mode if type(mode) is str else None,
        'difficulty': difficulty if type(difficulty) is int else None, 'phase_reference_only': True}


def event_reference(event_id, *, mode=None, difficulty=None):
    """Manual next-region references; no actual phase or choice is inferred."""
    if type(event_id) is not str or event_id != EVENT_ID: return None
    context = _context(mode, difficulty)
    packet = _verified_packet()
    common = {'target': True, 'event_id': event_id, 'context': context,
        **{key: None for key in ACTUAL_FIELDS}, 'calculation_applied': False, 'run_state_updated': False}
    if packet is None:
        return {**common, 'source_valid': False, 'status': 'source_unavailable', 'event_title': None,
            'scope_key': None, 'choices': [], 'phases': [], 'documented_phase': None,
            'source': None, 'source_reference': None, 'source_identity': None,
            'supplemental_documentation': None,
            'source_notice': '下一区域效果资料暂时无法核对，请勿沿用旧效果。',
            'notice': '下一区域效果资料暂时无法核对；本局选择与生效情况仍未知。',
            'unknowns': ['本局选择、实际生效档位及战后随机零件仍未知']}
    phase = None
    if context['mode'] == 'NORMAL' and type(difficulty) is int and 2 <= difficulty <= 15:
        phase = 'early' if difficulty <= 5 else 'middle' if difficulty <= 11 else 'late'
    return {**common, 'source_valid': True, 'status': 'documented_reference',
        'event_title': packet['event_title'],
        'scope_key': EVENT_ID + ':' + DATA_SHA256 + ':' + MANIFEST_SHA256,
        'choices': packet['choices'], 'phases': packet['phases'], 'documented_phase': phase,
        'source': packet['source'], 'source_reference': packet['source_reference'],
        'source_identity': {'data_sha256': DATA_SHA256, 'manifest_sha256': MANIFEST_SHA256,
            'game_commit': packet['source']['game']['commit']},
        'source_notice': '固定原表与社区文献资料；尚未核实当前服务器及本局是否生效。',
        'supplemental_documentation': packet['supplemental_documentation'],
        'notice': packet['notice'], 'unknowns': packet['unknowns']}
