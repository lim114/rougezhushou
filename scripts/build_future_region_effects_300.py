"""Reconstruct the exact red-moss document references from complete fixed sources.

Default is read-only verification. --write explicitly rebuilds derived public files.
No product modules, network, game, user state or Qt are accessed.
"""
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = 'research/p3-future-region-effects-300'
DATA = 'rouge/data/future-region-effects.json'
MANIFEST = PACK + '/source-manifest.json'
SELECTED_AUTHORITY = PACK + '/selected-authority-records.json'
EVENT = 'community_group_009'
COMMIT = 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'
SOURCES = {
    'game-topic-complete.json': 'f5867e55d09472253083486174aa47bd94dd48b07684b74b60a5b29ca00eda86',
    'prts-main-433770.html': '366e0bf14b526816b20750f1d83b6c7b132d556dfc0b09a0ab3c302fd00610e9',
    'prts-events-427904.html': 'faa088b0474e75806b357df8648c6a59b1be6dcbc9be749db7c934ca9e6307e9',
    'prts-events-440271.html': 'e04971ad361436e5bb3721883423d98ad66636d5156794dd6221a977ffd6dac8',
    'bwiki-events-349818.html': '26b7768bf3556cf73c24529659c2c92f4095059476f782130bf3fa768422b908',
    'weather-ordinary-tool-response.json': 'ce8b30ff6d394e7e5fcdf6eb75600eb71b93c60d7c5431ca9b389ed5ddaa42f1',
    'weather-footer-tool-response.json': '198489e0cd04494f16ddcd558331935959cc921c224a9a2b4052e2f4586400cb',
}
CATALOG_SHA = '7df1d94bb69650eb19fc811af661e54d44bf07d72b1c0793de511adc1b2e915d'


def sha(raw): return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf8')


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
        node = Node(tag, attrs)
        self.nodes.append(node)
        self.stack[-1].children.append(node)
        if tag not in self.VOID: self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID: self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                break

    def handle_data(self, value): self.stack[-1].children.append(value)


def text(node):
    if isinstance(node, str): return node
    return ''.join(text(c) + ('\n' if isinstance(c, Node) and c.tag in ('br', 'p', 'li') else '') for c in node.children)


def descendants(node):
    for c in node.children:
        if isinstance(c, Node):
            yield c
            yield from descendants(c)


def tree(node):
    if isinstance(node, str): return node
    return {'tag': node.tag, 'attributes': node.attrs, 'children': [tree(c) for c in node.children]}


def has_class(node, name): return name in node.attrs.get('class', '').split()


