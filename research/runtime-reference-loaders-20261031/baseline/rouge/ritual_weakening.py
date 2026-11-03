"""Fixed ritual choices and boss-weakening documents; no execution or run writes."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
DATA = 'rouge/data/ritual-weakening.json'
MANIFEST = 'research/p3-ritual-weakening-302/source-manifest.json'
SELECTED_AUTHORITY = 'research/p3-ritual-weakening-302/selected-authority-records.json'
DATA_SHA256 = '3e0533e212927bd9b50dd8f4f183ca97c5c02187f396a20718b049d7b7951138'
MANIFEST_SHA256 = 'bb1ab31f0e41e7015d303368292d28a752f539e78f7b80be90329adb24f97182'
EVENT_ID = 'community_group_032'
CHOICE_KEYS = tuple(EVENT_ID + ':scene:' + str(s) + ':choice:' + str(c) for s in (2, 3, 4) for c in (0, 1))
ACTUAL_FIELDS = ('actual_choice', 'actual_weakening', 'actual_attached', 'actual_inventory',
                 'actual_consumed', 'actual_effect', 'actual_numeric_result', 'actual_eligible')


def _same_json(value, expected):
    if type(value) is not type(expected): return False
    if type(expected) is dict:
        return value.keys() == expected.keys() and all(type(k) is str and _same_json(value[k], expected[k]) for k in value)
    if type(expected) is list:
        return len(value) == len(expected) and all(_same_json(a, b) for a, b in zip(value, expected))
    return value == expected


def _source_path(relative):
    if type(relative) is not str: raise ValueError('Fixed source path must be text.')
    path = PurePosixPath(relative)
    if path.is_absolute() or '..' in path.parts or '\\' in relative or ':' in relative:
        raise ValueError('Invalid fixed source path.')
    result = ROOT.joinpath(*path.parts)
    if result.is_symlink() or not result.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError('Fixed source escaped root.')
    return result


def _valid_packet(packet, authority, current):
    if packet['schema'] != 'ritual_weakening_v1' or authority['schema'] != 'ritual_weakening_selected_authority_v1': return False
    if packet['event_id'] != authority['event_id'] or packet['event_id'] != EVENT_ID or packet['event_title'] != '调谐仪式': return False
    if not _same_json(packet['expected_event'], authority['expected_event']) or not _same_json(current, authority['expected_event']): return False
    if not _same_json(packet['source'], authority['source']): return False
    if packet['current_server_verified'] is not False or packet['original_entry_restored'] is not False: return False
    if packet['calculation_applied'] is not False or packet['run_state_updated'] is not False: return False
    if any(packet[k] is not None for k in ACTUAL_FIELDS): return False
    rows, effects = packet['choices'], packet['weakening_references']
    if type(rows) is not list or [r['choice_key'] for r in rows] != list(CHOICE_KEYS): return False
    if type(effects) is not list or [e['weakening_id'] for e in effects] != [
            'rogue_6_chimera_weaken_1', 'rogue_6_chimera_weaken_3', 'rogue_6_chimera_weaken_2']: return False
    for row in rows:
        if row['event_id'] != EVENT_ID or row['reference_id'] != row['choice_key'] or row['scene_key'] != row['choice_key'].rsplit(':choice:', 1)[0]: return False
        scene = next(s for s in current['scenes'] if s['key'] == row['scene_key'])
        choice = next(c for c in scene['choices'] if c['key'] == row['choice_key'])
        if not _same_json(choice, row['catalog_choice']): return False
        if not _same_json(row['original_choice'], authority['complete_original_choices'][row['original_choice_id']]): return False
        if choice['game_choice_ids'] != [row['original_choice_id']]: return False
        if row['original_choice']['displayData']['itemId'] != row['weakening_id']: return False
        if not _same_json(row['feature_reference'], authority['complete_features'][row['weakening_id']]): return False
        if not _same_json(row['related_stage_reference'], packet['related_stage_reference']): return False
        if any(row[k] is not None for k in ACTUAL_FIELDS): return False
        if row['submission_reference']['quantity_reference'] is not None: return False
        if row['calculation_applied'] is not False or row['run_state_updated'] is not False: return False
    related = packet['related_stage_reference']
    if related['stage_id'] != 'ro6_b_6' or related['title'] != '畸症' or related['reference_only'] is not True or related['immediate_transition'] is not None: return False
    if related['enemy_selector'] != 'enemy_2150_shchmr' or related['enemy_level_reference'] is not None: return False
    if not _same_json(related['original_stage'], authority['complete_related_stage']): return False
    for effect in effects:
        if not _same_json(effect['feature_reference'], authority['complete_features'][effect['weakening_id']]): return False
        if any(effect[k] is not None for k in ACTUAL_FIELDS): return False
    return True


def _verified_packet():
    # Fresh small complete records are decoded on each call. There is deliberately
    # no module snapshot cache whose expected object could be altered alongside it.
    try:
        manifest_raw = _source_path(MANIFEST).read_bytes()
        if sha256(manifest_raw).hexdigest() != MANIFEST_SHA256: return None
        manifest = json.loads(manifest_raw)
        if (manifest['schema'] != 'ritual_weakening_source_manifest_v1' or manifest['event_id'] != EVENT_ID
                or manifest['data_file'] != DATA or manifest['data_sha256'] != DATA_SHA256
                or manifest['selected_authority_file'] != SELECTED_AUTHORITY
                or manifest['runtime_reads_complete_primary_table'] is not False
                or manifest['runtime_verifies_complete_original_bytes'] is not False
                or manifest['all_runtime_members_required_for_each_target_query'] is not True): return None
        selected = {}
        for relative, pin in manifest['runtime_files'].items():
            if not _same_json(pin, manifest['files'][relative]): return None
            raw = _source_path(relative).read_bytes()
            if type(pin['bytes']) is not int or len(raw) != pin['bytes'] or sha256(raw).hexdigest() != pin['sha256']: return None
            if relative in (DATA, SELECTED_AUTHORITY, 'rouge/data/node-catalog.json'): selected[relative] = raw
        if sha256(selected[DATA]).hexdigest() != DATA_SHA256: return None
        packet = json.loads(selected[DATA])
        authority = json.loads(selected[SELECTED_AUTHORITY])
        current = next(e for e in json.loads(selected['rouge/data/node-catalog.json'])['events'] if e['id'] == EVENT_ID)
        if not _valid_packet(packet, authority, current): return None
        # Legacy callers can hold a warm catalog. Compare the complete typed event
        # to the independently byte-pinned fresh records, including descriptions.
        from . import node_catalog
        if not _same_json(node_catalog._event(EVENT_ID), current): return None
        return deepcopy(packet)
    except (OSError, ValueError, TypeError, KeyError, AttributeError, IndexError, UnicodeError, StopIteration, RecursionError):
        return None


def source_data():
    """Fresh fixed packet or None. No source, evaluator or state injection API."""
    return _verified_packet()


def _actual_unknown():
    return {**{key: None for key in ACTUAL_FIELDS}, 'calculation_applied': False, 'run_state_updated': False}


def event_reference(event_id):
    if type(event_id) is not str or event_id != EVENT_ID: return None
    packet = _verified_packet()
    base = {'target': True, 'event_id': EVENT_ID, **_actual_unknown()}
    if packet is None:
        return {**base, 'source_valid': False, 'status': 'source_unavailable', 'event_title': None,
                'scope_key': None, 'choices': [], 'weakening_references': [], 'related_stage_reference': None,
                'source': None, 'source_reference': None, 'source_identity': None,
                'notice': '调谐仪式资料暂时无法核对，请勿沿用旧的选项与首领削弱关系。',
                'unknowns': ['本局选择、库存、实际交付、附着及生效情况仍未知']}
    return {**base, 'source_valid': True, 'status': 'documented_reference',
            'event_title': packet['event_title'], 'scope_key': EVENT_ID + ':' + DATA_SHA256 + ':' + MANIFEST_SHA256,
            'choices': packet['choices'], 'weakening_references': packet['weakening_references'],
            'related_stage_reference': packet['related_stage_reference'],
            'source': packet['source'], 'source_reference': packet['source_reference'],
            'source_identity': {'data_sha256': DATA_SHA256, 'manifest_sha256': MANIFEST_SHA256,
                                'game_commit': packet['source']['game']['commit']},
            'notice': packet['notice'], 'unknowns': packet['unknowns']}


def weakening_details(event_id, scene_key, choice_key):
    if type(event_id) is not str or event_id != EVENT_ID or type(scene_key) is not str or type(choice_key) is not str: return None
    if choice_key not in CHOICE_KEYS or scene_key != choice_key.rsplit(':choice:', 1)[0]: return None
    packet = _verified_packet()
    base = {'target': True, 'event_id': EVENT_ID, **_actual_unknown()}
    if packet is None:
        return {**base, 'source_valid': False, 'status': 'source_unavailable', 'reference': None,
                'weakening_reference': None, 'related_stage_reference': None, 'source': None, 'source_reference': None,
                'notice': '调谐仪式资料暂时无法核对，请勿沿用旧结果。'}
    row = next(r for r in packet['choices'] if r['choice_key'] == choice_key)
    effect = next(e for e in packet['weakening_references'] if e['weakening_id'] == row['weakening_id'])
    return {**base, 'source_valid': True, 'status': 'documented_reference', 'reference': row,
            'weakening_reference': effect, 'related_stage_reference': packet['related_stage_reference'],
            'source': packet['source'], 'source_reference': packet['source_reference'], 'notice': packet['notice']}
