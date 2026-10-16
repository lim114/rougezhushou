"""Source-bound expedition choice/return reading, never actual run effects.

Only the fixed 未涉足之树 group is covered. Every public target query rehashes
all source bytes. Reused parsed objects are additionally checked for mutation.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
EVENT = 'community_group_024'
SCENE = EVENT + ':scene:0'
CHOICES = tuple(SCENE + ':choice:' + str(index) for index in range(3))
ROOT_CHOICE = CHOICES[1]
ANNOTATION_SCENE = EVENT + ':scene:2'
ANNOTATION_CHOICE = ANNOTATION_SCENE + ':choice:1'
ITEM = 'rogue_6_relic_final_3'
DATA = 'rouge/data/expedition-results.json'
MANIFEST = 'research/p3-expedition-results-297/source-manifest.json'
DATA_SHA256 = 'f83ca0ec16a24e634e48500186da6f6f7f3269092d51045d99779f1a9439d3ff'
MANIFEST_SHA256 = '5227f6fc7171430dc820668daf636489c72673d62a5f1e9b82d26d0021cf323e'
_parsed_packet = None


def _sha(raw): return hashlib.sha256(raw).hexdigest()
def _canonical(value): return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf8')


def _source_path(relative):
    if type(relative) is not str: raise ValueError('Source path must be text.')
    rel = PurePosixPath(relative)
    if rel.is_absolute() or '..' in rel.parts or '\\' in relative or ':' in relative:
        raise ValueError('Invalid source path.')
    path = ROOT.joinpath(*rel.parts)
    if not path.resolve().is_relative_to(ROOT.resolve()): raise ValueError('Source escaped the root.')
    return path


def _same_json(value, expected):
    if type(value) is not type(expected): return False
    if type(expected) is dict:
        return value.keys() == expected.keys() and all(type(key) is str and _same_json(value[key], expected[key]) for key in value)
    if type(expected) is list:
        return len(value) == len(expected) and all(_same_json(a, b) for a, b in zip(value, expected))
    return value == expected


def _valid_schema(packet, current):
    if (type(packet) is not dict or packet.get('schema') != 'expedition_results_reference_v1'
            or packet.get('event_id') != EVENT or packet.get('current_server_verified') is not False
            or packet.get('inventory_updated') is not False or packet.get('eligibility_evaluated') is not False
            or not _same_json(packet.get('expected_event'), current)):
        return False
    rows = packet['rows']
    if type(rows) is not list or len(rows) != 3: return False
    expected_ids = ('choice_ro6_scout_1', 'choice_ro6_scout_3', 'choice_ro6_scout_2')
    for index, row in enumerate(rows):
        choice = current['scenes'][0]['choices'][index]
        if ((row['event_id'], row['scene_key'], row['choice_key'], row['original_choice_id']) !=
                (EVENT, SCENE, CHOICES[index], expected_ids[index])
                or choice['game_choice_ids'] != [expected_ids[index]]
                or not _same_json(row['choice_title'], choice['title'])
                or not _same_json(row['choice_description'], choice['description'])
                or row['effect_phase_reference'] != ('on_choice' if index == 2 else 'on_return')
                or row['is_actual_button_reference'] is not True
                or any(row[key] is not None for key in ('actual_dispatched_operator', 'actual_returned',
                    'actual_reward','actual_quantity','actual_advanced','actual_return_clock','actual_selectable'))):
            return False
        if not _same_json(row['immediate_resource_references'], [{'resource':'hope','quantity_reference':2}] if index == 2 else []): return False
        if not _same_json(row['return_resource_references'], [{'resource':'hope','quantity_reference':2}] if index == 1 else []): return False
        if row['promotion_reference'] is not (False if index == 1 else None): return False
        if index == 2:
            if row['dispatch_reference'] is not None or row['documented_return_item'] is not None or row['beak_reference'] is not None: return False
        else:
            dispatch = row['dispatch_reference']
            if (type(dispatch['operator_count_reference']) is not int or dispatch['operator_count_reference'] != 1
                    or dispatch['temporarily_unavailable_for_squad'] is not True
                    or dispatch['special_region_equivalence'] is not None
                    or row['beak_reference']['applies_to_root_branch'] is not None): return False
    annotation = packet['return_explanatory_reference']; original = current['scenes'][2]['choices'][1]
    if ((annotation['event_id'], annotation['scene_key'], annotation['choice_key']) !=
            (EVENT, ANNOTATION_SCENE, ANNOTATION_CHOICE)
            or annotation['is_actual_button'] is not False or annotation['effect_phase'] != 'on_return'
            or annotation['presentation_role'] != 'explanatory_text'
            or not _same_json(annotation['description'], original['description'])
            or not _same_json(annotation['game_choice_ids'], original['game_choice_ids'])
            or annotation['source_dispatch_choice_key'] != ROOT_CHOICE): return False
    item = packet['item']; icon = packet['icon_reference']
    return (item['id'] == ITEM and item['type'] == 'RELIC' and item['iconId'] == ITEM
        and icon['file'] == 'rouge/data/relic-icons/' + ITEM + '.png'
        and icon['item_id'] == ITEM and icon['icon_id'] == ITEM
        and packet['source_reference']['original_return_item_pointer'] == ITEM)


def _verified_packet():
    global _parsed_packet
    try:
        raw_manifest = _source_path(MANIFEST).read_bytes()
        if _sha(raw_manifest) != MANIFEST_SHA256: return None
        manifest = json.loads(raw_manifest)
        if (manifest.get('schema') != 'expedition_results_source_manifest_v1'
                or manifest.get('data_file') != DATA or manifest.get('data_sha256') != DATA_SHA256
                or manifest.get('runtime_reads_primary_table') is not False): return None
        blobs = {}
        for name, pin in manifest['files'].items():
            raw = _source_path(name).read_bytes()
            if type(pin['bytes']) is not int or len(raw) != pin['bytes'] or _sha(raw) != pin['sha256']: return None
            blobs[name] = raw
        raw_data = blobs[DATA]
        if _sha(raw_data) != DATA_SHA256: return None
        current = next((row for row in json.loads(blobs['rouge/data/node-catalog.json'])['events']
                        if row.get('id') == EVENT), None)
        key = (MANIFEST_SHA256, DATA_SHA256)
        if _parsed_packet is None or _parsed_packet[0] != key:
            packet = json.loads(raw_data)
            if not _valid_schema(packet, current): return None
            _parsed_packet = (key, _sha(_canonical(packet)), packet)
        elif _sha(_canonical(_parsed_packet[2])) != _parsed_packet[1]:
            return None
        if not _valid_schema(_parsed_packet[2], current): return None
        return deepcopy(_parsed_packet[2])
    except (OSError, ValueError, TypeError, KeyError, AttributeError, IndexError, UnicodeError):
        return None


def source_data():
    """Return a validated independent copy; no caller-supplied data interface."""
    return _verified_packet()


def _unknown(kind, *, scene_key=None, choice_key=None):
    return {'status':'source_unavailable','source_valid':False,'reference_kind':kind,'event_id':EVENT,
        'scene_key':scene_key,'choice_key':choice_key,'rows':[], 'return_explanatory_reference':None,
        'item':None,'icon_reference':None,'source':None,'source_reference':None,'reference':None,
        'notice':'派出与归来资料暂时无法核对；旧结果及图片已清除。保留事件原文，时点和实际领取仍待确认。',
        'actual_dispatched_operator':None,'actual_returned':None,'actual_reward':None,
        'actual_quantity':None,'actual_advanced':None,'actual_return_clock':None,'actual_selectable':None,
        'current_server_verified':False,'inventory_updated':False,'eligibility_evaluated':False}


def event_reference(event_id):
    """Three exact documented choices; never a current run decision or grant."""
    if type(event_id) is not str or event_id != EVENT: return None
    packet = _verified_packet()
    if packet is None: return _unknown('expedition_choice_results')
    packet.update(status='documented_reference', source_valid=True)
    return packet


def _target_choice(event_id, scene_key, choice_key):
    return (type(event_id) is str and event_id == EVENT and type(scene_key) is str and scene_key == SCENE
            and type(choice_key) is str and choice_key in CHOICES)


def choice_reference(event_id, scene_key, choice_key):
    """An exact actual-choice reference, isolated from the explanatory note."""
    if not _target_choice(event_id, scene_key, choice_key): return None
    packet = _verified_packet()
    if packet is None: return _unknown('expedition_choice_result', scene_key=scene_key, choice_key=choice_key)
    row = next(row for row in packet['rows'] if row['choice_key'] == choice_key)
    row.update(status='documented_reference',source_valid=True,source=packet['source'],
               source_reference=packet['source_reference'],notice=packet['notice'])
    return row


def annotation_reference(event_id, scene_key, choice_key):
    """Only the exact return explanation; it never becomes an actual choice."""
    if (type(event_id) is not str or event_id != EVENT or type(scene_key) is not str or scene_key != ANNOTATION_SCENE
            or type(choice_key) is not str or choice_key != ANNOTATION_CHOICE): return None
    packet = _verified_packet()
    if packet is None: return _unknown('expedition_return_explanation', scene_key=scene_key, choice_key=choice_key)
    row = packet['return_explanatory_reference']
    row.update(status='documented_reference',source_valid=True,source=packet['source'],source_reference=packet['source_reference'])
    return row


def item_details(event_id, scene_key, choice_key):
    """Manually readable return item; it is not claimed or applied."""
    if not _target_choice(event_id, scene_key, choice_key) or choice_key != ROOT_CHOICE: return None
    packet = _verified_packet()
    if packet is None: return _unknown('expedition_return_item', scene_key=scene_key, choice_key=choice_key)
    return {'status':'documented_reference','source_valid':True,'reference_kind':'expedition_return_item',
        'event_id':EVENT,'scene_key':SCENE,'choice_key':ROOT_CHOICE,'reference':packet['rows'][1],
        'item':packet['item'],'icon_reference':packet['icon_reference'],'source':packet['source'],
        'source_reference':packet['source_reference'],'unlock_notice':packet['unlock_notice'],'notice':packet['notice'],
        'quantity_reference':None,'actual_reward':None,'actual_quantity':None,'actual_selectable':None,
        'actual_returned':None,'actual_advanced':None,'current_server_verified':False,
        'inventory_updated':False,'eligibility_evaluated':False}
