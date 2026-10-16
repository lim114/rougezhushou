"""Build selected expedition references from complete pinned public originals.

Reuses the standard-library exact-DOM approach used by sections 290/293/295.
The 17 MB primary table is checked at build time, never by the runtime query.
"""
from copy import deepcopy
from hashlib import sha256
from html.parser import HTMLParser
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKET = 'research/p3-expedition-results-297'
DATA = 'rouge/data/expedition-results.json'
CATALOG = 'rouge/data/node-catalog.json'
CATALOG_SHA = '7df1d94bb69650eb19fc811af661e54d44bf07d72b1c0793de511adc1b2e915d'
EVENT = 'community_group_024'
SCENE = EVENT + ':scene:0'
ITEM = 'rogue_6_relic_final_3'
GAME_SHA = 'f5867e55d09472253083486174aa47bd94dd48b07684b74b60a5b29ca00eda86'
COMMIT = 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'
SOURCE_FILES = {
    'prts-events-427904.html': ('research/p3-choice-recruitment-290/prts-events-427904.html',
        'faa088b0474e75806b357df8648c6a59b1be6dcbc9be749db7c934ca9e6307e9'),
    'prts-events-440271.html': ('research/p3-choice-recruitment-290/prts-events-440271.html',
        'e04971ad361436e5bb3721883423d98ad66636d5156794dd6221a977ffd6dac8'),
    'prts-main-433770.html': ('research/p3-stage-context/community-main.html',
        '366e0bf14b526816b20750f1d83b6c7b132d556dfc0b09a0ab3c302fd00610e9'),
}
ICON = 'rouge/data/relic-icons/' + ITEM + '.png'
ICON_SHA = '7d6ba9f10f8b19d4442b224c2f59e4a60bcc4da8e58689ebcf2239e5e9e7542e'
ICON_RECEIPT = 'rouge/data/relic-icon-receipt.json'
ICON_RECEIPT_SHA = 'aaf4cb93f7a41791e37481106a35fa75614d6f3f4bc12a2bb971a9c2bdd5e6ac'
ORIGINAL_IDS = ('choice_ro6_scout_1', 'choice_ro6_scout_3', 'choice_ro6_scout_2', 'choice_ro6_scout_4')
SCENE_IDS = ('scene_ro6_scout_enter', 'scene_ro6_scout_2', 'scene_ro6_scout_3', 'scene_ro6_scout_1')


class _Node:
    def __init__(self, tag, attrs, order):
        self.tag, self.attrs, self.order, self.children = tag, dict(attrs), order, []


class _Document(HTMLParser):
    VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.nodes = []; self.stack = [_Node('root', [], -1)]; self.feed(text)
    def handle_starttag(self, tag, attrs):
        node = _Node(tag, attrs, len(self.nodes)); self.nodes.append(node)
        self.stack[-1].children.append(node)
        if tag not in self.VOID: self.stack.append(node)
    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID: self.handle_endtag(tag)
    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]; break
    def handle_data(self, value): self.stack[-1].children.append(value)


def _descendants(node):
    for child in node.children:
        if isinstance(child, _Node): yield child; yield from _descendants(child)


def _class(node, value): return value in node.attrs.get('class', '').split()
def _text(node):
    if isinstance(node, str): return node
    return ''.join(_text(child) + ('\n' if isinstance(child, _Node) and child.tag in ('br','li','p') else '')
                   for child in node.children)
def _part(node, cls):
    parts = [n for n in _descendants(node) if _class(n, cls)]
    if len(parts) != 1: raise ValueError('Expected one DOM part: ' + cls)
    return _text(parts[0]).strip()
def _json(value): return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf8')
def _pin(raw): return {'sha256': sha256(raw).hexdigest(), 'bytes': len(raw)}
def _checked(root, path, digest):
    raw = (root / path).read_bytes()
    if sha256(raw).hexdigest() != digest: raise ValueError('Changed source: ' + path)
    return raw