def reconstruct():
    raw = {}
    for name, digest in SOURCES.items():
        value = (ROOT / PACK / name).read_bytes()
        if sha(value) != digest: raise ValueError('Fixed source mismatch: ' + name)
        raw[name] = value
    catalog_raw = (ROOT / 'rouge/data/node-catalog.json').read_bytes()
    if sha(catalog_raw) != CATALOG_SHA: raise ValueError('Catalog source mismatch.')
    catalog = json.loads(catalog_raw)
    event = next(e for e in catalog['events'] if e['id'] == EVENT)
    assert event['title'] == '呼吸的红苔' and len(event['scenes']) == 4
    scene = event['scenes'][0]
    assert scene['key'] == EVENT + ':scene:0'
    choices = scene['choices'][:2]
    assert [c['key'] for c in choices] == [scene['key'] + ':choice:0', scene['key'] + ':choice:1']
    assert choices[0]['game_choice_ids'] == [] and choices[1]['game_choice_ids'] == ['choice_ro6_normal3_2']
    game = json.loads(raw['game-topic-complete.json'])
    detail = game['details']['rogue_6']
    weather = game['modules']['rogue_6']['weather']
    primary_choices = [detail['choices']['choice_ro6_normal3_' + str(i)] for i in (1, 2)]
    assert [c['title'] for c in choices] == [c['title'] for c in primary_choices]
    event_doms = {}
    for revision in ('427904', '440271'):
        document = Document(raw['prts-events-' + revision + '.html'])
        matches = []
        for group in (n for n in document.nodes if has_class(n, 'IS-event-data')):
            scenes = [n for n in descendants(group) if has_class(n, 'scene')]
            if scenes and scenes[0].attrs.get('data-index') == scene['attributes']['data-index']:
                matches.append((group, scenes))
        assert len(matches) == 1
        group, scenes = matches[0]
        assert [s.attrs for s in scenes] == [s['attributes'] for s in event['scenes']]
        event_doms[revision] = {'complete_DOM': tree(group), 'complete_text': text(group)}
    main = Document(raw['prts-main-433770.html'])
    tables = [n for n in main.nodes if n.tag == 'table' and '实托邦景象' in text(n) and '保密等级·15' in text(n)]
    assert len(tables) == 1
    difficulty_cells = {}
    for row in descendants(tables[0]):
        if row.tag != 'tr': continue
        cells = [c for c in row.children if isinstance(c, Node) and c.tag in ('td', 'th')]
        if len(cells) != 7: continue
        grade = text(cells[2]).strip()
        if grade in {str(n) for n in range(16)}:
            assert grade not in difficulty_cells
            difficulty_cells[grade] = {'complete_DOM': tree(row), 'weather_cell': text(cells[-1]).strip()}
    assert set(difficulty_cells) == {str(n) for n in range(16)}
    assert {g: difficulty_cells[str(g)]['weather_cell'] for g in (0, 1, 2, 6, 12)} == {0:'无', 1:'~', 2:'早期', 6:'中期', 12:'晚期'}
    assert all(difficulty_cells[str(g)]['weather_cell'] == '~' for g in (3,4,5,7,8,9,10,11,13,14,15))
    normal = [r for r in detail['difficulties'] if r['modeDifficulty'] == 'NORMAL']
    assert len(normal) == 16
    assert '中期' in normal[6]['ruleDesc'] and '晚期' in normal[12]['ruleDesc']
    bw = Document(raw['bwiki-events-349818.html'])
    bw_cells = [tree(n) for n in bw.nodes if n.tag in ('p','td','dd') and '希望的沃土' in text(n)]
    assert bw_cells
    phases = []
    for suffix, phase, name, low, high, attack, hp in (
            ('a','early','早期',2,5,10,10), ('b','middle','中期',6,11,15,20), ('c','late','晚期',12,15,20,30)):
        identity = 'rogue_6_weather_8_' + suffix
        original = weather['mainWeatherData'][identity]
        assert original['levelName'] == name and original['name'] == '“希望的沃土”'
        assert original['functionDesc'] == f'我方单位攻击+{attack}%，生命+{hp}%，战斗胜利后获得随机零件'
        phases.append({'id':identity, 'phase':phase, 'phase_name':name, 'name':name,
            'normal_difficulty_min':low, 'normal_difficulty_max':high,
            'attack_percent':attack, 'max_hp_percent':hp, 'hp_percent':hp,
            'source_text':original['functionDesc'], 'raw':original})
    rows = []
    for index, (community, original) in enumerate(zip(choices, primary_choices)):
        rows.append({'reference_id':community['key'], 'event_id':EVENT, 'scene_key':scene['key'],
            'choice_key':community['key'], 'choice_title':community['title'], 'choice_description':community['description'],
            'catalog_choice':community, 'original_choice':original, 'primary_choice_id':original['id'],
            'game_choice_ids':community['game_choice_ids'], 'entry_restored':False,
            'source_text':original['description'],
            'immediate_text':'获得30源石锭。' if index == 0 else '种下1枚种子。',
            'requirement_text':'原文要求持有笼控器；本局是否满足仍未知。' if index == 0 else '原文种下1枚种子；本局能否选择仍未知。',
            'direct_resources':[{'resource':'gold' if index == 0 else 'seed', 'quantity_reference':30 if index == 0 else 1,
                'action':'gain' if index == 0 else 'sow', 'effect_phase':'on_choice', 'source_text':original['description']}],
            'future_region_reference':{'name':'希望的沃土', 'effect_phase':'next_region',
                'affected_nodes':'仅受该实托邦影响的节点；具体节点未知', 'phases':phases},
            'conditional_victory_reward':{'resource':'random_scrap', 'condition':'受该实托邦影响的战斗胜利后',
                'quantity_reference':None, 'complete_pool':None, 'actual_received':None,
                'source_text':'战斗胜利后获得随机零件'},
            **{k:None for k in ('actual_choice','actual_weather','actual_phase','actual_affected_nodes','actual_reward','actual_quantity')}})
    source = {'game':{'commit':COMMIT,'file':PACK+'/game-topic-complete.json'},
        'main':{'revision':'433770','file':PACK+'/prts-main-433770.html'},
        'events':[{'revision':r,'file':PACK+'/prts-events-'+r+'.html'} for r in ('427904','440271')],
        'bwiki':{'revision':'349818','file':PACK+'/bwiki-events-349818.html'},
        'supplemental_weather':{'ordinary_tool_response_footer_revision':'434599',
            'fixed_full_HTML_acquired':False, 'file':PACK+'/weather-ordinary-tool-response.json',
            'footer_file':PACK+'/weather-footer-tool-response.json', 'role':'supplemental_documentation_only'}}
    packet = {'schema':'future_region_effects_v1', 'event_id':EVENT, 'event_title':event['title'],
        'expected_event':event, 'choices':rows, 'phases':phases, 'source':source,
        'source_reference':{'complete_primary_choices':primary_choices,
            'complete_primary_weather':[p['raw'] for p in phases], 'complete_NORMAL_difficulties':normal,
            'complete_difficulty_table_DOM':tree(tables[0]), 'complete_difficulty_cells':difficulty_cells,
            'complete_community_event_DOMs':event_doms, 'complete_BWiki_containing_elements':bw_cells,
            'complete_force_weather_item':detail['items']['rogue_6_next_weather_1'],
            'complete_force_weather_relic':detail['relics']['rogue_6_next_weather_1'],
            'complete_gain_policy':weather['subWeatherData']['rogue_6_subweather_4'],
            'complete_weather_archive_entries':{k:detail['archiveComp']['weather']['weathers'][k] for k in
                ('rogue_6_weather_8_a','rogue_6_weather_8_b','rogue_6_weather_8_c','rogue_6_subweather_4')}},
        'supplemental_documentation':{
            'source_role':'supplemental_documentation_only', 'gain_policy':weather['subWeatherData']['rogue_6_subweather_4'],
            'community_pairing_documented':True, 'execution_pair_binding_proven':False,
            'notice':'社区资料记有与“增益”同现、经特定选择带入下一区域等说明；这些说明不证明本局已生效，不作为排除条件或数值计算。',
            'fixed_full_HTML_acquired':False, 'force_limit_literal':1.0, 'force_limit_semantics_verified':False},
        'notice':'这里只列所选分支在下一区域的文献效果；两条选择与三个档位分别阅读，不相加，也不表示本局已发生。',
        'unknowns':['本局能否选择及是否已选择','下一区域实际采用的档位与受影响节点','随机零件的完整范围、数量及实际领取',
            '普通模式0/1级的强制生成与档位、其它模式对应关系','当前服务器版本是否与固定资料一致'],
        'current_server_verified':False, 'entry_restored':False, 'calculation_applied':False, 'run_state_updated':False}
    authority_raw = encoded({'schema':'future_region_selected_authority_v1','event_id':EVENT,
        'expected_event':event, 'source':source, 'source_reference':packet['source_reference'],
        'build_authority_sha256':{PACK+'/'+name:digest for name,digest in SOURCES.items()},
        'complete_source_reconstruction_required':True})
    data_raw = encoded(packet)
    files = {PACK+'/'+name: {'sha256':sha(value), 'bytes':len(value)} for name,value in raw.items()}
    files['rouge/data/node-catalog.json'] = {'sha256':sha(catalog_raw),'bytes':len(catalog_raw)}
    for name in ('README.md','SCHEMA.md'):
        value = (ROOT/PACK/name).read_bytes()
        files[PACK+'/'+name] = {'sha256':sha(value),'bytes':len(value)}
    files[DATA] = {'sha256':sha(data_raw),'bytes':len(data_raw)}
    files[SELECTED_AUTHORITY] = {'sha256':sha(authority_raw),'bytes':len(authority_raw)}
    runtime_files = {relative:files[relative] for relative in
        (DATA,SELECTED_AUTHORITY,'rouge/data/node-catalog.json',PACK+'/README.md',PACK+'/SCHEMA.md')}
    manifest = {'schema':'future_region_effects_source_manifest_v1','data_file':DATA,'data_sha256':sha(data_raw),
        'event_id':EVENT, 'files':files, 'runtime_reads_primary_table':False,
        'runtime_files':runtime_files,'selected_authority_file':SELECTED_AUTHORITY,
        'build_authority_files':{PACK+'/'+name:files[PACK+'/'+name] for name in SOURCES},
        'runtime_verifies_complete_original_bytes':False,
        'rebuilds_from_complete_primary_table':True, 'source':source}
    return data_raw, encoded(manifest), authority_raw


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Explicitly rebuild the two public derived files.')
    args = parser.parse_args()
    data, manifest, authority = reconstruct()
    for relative, raw in ((DATA,data),(MANIFEST,manifest),(SELECTED_AUTHORITY,authority)):
        path = ROOT/relative
        if args.write:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(raw)
        elif path.read_bytes() != raw:
            raise ValueError('Rebuild differs: '+relative)
    print(json.dumps({'kind':'SOURCE_BUILD_NOT_PRODUCT_ACCEPTANCE','write':args.write,
        'complete_source_count':len(SOURCES),'choices':2,'phases':3,
        'data_sha256':sha(data),'manifest_sha256':sha(manifest),'selected_authority_sha256':sha(authority),
        'runtime_fresh_file_count':5,'runtime_fresh_bytes':sum(p['bytes'] for p in json.loads(manifest)['runtime_files'].values())+len(manifest),
        'new_entry_or_actual_execution_claim':False},ensure_ascii=False,indent=2))


if __name__ == '__main__': main()
