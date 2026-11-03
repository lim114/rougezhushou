"""Fixed choice-specific node documents; never mutate a run or infer live nodes."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
PACK = 'research/p3-curiosity-node-rules-304'
DATA = 'rouge/data/curiosity-node-rules.json'
MANIFEST = PACK + '/source-manifest.json'
SELECTED_AUTHORITY = PACK + '/selected-authority-records.json'
RULE_MAP = PACK + '/choice-rule-map.json'
# Filled only from the actual reproducible cache source-build before READY.
DATA_SHA256 = '62529af5ba7f4c30bc57c95a98b03c4457f7426cd6d5bb49efd3abaee325285a'
MANIFEST_SHA256 = '6e4bddeef0ba5913504725d2f235f5384e8f7d1b51c1e89d6de5b7d977304237'
EVENT_IDS = ('community_group_030', 'community_group_031')
CHOICE_IDENTITIES = (
    ('community_group_030', 'community_group_030:scene:0', 'community_group_030:scene:0:choice:0'),
    ('community_group_030', 'community_group_030:scene:0', 'community_group_030:scene:0:choice:1'),
    ('community_group_031', 'community_group_031:scene:0', 'community_group_031:scene:0:choice:0'),
    ('community_group_031', 'community_group_031:scene:0', 'community_group_031:scene:0:choice:1'),
    ('community_group_031', 'community_group_031:scene:2', 'community_group_031:scene:2:choice:0'),
)
ORIGINAL_IDS = (
    ('choice_ro6_end1_1',), ('choice_ro6_end1_2',),
    ('choice_ro6_end2_1', 'choice_ro6_end2_4'), ('choice_ro6_end2_2',), ('choice_ro6_end2_3',),
)
RELATED_CHOICES = (CHOICE_IDENTITIES[2][2], CHOICE_IDENTITIES[4][2])
RELATED_STAGE_REFERENCE = {'stage_id': 'ro6_b_5', 'title': '混沌源阶理论',
                           'reference_only': True, 'immediate_transition': None}
ACTUAL_FIELDS = ('actual_choice', 'actual_node_id', 'actual_marker', 'actual_transformation',
                 'actual_revisit', 'actual_consumed', 'actual_reward', 'actual_quantity', 'actual_eligible')


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


def _actual_unknown():
    return {**{key: None for key in ACTUAL_FIELDS}, 'inventory_updated': False,
            'calculation_applied': False, 'run_state_updated': False}


def _valid_unknowns(value):
    return all(value[k] is None for k in ACTUAL_FIELDS) and all(
        value[k] is False for k in ('inventory_updated', 'calculation_applied', 'run_state_updated'))


def _valid_packet(packet, authority, rules, current_events):
    if packet['schema'] != 'curiosity_node_rules_v1' or rules['schema'] != 'curiosity_node_choice_rule_map_v1': return False
    if packet['event_ids'] != list(EVENT_IDS): return False
    if not _same_json(packet['expected_events'], authority['complete_current_events']): return False
    if not _same_json(current_events, authority['complete_current_events']): return False
    if not _valid_unknowns(packet) or packet['current_server_verified'] is not False or packet['original_entry_restored'] is not False: return False
    context = packet['node_context_reference']
    if not _same_json(context, rules['node_context_reference']): return False
    if type(context['documented_main_floor']) is not int or context['documented_main_floor'] != 5 or context['actual_node_ids'] is not None: return False
    if type(context['texts']) is not list or not context['texts'] or any(type(v) is not str for v in context['texts']): return False
    for key in ('source', 'source_reference', 'notice', 'unknowns'):
        if not _same_json(packet[key], rules[key]): return False
    rows = packet['choices']
    if type(rows) is not list or len(rows) != len(CHOICE_IDENTITIES) or len(rules['choices']) != len(rows): return False
    if not _same_json(packet['complete_original_choices'], authority['complete_original_choices']): return False
    if not _same_json(packet['complete_original_scenes'], authority['complete_original_scenes']): return False
    if not _same_json(packet['configuration_references'], {'items': authority['complete_items'], 'relics': authority['complete_relics'],
                                                        'related_stage': authority['complete_related_stage']}): return False
    for row, rule, identity, expected_ids in zip(rows, rules['choices'], CHOICE_IDENTITIES, ORIGINAL_IDS):
        event_id, scene_key, choice_key = identity
        if (row['event_id'], row['scene_key'], row['choice_key']) != identity or row['reference_id'] != choice_key: return False
        scene = next(s for s in current_events[event_id]['scenes'] if s['key'] == scene_key)
        choice = next(c for c in scene['choices'] if c['key'] == choice_key)
        if not _same_json(row['catalog_choice'], choice) or row['original_choice_ids'] != list(expected_ids): return False
        if not _same_json(choice['game_choice_ids'], list(expected_ids)): return False
        originals = {key: authority['complete_original_choices'][key] for key in expected_ids}
        if not _same_json(row['original_choices'], originals): return False
        if row['original_choice_candidate_selection_unknown'] is not (len(expected_ids) > 1): return False
        if row['scene_number'] != current_events[event_id]['scenes'].index(scene) + 1 or row['choice_number'] != scene['choices'].index(choice) + 1: return False
        if type(row['scene_number']) is not int or type(row['choice_number']) is not int: return False
        for key in ('event_id', 'scene_key', 'choice_key', 'reference_id', 'choice_title', 'choice_description',
                    'condition_text', 'original_choice_ids', 'documented_rules', 'related_stage_reference'):
            if not _same_json(row[key], rule[key]): return False
        if row['choice_title'] != choice['title'] or row['choice_description'] != choice['description'] or row['condition_text'] != choice['conditional']: return False
        entries = row['documented_rules']
        if type(entries) is not list or not entries or len({v['rule_id'] for v in entries}) != len(entries): return False
        for item in entries:
            if set(item) != {'rule_id', 'title', 'text', 'source_refs'}: return False
            if any(type(item[k]) is not str or not item[k] for k in ('rule_id', 'title', 'text')): return False
            if type(item['source_refs']) is not list or not item['source_refs']: return False
        expected_stage = RELATED_STAGE_REFERENCE if choice_key in RELATED_CHOICES else None
        if not _same_json(row['related_stage_reference'], expected_stage) or not _valid_unknowns(row): return False
    # The shared title is not a reason to merge distinct primary records.
    protection = rows[2]['original_choices']
    if protection['choice_ro6_end2_1']['displayData']['itemId'] != 'rogue_6_end_2_change': return False
    if protection['choice_ro6_end2_4']['displayData']['itemId'] is not None: return False
    return authority['complete_related_stage']['id'] == 'ro6_b_5'


def _verified_packet():
    # No mutable decoded snapshot is cached: every target query independently
    # checks current bytes and parses the small complete authority records.
    try:
        manifest_raw = _source_path(MANIFEST).read_bytes()
        if sha256(manifest_raw).hexdigest() != MANIFEST_SHA256: return None
        manifest = json.loads(manifest_raw)
        if (manifest['schema'] != 'curiosity_node_rules_source_manifest_v1' or manifest['event_ids'] != list(EVENT_IDS)
                or manifest['data_file'] != DATA or manifest['data_sha256'] != DATA_SHA256
                or manifest['selected_authority_file'] != SELECTED_AUTHORITY or manifest['rule_map_file'] != RULE_MAP
                or manifest['runtime_reads_complete_primary_table'] is not False
                or manifest['all_runtime_members_required_for_each_target_query'] is not True): return None
        required = {DATA, SELECTED_AUTHORITY, RULE_MAP, 'rouge/data/node-catalog.json'}
        if not required.issubset(manifest['runtime_files']): return None
        selected = {}
        for relative, expected in manifest['runtime_files'].items():
            if not _same_json(expected, manifest['files'][relative]): return None
            raw = _source_path(relative).read_bytes()
            if type(expected['bytes']) is not int or len(raw) != expected['bytes'] or sha256(raw).hexdigest() != expected['sha256']: return None
            if relative in required: selected[relative] = raw
        if sha256(selected[DATA]).hexdigest() != DATA_SHA256: return None
        packet = json.loads(selected[DATA]); authority = json.loads(selected[SELECTED_AUTHORITY]); rules = json.loads(selected[RULE_MAP])
        catalog = json.loads(selected['rouge/data/node-catalog.json'])
        current = {key: next(e for e in catalog['events'] if e['id'] == key) for key in EVENT_IDS}
        if not _valid_packet(packet, authority, rules, current): return None
        # Do not trust a previously returned or mutated legacy catalog object.
        from . import node_catalog
        if any(not _same_json(node_catalog._event(key), current[key]) for key in EVENT_IDS): return None
        return deepcopy(packet)
    except (OSError, ValueError, TypeError, KeyError, AttributeError, IndexError, UnicodeError, StopIteration, RecursionError):
        return None


def source_data():
    """Fresh complete fixed packet or None. No state/evaluator/source argument."""
    return _verified_packet()


def event_reference(event_id):
    if type(event_id) is not str or event_id not in EVENT_IDS: return None
    packet = _verified_packet()
    base = {'target': True, 'event_id': event_id, **_actual_unknown()}
    if packet is None:
        return {**base, 'status': 'source_unavailable', 'source_valid': False, 'event_title': None,
                'scope_key': None, 'choices': [], 'node_context_reference': None, 'source': None,
                'source_reference': None, 'source_identity': None,
                'notice': '命运所指的补充说明暂时无法核对，已清除旧的节点变化与再访资料。',
                'unknowns': ['本局节点、标记、选择、消耗、发生与实际奖励仍未确认。']}
    return {**base, 'status': 'documented_reference', 'source_valid': True,
            'event_title': packet['expected_events'][event_id]['title'],
            'scope_key': event_id + ':' + DATA_SHA256 + ':' + MANIFEST_SHA256,
            'choices': [row for row in packet['choices'] if row['event_id'] == event_id],
            'node_context_reference': packet['node_context_reference'], 'source': packet['source'],
            'source_reference': packet['source_reference'],
            'source_identity': {'data_sha256': DATA_SHA256, 'manifest_sha256': MANIFEST_SHA256},
            'notice': packet['notice'], 'unknowns': packet['unknowns']}


def choice_reference(event_id, scene_key, choice_key):
    if any(type(value) is not str for value in (event_id, scene_key, choice_key)): return None
    if (event_id, scene_key, choice_key) not in CHOICE_IDENTITIES: return None
    packet = _verified_packet()
    base = {'target': True, 'event_id': event_id, **_actual_unknown()}
    if packet is None:
        return {**base, 'status': 'source_unavailable', 'source_valid': False, 'reference': None,
                'related_stage_reference': None, 'node_context_reference': None,
                'source': None, 'source_reference': None, 'source_identity': None,
                'notice': '该选项的补充说明暂时无法核对，已清除旧资料。'}
    row = next(row for row in packet['choices'] if (row['event_id'], row['scene_key'], row['choice_key']) == (event_id, scene_key, choice_key))
    return {**base, 'status': 'documented_reference', 'source_valid': True, 'reference': row,
            'related_stage_reference': row['related_stage_reference'],
            'node_context_reference': packet['node_context_reference'],
            'source': packet['source'], 'source_reference': packet['source_reference'],
            'source_identity': {'data_sha256': DATA_SHA256, 'manifest_sha256': MANIFEST_SHA256},
            'notice': packet['notice']}