def _event_dom(raw, revision):
    doc = _Document(raw.decode('utf8'))
    groups = [n for n in doc.nodes if _class(n, 'IS-event-data')]
    groups = [g for g in groups if any(_class(n, 'scene') and n.attrs.get('data-name') == '未涉足之树'
                                     for n in _descendants(g))]
    if len(groups) != 1: raise ValueError('Ambiguous expedition DOM group.')
    scenes = [n for n in _descendants(groups[0]) if _class(n, 'scene')]
    if len(scenes) != 4: raise ValueError('Expedition scene count changed.')
    expected = [('尝试探索树的内部', '1', 'simple'), ('尝试探索树的源头', '2', 'simple'), ('休息', '3', 'simple')]
    start = [n for n in _descendants(scenes[0]) if _class(n, 'choose')]
    if [(n.attrs.get('data-title'),n.attrs.get('data-dest'),n.attrs.get('data-type')) for n in start] != expected:
        raise ValueError('Dispatch/rest choices changed.')
    origin = [n for n in _descendants(scenes[2]) if _class(n, 'choose')]
    if len(origin) != 2 or origin[1].attrs.get('data-type') != 'desc': raise ValueError('Explanatory role changed.')
    note = _part(origin[1], 'desc1')
    if not all(word in note for word in ('不会被进阶', '回归时，仅获得2希望与收藏品', 'No.227 怦然信标')):
        raise ValueError('Root return reward wording changed.')
    images = [n.attrs for n in _descendants(origin[1]) if n.tag == 'img']
    if len(images) != 1 or not images[0].get('src', '').endswith('/' + ITEM + '.png'):
        raise ValueError('Return item exact image identity changed.')
    return {'revision': revision, 'group_identity': '未涉足之树 / 先行一步',
        'scenes': [{'scene_number_zero_based': number, 'attributes': scene.attrs,
            'description': _part(scene, 'sceneText'), 'choices': [{'attributes': n.attrs,
                'description': _part(n, 'desc1')} for n in _descendants(scene) if _class(n, 'choose')]}
            for number, scene in enumerate(scenes)],
        'root_return_explanation': note, 'root_return_item_image': images[0]}


