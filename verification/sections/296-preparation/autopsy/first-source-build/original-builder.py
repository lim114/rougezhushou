"""Build only the documented ro6_t_12 entry configuration from fixed originals.

This is a pure-file builder. It neither imports the product nor infers an
activation script. Runtime uses selected byte-exact values, not the large table.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
from pathlib import Path
import re

GAME_SHA = 'f5867e55d09472253083486174aa47bd94dd48b07684b74b60a5b29ca00eda86'
COMMUNITY_SHA = '366e0bf14b526816b20750f1d83b6c7b132d556dfc0b09a0ab3c302fd00610e9'
GAME_COMMIT = 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'
STAGE = 'ro6_t_12'
FEATURES = tuple('rogue_6_end_3_relic_trigger_' + str(n) for n in (1, 2, 3, 10))
ZONES = ('zone_3', 'zone_4', 'zone_5', 'zone_4_1')
USAGES = tuple('给' + part + '普通作战挂上狼兽主气泡' for part in ('3层', '4层', '5层', '假层'))
ITEMS = ('rogue_6_bubble_04', 'rogue_6_relic_final_5', 'rogue_6_relic_final_3')
PACKET = Path('research/p3-stage-entry-configuration-296')
DATA = Path('rouge/data/stage-entry-configuration-reference.json')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf8', newline='\n')


def skip_ws(raw, pos):
    while pos < len(raw) and raw[pos] in b' \t\r\n':
        pos += 1
    return pos


def string_end(raw, pos):
    if raw[pos] != 34:
        raise ValueError('Expected a JSON string.')
    pos += 1
    while pos < len(raw):
        if raw[pos] == 92:
            pos += 2
        elif raw[pos] == 34:
            return pos + 1
        else:
            pos += 1
    raise ValueError('Unterminated JSON string.')


def value_end(raw, pos):
    pos = skip_ws(raw, pos)
    if raw[pos] == 34:
        return string_end(raw, pos)
    if raw[pos] in (91, 123):
        closing = 93 if raw[pos] == 91 else 125
        pos += 1
        while pos < len(raw):
            pos = skip_ws(raw, pos)
            if raw[pos] == closing:
                return pos + 1
            if raw[pos] in (44, 58):
                pos += 1
            else:
                pos = value_end(raw, pos)
        raise ValueError('Unterminated JSON compound.')
    end = pos
    while end < len(raw) and raw[end] not in b',]} \t\r\n':
        end += 1
    if end == pos:
        raise ValueError('Missing JSON value.')
    return end


def member(raw, start, key):
    pos = skip_ws(raw, start)
    if raw[pos] != 123:
        raise ValueError('Expected a JSON object.')
    pos += 1
    found = None
    while True:
        pos = skip_ws(raw, pos)
        if raw[pos] == 125:
            break
        key_end = string_end(raw, pos)
        name = json.loads(raw[pos:key_end])
        pos = skip_ws(raw, key_end)
        if raw[pos] != 58:
            raise ValueError('Missing JSON member colon.')
        begin = skip_ws(raw, pos + 1)
        end = value_end(raw, begin)
        if name == key:
            if found is not None:
                raise ValueError('Duplicate selected JSON member.')
            found = (begin, end)
        pos = skip_ws(raw, end)
        if raw[pos] == 44:
            pos += 1
        elif raw[pos] != 125:
            raise ValueError('Missing JSON member separator.')
    if found is None:
        raise ValueError('Selected original member is missing: ' + key)
    return found


def selected_span(raw, path, spans):
    for length in range(1, len(path) + 1):
        prefix = path[:length]
        if prefix not in spans:
            spans[prefix] = member(raw, spans[path[:length - 1]][0], prefix[-1])
    return spans[path]


def exact_keys(value, keys):
    if type(value) is not dict or set(value) != set(keys):
        raise ValueError('Selected original parameter shape changed.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--game-source', required=True, type=Path)
    parser.add_argument('--community-source', required=True, type=Path)
    parser.add_argument('--output-root', required=True, type=Path)
    args = parser.parse_args()
    game_raw = args.game_source.read_bytes()
    community_raw = args.community_source.read_bytes()
    if sha(game_raw) != GAME_SHA or sha(community_raw) != COMMUNITY_SHA:
        raise ValueError('The complete fixed original does not match its recorded SHA256.')
    game = json.loads(game_raw)['details']['rogue_6']
    target = args.output_root.resolve()
    selected = {}
    index = []
    paths = [('stages', STAGE)]
    paths += [('items', key) for key in FEATURES]
    paths += [('relics', key) for key in FEATURES]
    paths += [('zones', key) for key in ZONES]
    paths += [(section, key) for key in ITEMS for section in ('items', 'relics')]
    paths += [('relicParams', key) for key in ITEMS[1:]]
    spans = {(): (0, len(game_raw))}
    for section, key in paths:
        original_path = ('details', 'rogue_6', section, key)
        begin, end = selected_span(game_raw, original_path, spans)
        raw = game_raw[begin:end]
        value = json.loads(raw)
        if value != game[section][key] or value['id'] != key:
            raise ValueError('Original bytes do not bind the exact selected object.')
        rel = PACKET / 'original-values' / (section + '--' + key + '.json')
        (target / rel).parent.mkdir(parents=True, exist_ok=True)
        (target / rel).write_bytes(raw)
        selected[(section, key)] = value
        index.append({'json_path': '$.' + '.'.join(original_path), 'file': rel.as_posix(),
                      'start_byte': begin, 'end_byte_exclusive': end,
                      'bytes': len(raw), 'sha256': sha(raw), 'complete_original_sha256': GAME_SHA})

    stage = selected[('stages', STAGE)]
    if stage['name'] != '无效验尸' or stage['levelId'] != 'Obt/Roguelike/RO6/level_rogue6_t-12' or stage['difficulty'] != 'NORMAL' or stage['linkedStageId'] != '' or stage['levelReplaceIds'] != []:
        raise ValueError('Do not add an emergency alias or change the exact original stage.')
    rows = []
    for i, (feature, zone, usage) in enumerate(zip(FEATURES, ZONES, USAGES)):
        item = selected[('items', feature)]
        relic = selected[('relics', feature)]
        if item['type'] != 'FEATURE' or item['usage'] != usage or type(relic['buffs']) is not list or len(relic['buffs']) != 1:
            raise ValueError('The complete original FEATURE or its Chinese floor wording changed.')
        buff = relic['buffs'][0]
        exact_keys(buff, ('key', 'blackboard'))
        if buff['key'] != 'zone_into_node_attach_buff' or type(buff['blackboard']) is not list or len(buff['blackboard']) != 6:
            raise ValueError('The original attachment configuration changed.')
        bb = {}
        for entry in buff['blackboard']:
            exact_keys(entry, ('key', 'value', 'valueStr'))
            if type(entry['key']) is not str or entry['key'] in bb or type(entry['value']) is not float:
                raise ValueError('Duplicate/untyped original blackboard entry.')
            bb[entry['key']] = entry
        expected = {'id': ITEMS[0], 'node': 'BATTLE_NORMAL', 'limit': None,
                    'zone_id': zone, 'not_hold_relic_id': ITEMS[1], 'stage_id': STAGE}
        exact_keys(bb, expected)
        for key, value in expected.items():
            if bb[key]['valueStr'] != value or (value is not None and type(bb[key]['valueStr']) is not str):
                raise ValueError('An exact stage/marker/node/zone/not-hold pointer changed.')
            if bb[key]['value'] != (1.0 if key == 'limit' else 0.0):
                raise ValueError('An exact numerical parameter changed.')
        zone_data = selected[('zones', zone)]
        if type(zone_data['isHiddenZone']) is not bool or zone_data['isHiddenZone'] is not False:
            raise ValueError('The selected zone flag changed; do not rename it a secret region.')
        floor = i + 3 if i < 3 else None
        rows.append({'feature_id': feature, 'feature_item': item, 'feature_relic': relic,
                     'zone': zone_data, 'source_usage': usage, 'main_floor_reference': floor,
                     'label': '第' + str(floor) + '层普通作战（配置资料）' if floor is not None else '原资料称假层（不推定主层或秘境）',
                     'node_type': 'BATTLE_NORMAL', 'node_type_name': '普通作战',
                     'marker_id': ITEMS[0], 'not_hold_item_id': ITEMS[1], 'configured_limit': bb['limit']['value'],
                     'configured_limit_is_actual_count': False,
                     'actual_feature_attached': None, 'actual_node_marked': None,
                     'actual_stage_replacement': None, 'actual_count': None})

    marker_item = selected[('items', ITEMS[0])]
    if marker_item['type'] != 'NODE_BUOY' or marker_item['name'] != '光明之末' or marker_item['usage'] != '这是它第一次踏上这片土地，亮出自己的利爪。\n持有“怦然信标”，可以获得削弱强敌的方法。':
        raise ValueError('The complete marker identity or wording changed.')
    if selected[('items', ITEMS[1])]['name'] != '湮没“光明”' or selected[('items', ITEMS[2])]['name'] != '怦然信标':
        raise ValueError('The two separate item identities changed.')

    # A complete original <li>, not a text search snippet or a guessed heading.
    needle = '<b>光明之末</b>'.encode('utf8')
    center = community_raw.index(needle)
    begin = community_raw.rfind(b'<li>', 0, center)
    end = community_raw.index(b'</li>', center) + len(b'</li>')
    fragment = community_raw[begin:end]
    text = html.unescape(re.sub('<[^>]+>', '', fragment.decode('utf8')))
    expected_text = '<光明之末>：未持有【湮没“光明”】时标记于普通【作战】：对战未名的荒原的无效验尸，完成后可以选择获得收藏品【湮没“光明”】。'
    if text != expected_text:
        raise ValueError('The exact complete community marker paragraph changed.')
    rel_fragment = PACKET / 'community-marker-original.html'
    (target / rel_fragment).write_bytes(fragment)
    community = {'community_revision': 433770, 'community_complete_sha256': COMMUNITY_SHA,
                 'community_complete_bytes': len(community_raw), 'start_byte': begin,
                 'end_byte_exclusive': end, 'fragment_sha256': sha(fragment),
                 'fragment_file': rel_fragment.as_posix(), 'text': text,
                 'url': 'https://prts.wiki/index.php?title=%E6%B2%89%E6%B2%A6%E8%80%85%E7%9A%84%E9%BB%91%E6%B5%81%E6%A0%91%E6%B5%B7&oldid=433770',
                 'role': 'community_description_not_activation_script',
                 'beacon_acquisition_implies_feature_attachment_proven': False,
                 'license': 'CC BY-NC-SA 4.0'}
    upstream = []
    def walk(value, path):
        if isinstance(value, dict):
            for key, child in value.items():
                walk(child, path + '.' + key)
        elif isinstance(value, list):
            for i, child in enumerate(value):
                walk(child, path + '[' + str(i) + ']')
        elif isinstance(value, str) and 'rogue_6_end_3_relic_trigger_' in value and not path.endswith(('.id', '.iconId')):
            upstream.append({'path': path, 'value': value})
    walk(game, '$.details.rogue_6')
    audit = {'scope': 'Literal string values only in the complete fixed $.details.rogue_6',
             'excluded_path_suffixes': ['.id', '.iconId'], 'matches': upstream,
             'actual_feature_acquisition': None, 'activation_script_recovered': False,
             'absence_is_not_engine_or_server_absence_proof': True}
    write_json(target / PACKET / 'topic-selected-index.json', index)
    write_json(target / PACKET / 'community-marker-extraction.json', community)
    write_json(target / PACKET / 'upstream-literal-audit.json', audit)

    packet = {'schema': 'stage_entry_configuration_reference_v1', 'reference_kind': 'documented_stage_entry_configuration',
              'stage': stage, 'rows': rows,
              'marker': {'item': marker_item, 'relic': selected[('relics', ITEMS[0])]},
              'not_hold_item': {'item': selected[('items', ITEMS[1])], 'relic': selected[('relics', ITEMS[1])], 'params': selected[('relicParams', ITEMS[1])]},
              'beacon_item': {'item': selected[('items', ITEMS[2])], 'relic': selected[('relics', ITEMS[2])], 'params': selected[('relicParams', ITEMS[2])]},
              'community_reference': community, 'upstream_reference': audit,
              'source': {'game_commit': GAME_COMMIT, 'game_table_sha256': GAME_SHA, 'game_table_bytes': len(game_raw),
                         'game_url': 'https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/' + GAME_COMMIT + '/zh_CN/gamedata/excel/roguelike_topic_table.json',
                         'community_revision': 433770, 'community_pinned_url': community['url'],
                         'scope': 'Fixed source configuration; not current-server or actual-run eligibility.',
                         'game_material_rights': '游戏原文、图片等版权属于鹰角网络及关联权利人。',
                         'community_license': 'CC BY-NC-SA 4.0'},
              'player_notice': '这些是资料中列出的节点配置，不表示本局已出现或一定出现。实际进入条件仍未完整核实。',
              'unknowns': ['机制物品如何获得、何时附着与执行，尚未取得完整依据。',
                           '本局是否已有光明之末标记、它位于哪个节点、实际进入与领取结果均未确认。',
                           '配置中的未持有湮没“光明”与数量参数，不等于已核实本局是否可进入，也不保证每层出现一场。',
                           '假层仅保留原资料称呼，不认作某一主层或秘境。'],
              'actual_eligibility': None, 'actual_node': None, 'actual_entry': None,
              'actual_reward': None, 'actual_count': None, 'complete_stage_floor_pool': None}
    write_json(target / DATA, packet)
    receipt = {'status': 'SOURCE_SELECTION_AND_DATA_BUILD_ONLY', 'complete_game_sha256': GAME_SHA,
               'complete_community_sha256': COMMUNITY_SHA, 'selected_complete_objects': len(index),
               'selected_object_byte_total': sum(x['bytes'] for x in index), 'feature_rows': len(rows),
               'runtime_main_floor_references': [r['main_floor_reference'] for r in rows],
               'upstream_non_self_literal_matches': len(upstream), 'data_sha256': sha((target / DATA).read_bytes()),
               'qt_or_product_tests': False, 'game_chat_private_operations': 0}
    write_json(target / PACKET / 'build-receipt.json', receipt)
    source_files = sorted(p for p in (target / PACKET).rglob('*') if p.is_file() and p.name != 'manifest.json')
    source_files.append(Path(__file__).resolve())
    manifest = {'schema': 'stage_entry_configuration_source_manifest_v1', 'source': packet['source'],
                'data_file': DATA.as_posix(), 'data_sha256': sha((target / DATA).read_bytes()),
                'files': {p.relative_to(target).as_posix(): {'sha256': sha(p.read_bytes()), 'bytes': p.stat().st_size} for p in source_files}}
    write_json(target / PACKET / 'manifest.json', manifest)
    print(json.dumps({**receipt, 'manifest_sha256': sha((target / PACKET / 'manifest.json').read_bytes())}, ensure_ascii=False))


if __name__ == '__main__':
    main()
