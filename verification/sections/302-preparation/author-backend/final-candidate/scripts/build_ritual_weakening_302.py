"""Rebuild complete fixed ritual records. Default verifies bytes; --write rebuilds.

No application, Qt, network, run, game or chat APIs are imported.
"""
import argparse
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PACK = 'research/p3-ritual-weakening-302'
CONFIG = PACK + '/fixed-build-inputs.json'
SELECTED = PACK + '/selected-authority-records.json'
DATA = 'rouge/data/ritual-weakening.json'
MANIFEST = PACK + '/source-manifest.json'
EVENT_ID = 'community_group_032'
COMMIT = 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'
ACTUAL_FIELDS = ('actual_choice', 'actual_weakening', 'actual_attached', 'actual_inventory',
                 'actual_consumed', 'actual_effect', 'actual_numeric_result', 'actual_eligible')
GROUPS = ((2, (3, 4), 1), (3, (6, 7), 3), (4, (9, 10), 2))
SOURCE_FILES = {
    'research/p3-future-region-effects-300/game-topic-complete.json': 'f5867e55d09472253083486174aa47bd94dd48b07684b74b60a5b29ca00eda86',
    'research/p3-stage-context/community-main.html': '366e0bf14b526816b20750f1d83b6c7b132d556dfc0b09a0ab3c302fd00610e9',
    'research/p3-choice-recruitment-290/prts-events-427904.html': 'faa088b0474e75806b357df8648c6a59b1be6dcbc9be749db7c934ca9e6307e9',
    'research/p3-choice-recruitment-290/prts-events-440271.html': 'e04971ad361436e5bb3721883423d98ad66636d5156794dd6221a977ffd6dac8',
    'rouge/data/node-catalog.json': '7df1d94bb69650eb19fc811af661e54d44bf07d72b1c0793de511adc1b2e915d',
    'rouge/node_catalog.py': '438f393aa5016ea1bb17df7e0489c870d17371d4d478f7c7d6d9f77039cbe5d0',
}


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf8')


def pin(raw): return {'sha256': sha256(raw).hexdigest(), 'bytes': len(raw)}


class Node:
    def __init__(self, tag, attrs):
        self.tag, self.attrs, self.children = tag, dict(attrs), []


class Document(HTMLParser):
    VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}

    def __init__(self, raw):
        super().__init__(convert_charrefs=True)
        self.nodes, self.stack = [], [Node('root', [])]
        self.feed(raw.decode('utf8'))

    def handle_starttag(self, tag, attrs):
        n = Node(tag, attrs)
        self.nodes.append(n)
        self.stack[-1].children.append(n)
        if tag not in self.VOID: self.stack.append(n)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID: self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                break

    def handle_data(self, value): self.stack[-1].children.append(value)


def descendants(node):
    for child in node.children:
        if isinstance(child, Node):
            yield child
            yield from descendants(child)


def has_class(node, name): return name in node.attrs.get('class', '').split()


def tree(node):
    if isinstance(node, str): return node
    return {'tag': node.tag, 'attributes': node.attrs, 'children': [tree(c) for c in node.children]}


def text(node):
    if isinstance(node, str): return node
    return ''.join(text(c) + ('\n' if isinstance(c, Node) and c.tag in ('br', 'p', 'li') else '') for c in node.children)


def plain(value): return re.sub(r'<[^>]*>', '', value)