def build(root=ROOT, *, original_topic):
    root = Path(root)
    game_raw = Path(original_topic).read_bytes()
    if sha256(game_raw).hexdigest() != GAME_SHA: raise ValueError('Complete primary topic table changed.')
    detail = json.loads(game_raw)['details']['rogue_6']
    catalog_raw = _checked(root, CATALOG, CATALOG_SHA)
    event = next(e for e in json.loads(catalog_raw)['events'] if e['id'] == EVENT)
    if len(event['scenes']) != 4: raise ValueError('Current event scope changed.')
    starts = event['scenes'][0]['choices']
    for index, expected_id in enumerate(ORIGINAL_IDS[:3]):
        if starts[index]['key'] != SCENE + ':choice:' + str(index) or starts[index]['game_choice_ids'] != [expected_id]:
            raise ValueError('Complete choice identity changed.')
    if event['scenes'][2]['choices'][0]['game_choice_ids'] != [ORIGINAL_IDS[3]]:
        raise ValueError('Original leave identity changed.')
    explanation = event['scenes'][2]['choices'][1]
    if explanation['presentation_role'] != 'explanatory_text' or explanation['game_choice_ids'] != []:
        raise ValueError('Explanatory text must not become a game choice.')
    primary = {'source': {'url': 'https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/' + COMMIT +
        '/zh_CN/gamedata/excel/roguelike_topic_table.json', 'commit': COMMIT, **_pin(game_raw)},
        'choiceScenes': {key: detail['choiceScenes'][key] for key in SCENE_IDS},
        'choices': {key: detail['choices'][key] for key in ORIGINAL_IDS},
        'gameConst': {key: value for key,value in detail['gameConst'].items() if 'exped' in key.lower()},
        'detailConst': {key: value for key,value in detail['detailConst'].items() if 'exped' in key.lower()},
        'item': detail['items'][ITEM], 'relic': detail['relics'][ITEM], 'relicParams': detail['relicParams'][ITEM]}
    if primary['gameConst']['expedEndingRelic'] != ITEM: raise ValueError('Explicit return item pointer changed.')
    if [primary['choices'][k]['type'] for k in ORIGINAL_IDS] != ['EXPEDITION','EXPEDITION','TRADE','TRADE']:
        raise ValueError('Original dispatch/leave choice types changed.')
    if [primary['choices'][k]['nextSceneId'] for k in ORIGINAL_IDS] != ['scene_ro6_scout_2','scene_ro6_scout_3','scene_ro6_scout_1',None]:
        raise ValueError('Declared destination changed; cannot infer a new entry.')
    files = {}; dom = []
    for name,(path,digest) in SOURCE_FILES.items():
        raw = _checked(root, path, digest); files[PACKET + '/' + name] = raw
        if name.startswith('prts-events-'): dom.append(_event_dom(raw, name.split('-')[-1][:-5]))
    main_doc = _Document(files[PACKET + '/prts-main-433770.html'].decode('utf8'))
    main_excerpts = []
    for n in main_doc.nodes:
        text = _text(n).strip() if n.tag in ('li', 'dd') else ''
        if any(needle in text for needle in ('该干员将在下一层开始时归来', '尝试探索树的源头',
                '无法在先行一步中被选择', '干员归来时还可获得随机加工品',
                '可不选择干员并“确认”重新选择选项')):
            main_excerpts.append({'tag': n.tag, 'dom_order': n.order, 'text': text})
    if len(main_excerpts) != 5: raise ValueError('Expected five exact main-page reference paragraphs.')
    icon_raw = _checked(root, ICON, ICON_SHA)
    receipt_raw = _checked(root, ICON_RECEIPT, ICON_RECEIPT_SHA)
    receipt = json.loads(receipt_raw)
    icon_record = next(r for r in receipt['icons'] if r['id'] == ITEM)
    if icon_record['sha256'] != ICON_SHA: raise ValueError('Icon receipt disagrees with the image.')
    icon = {'item_id': ITEM, 'icon_id': ITEM, 'file': ICON, **_pin(icon_raw),
            'source': icon_record, 'repository': receipt['repository'], 'commit': receipt['commit']}
    source = {'primary': primary['source'], 'event_documents': [{'revision': revision,
        'url': 'https://prts.wiki/index.php?title=沉沦者的黑流树海/事件一览&oldid=' + revision,
        'file': PACKET + '/prts-events-' + revision + '.html'} for revision in ('427904','440271')],
        'main_document': {'revision': '433770', 'file': PACKET + '/prts-main-433770.html',
            'url': 'https://prts.wiki/index.php?title=沉沦者的黑流树海&oldid=433770'},
        'current_server_verified': False}
    dispatch = {'operator_count_reference': 1, 'temporarily_unavailable_for_squad': True,
        'native_return_wordings': [primary['gameConst']['expeditionSelectDescFormat'],
                                   primary['detailConst']['defaultExpeditionSelectDesc']],
        'native_unavailable_wording': primary['gameConst']['charSelectExpeditionConflictToast'],
        'community_return_when': '下一层开始时', 'special_region_equivalence': None,
        'actual_operator': None, 'actual_unavailable': None, 'actual_returned': None, 'actual_return_clock': None}
    beak = {'source_text': main_excerpts[3]['text'], 'applies_to_root_branch': None,
        'current_technology_active': None, 'quantity_reference': None, 'complete_item_pool': None,
        'notice': '资料另记“喙”使归来时额外获得随机加工品；与源头“仅获得”的关系尚未核验，不额外加算。'}
    if '喙' not in beak['source_text']: raise ValueError('Beak paragraph was not selected exactly.')
    rows = []
    for index, choice in enumerate(starts):
        row = {'reference_id': choice['key'] + ':expedition-result', 'event_id': EVENT,
            'scene_key': SCENE, 'choice_key': choice['key'], 'original_choice_id': ORIGINAL_IDS[index],
            'choice_title': choice['title'], 'choice_description': choice['description'],
            'is_actual_button_reference': True, 'reference_kind': 'expedition_choice_result',
            'effect_phase_reference': 'on_choice' if index == 2 else 'on_return',
            'dispatch_reference': None if index == 2 else deepcopy(dispatch),
            'immediate_resource_references': [{'resource': 'hope', 'quantity_reference': 2}] if index == 2 else [],
            'return_resource_references': [{'resource': 'hope', 'quantity_reference': 2}] if index == 1 else [],
            'documented_return_item': {'item_id': ITEM, 'name': primary['item']['name'], 'quantity_reference': None,
                'effect_phase_reference': 'on_return', 'original_pointer_field': 'gameConst.expedEndingRelic'} if index == 1 else None,
            'promotion_reference': False if index == 1 else None,
            'complete_return_rewards_known': False, 'beak_reference': deepcopy(beak) if index != 2 else None,
            'explanatory_choice_key': explanation['key'] if index == 1 else None,
            'return_explanation': explanation['description'] if index == 1 else None,
            'actual_dispatched_operator': None, 'actual_returned': None, 'actual_reward': None,
            'actual_quantity': None, 'actual_advanced': None, 'actual_return_clock': None, 'actual_selectable': None}
        rows.append(row)
    annotation = {'reference_id': explanation['key'] + ':return-explanation', 'event_id': EVENT,
        'scene_key': event['scenes'][2]['key'], 'choice_key': explanation['key'],
        'description': explanation['description'], 'presentation_role': explanation['presentation_role'],
        'game_choice_ids': deepcopy(explanation['game_choice_ids']), 'is_actual_button': False,
        'reference_kind': 'expedition_return_explanation', 'effect_phase': 'on_return',
        'source_dispatch_choice_key': starts[1]['key'],
        'return_resource_references': deepcopy(rows[1]['return_resource_references']),
        'documented_return_item': deepcopy(rows[1]['documented_return_item']),
        'actual_reward': None, 'actual_quantity': None, 'actual_selectable': None,
        'actual_returned': None, 'actual_advanced': None}
    packet = {'schema': 'expedition_results_reference_v1', 'event_id': EVENT, 'reference_kind': 'expedition_choice_results',
        'event_name': event['title'], 'expected_event': event, 'rows': rows, 'item': primary['item'], 'icon_reference': icon,
        'return_explanatory_reference': annotation,
        'source': source, 'source_reference': {'event_dom_bindings': dom, 'main_excerpts': main_excerpts,
            'original_choice_ids': list(ORIGINAL_IDS), 'original_scene_ids': list(SCENE_IDS),
            'original_return_item_pointer': primary['gameConst']['expedEndingRelic'],
            'entry_script_recovered': False, 'return_script_recovered': False},
        'current_server_verified': False, 'inventory_updated': False, 'eligibility_evaluated': False,
        'unlock_notice': '物品条目的“完成游戏结局”是物品解锁资料，不等于源头选项或本局完整出现条件；主网页另在完成强制重启后的流程内说明此选项。',
        'notice': '这里只查阅三个具体选项的资料结果。派出与归来不是同一时刻；不代表本局已派出、已回来、已领取或已进阶。',
        'unknowns': ['普通内部探索是否必然进阶未闭合。',
            '进入特殊区域是否等同此处“进入新区域”未核验；不据此计算实际归来时刻。',
            '“喙”的额外加工品与源头“仅获得2希望与怦然信标”的关系未核验，不强行叠加。',
            '具体派出者、实际可选、归来/发放脚本、完整物资池与当前服务器执行均未核验。']}
    files[PACKET + '/original-records.json'] = _json(primary)
    files[PACKET + '/dom-bindings.json'] = _json({'event_documents': dom, 'main_excerpts': main_excerpts})
    files[DATA] = _json(packet)
    dependencies = {CATALOG: catalog_raw, ICON: icon_raw, ICON_RECEIPT: receipt_raw}
    manifest = {'schema': 'expedition_results_source_manifest_v1', 'data_file': DATA,
        'data_sha256': sha256(files[DATA]).hexdigest(),
        'files': {name: _pin(blob) for name,blob in {**files, **dependencies}.items()},
        'primary_table_build_check': primary['source'],
        'runtime_reads_primary_table': False, 'scope': 'documented reference only, no run state or actual outcome'}
    files[PACKET + '/source-manifest.json'] = _json(manifest)
    return files, dependencies


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--original-topic', required=True, type=Path)
    parser.add_argument('--output-root', type=Path)
    args = parser.parse_args(); output = args.output_root or args.root
    files, dependencies = build(args.root, original_topic=args.original_topic)
    for name,raw in files.items():
        path = output / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(raw)
    print(json.dumps({'kind': 'source-build-not-product-acceptance', 'files': {name: _pin(raw) for name,raw in files.items()},
        'dependency_pins': {name: _pin(raw) for name,raw in dependencies.items()},
        'data_sha256': sha256(files[DATA]).hexdigest(),
        'manifest_sha256': sha256(files[PACKET + '/source-manifest.json']).hexdigest(),
        'original_topic_checked': True, 'Qt_game_chat_private': False}, ensure_ascii=False, indent=2))


if __name__ == '__main__': main()