def reconstruct():
    config_raw = (ROOT / CONFIG).read_bytes()
    config = json.loads(config_raw)
    assert config['schema'] == 'ritual_weakening_build_inputs_v1' and config['game_commit'] == COMMIT
    assert set(config['sources']) == set(SOURCE_FILES)
    raws = {}
    for relative, digest in SOURCE_FILES.items():
        raw = (ROOT / relative).read_bytes()
        assert pin(raw) == config['sources'][relative] and pin(raw)['sha256'] == digest, relative
        raws[relative] = raw
    game_file = 'research/p3-future-region-effects-300/game-topic-complete.json'
    game = json.loads(raws[game_file])['details']['rogue_6']
    catalog = json.loads(raws['rouge/data/node-catalog.json'])
    event = next(e for e in catalog['events'] if e['id'] == EVENT_ID)
    assert event['title'] == '调谐仪式' and len(event['scenes']) == 6
    doms = {}
    for revision in ('427904', '440271'):
        relative = 'research/p3-choice-recruitment-290/prts-events-' + revision + '.html'
        document = Document(raws[relative])
        matches = []
        for n in document.nodes:
            if not has_class(n, 'IS-event-data'): continue
            scenes = [c for c in descendants(n) if has_class(c, 'scene')]
            if scenes and scenes[0].attrs.get('data-index') == '164': matches.append((n, scenes))
        assert len(matches) == 1, revision
        group, scenes = matches[0]
        assert len(scenes) == len(event['scenes'])
        for n, scene in zip(scenes, event['scenes']):
            assert n.attrs == scene['attributes']
            choices = [c for c in descendants(n) if has_class(c, 'choose')]
            assert len(choices) == len(scene['choices'])
            assert all(c.attrs == row['attributes'] for c, row in zip(choices, scene['choices']))
        doms[revision] = {'file': relative, 'revision': revision, 'complete_DOM': tree(group), 'text': text(group)}
    document = Document(raws['research/p3-stage-context/community-main.html'])
    endings = [n for n in document.nodes if has_class(n, 'AKCollapse-content')
               and len([c for c in descendants(n) if has_class(c, 'end_title')]) == 1
               and any(has_class(c, 'end3') for c in descendants(n) if has_class(c, 'end_title'))]
    assert len(endings) == 1
    ending = {'file': 'research/p3-stage-context/community-main.html', 'revision': '433770',
              'complete_DOM': tree(endings[0]), 'text': text(endings[0])}
    effect_sources = {
        1: '提交【击坠“神明”】后，首次释放的灾厄之口不会摧毁“危朽”。',
        3: '提交【焚毁“文明”】后，灾厄之口释放时不会封锁待部署区。',
        2: '提交【湮没“光明”】后，灾厄之口的伤害降低。',
    }
    assert all(s in ending['text'] for s in effect_sources.values())
    assert '使用【源私钥】可以作弊以替换上述任一需求。' in ending['text']
    stage = game['stages']['ro6_b_6']
    assert stage['id'] == 'ro6_b_6' and stage['name'] == '畸症'
    assert sum(s['name'] == '畸症' for s in game['stages'].values()) == 1
    related = {'stage_id': 'ro6_b_6', 'title': '畸症', 'reference_only': True,
               'immediate_transition': None, 'enemy_selector': 'enemy_2150_shchmr',
               'enemy_level_reference': None, 'original_stage': stage,
               'notice': '相关固定作战资料；不表示选择后立即开战，也不表示本局已经削弱首领。'}
    effects = []
    originals = {}
    rows = []
    required_names = {1: '击坠“神明”', 3: '焚毁“文明”', 2: '湮没“光明”'}
    effect_texts = {1: '首次释放灾厄之口时，不会摧毁“危朽”（可部署高台干员的地块）。',
                    3: '灾厄之口释放时，不再封锁待部署区。', 2: '灾厄之口的伤害降低。'}
    effect_keys = {1: 'enemy_shchmr_no_fire_mode_1', 3: 'enemy_shchmr_reborn_no_card',
                   2: 'enemy_shchmr_reborn_damage'}
    for step, (scene_index, choice_numbers, weaken_index) in enumerate(GROUPS, 1):
        feature_id = 'rogue_6_chimera_weaken_' + str(weaken_index)
        item, relic = game['items'][feature_id], game['relics'][feature_id]
        assert item['id'] == relic['id'] == feature_id and item['type'] == 'FEATURE'
        assert len(relic['buffs']) == 1 and relic['buffs'][0]['key'] == 'global_buff_normal'
        blackboard = relic['buffs'][0]['blackboard']
        assert next(b['valueStr'] for b in blackboard if b['key'] == 'key') == effect_keys[weaken_index]
        assert next(b['valueStr'] for b in blackboard if b['key'] == 'selector.enemy') == 'enemy_2150_shchmr'
        configuration = None
        if weaken_index == 2:
            assert next(b['value'] for b in blackboard if b['key'] == 'damage_scale') == 0.5
            configuration = {'key': 'damage_scale', 'value': 0.5, 'numerical_execution_verified': False,
                             'notice': '原表配置参数，仅供资料核对；不能由此认定本局实际伤害或完整换算。'}
        feature = {'item': item, 'relic': relic, 'selector': 'enemy_2150_shchmr',
                   'blackboard': blackboard, 'configuration_reference': configuration}
        effect = {'weakening_id': feature_id, 'ritual_step': step, 'title': effect_texts[weaken_index],
                  'effect_text': effect_texts[weaken_index], 'effect_source_text': effect_sources[weaken_index],
                  'feature_reference': feature, 'configuration_reference': configuration,
                  'related_stage_reference': related, **{k: None for k in ACTUAL_FIELDS}}
        effects.append(effect)
        scene = event['scenes'][scene_index]
        for local_index, number in enumerate(choice_numbers):
            original_id = 'choice_ro6_end3_' + str(number)
            original = game['choices'][original_id]
            choice = scene['choices'][local_index]
            assert choice['game_choice_ids'] == [original_id]
            assert original['displayData']['itemId'] == feature_id
            assert original['title'] == choice['title'] and plain(original['description']) == choice['description']
            name = '源私钥' if local_index else required_names[weaken_index]
            assert plain(original['description']).startswith('交出' + name + '，')
            originals[original_id] = original
            condition_text = '交出【' + name + '】。' + ('它可替代本步骤所需的【' + required_names[weaken_index] + '】。' if local_index else '')
            rows.append({'reference_id': choice['key'], 'event_id': EVENT_ID, 'scene_key': scene['key'],
                         'choice_key': choice['key'], 'choice_title': choice['title'],
                         'choice_description': choice['description'], 'source_text': original['description'],
                         'scene_title': scene['attributes']['data-nav'], 'ritual_step': step,
                         'condition_text': condition_text, 'effect_text': effect_texts[weaken_index],
                         'effect_source_text': effect_sources[weaken_index], 'weakening_id': feature_id,
                         'original_choice_id': original_id, 'catalog_choice': choice, 'original_choice': original,
                         'submission_reference': {'name': name, 'is_alternative': bool(local_index),
                                                  'quantity_reference': None, 'source_text': original['description']},
                         'feature_reference': feature, 'related_stage_reference': related,
                         'calculation_applied': False, 'run_state_updated': False,
                         **{k: None for k in ACTUAL_FIELDS}})
    complete_scenes = {sid: game['choiceScenes'][sid] for scene in event['scenes'] for sid in scene['game_scene_ids']}
    source = {'game': {'repository': 'Kengxxiao/ArknightsGameData', 'commit': COMMIT,
                       'file': game_file, 'sha256': SOURCE_FILES[game_file],
                       'record_path': 'details.rogue_6'},
              'community_events': [{'revision': revision, 'file': doms[revision]['file'],
                                    'url': 'https://prts.wiki/index.php?oldid=' + revision} for revision in doms],
              'community_ending': {'revision': '433770', 'file': ending['file'],
                                   'url': 'https://prts.wiki/index.php?oldid=433770'},
              'catalog': {'file': 'rouge/data/node-catalog.json', 'sha256': SOURCE_FILES['rouge/data/node-catalog.json']}}
    authority = {'schema': 'ritual_weakening_selected_authority_v1', 'event_id': EVENT_ID,
                 'expected_event': event, 'complete_original_choices': originals,
                 'complete_original_scenes': complete_scenes,
                 'complete_features': {e['weakening_id']: e['feature_reference'] for e in effects},
                 'complete_related_stage': stage, 'event_complete_DOMs': doms,
                 'main_complete_ending_block': ending, 'source': source}
    data = {'schema': 'ritual_weakening_v1', 'event_id': EVENT_ID, 'event_title': event['title'],
            'expected_event': event, 'choices': rows, 'weakening_references': effects,
            'related_stage_reference': related, 'source': source,
            'source_reference': {'event_id': EVENT_ID, 'choice_keys': [r['choice_key'] for r in rows],
                                 'weakening_order': [e['weakening_id'] for e in effects],
                                 'community_ending_revision': '433770'},
            'current_server_verified': False, 'original_entry_restored': False,
            'calculation_applied': False, 'run_state_updated': False,
            'notice': '固定资料说明交付选项与首领削弱的对应；本局能否选择、是否持有、实际交付、附着与生效仍未知。',
            'unknowns': ['本局选项资格、库存与交付情况', '机制物品是否实际附着及执行', '伤害参数的实际换算、热更新与当前服务器适用性'],
            **{k: None for k in ACTUAL_FIELDS}}
    result = {DATA: encoded(data), SELECTED: encoded(authority)}
    files = {**config['sources'], CONFIG: pin(config_raw)}
    for name in ('README.md', 'SCHEMA.md'):
        relative = PACK + '/' + name
        files[relative] = pin((ROOT / relative).read_bytes())
    files.update({name: pin(raw) for name, raw in result.items()})
    build = {n: files[n] for n in SOURCE_FILES if n.endswith('.html') or n == game_file}
    runtime = {n: files[n] for n in ('rouge/data/node-catalog.json', 'rouge/node_catalog.py',
                                    CONFIG, SELECTED, DATA, PACK + '/README.md', PACK + '/SCHEMA.md')}
    manifest = {'schema': 'ritual_weakening_source_manifest_v1', 'event_id': EVENT_ID,
                'data_file': DATA, 'data_sha256': pin(result[DATA])['sha256'],
                'selected_authority_file': SELECTED, 'fixed_build_inputs_sha256': pin(config_raw)['sha256'],
                'files': files, 'runtime_files': runtime, 'build_authority_files': build,
                'runtime_reads_complete_primary_table': False, 'runtime_verifies_complete_original_bytes': False,
                'all_runtime_members_required_for_each_target_query': True,
                'counts': {'events': 1, 'choices': 6, 'weakening_references': 3, 'related_stages': 1}, 'source': source}
    result[MANIFEST] = encoded(manifest)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = reconstruct()
    for name, raw in result.items():
        target = ROOT / name
        if args.write:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
        else: assert target.read_bytes() == raw, name
    manifest = json.loads(result[MANIFEST])
    print(json.dumps({'kind': 'FIXED_SOURCE_BUILD_NOT_PRODUCT_ACCEPTANCE', 'write': args.write,
                      'counts': manifest['counts'], 'runtime_files': len(manifest['runtime_files']),
                      'runtime_bytes_with_manifest': sum(p['bytes'] for p in manifest['runtime_files'].values()) + len(result[MANIFEST]),
                      'data_sha256': pin(result[DATA])['sha256'], 'manifest_sha256': pin(result[MANIFEST])['sha256'],
                      'calculation_or_run_state_changed': False}, ensure_ascii=False, indent=2))


if __name__ == '__main__': main()
