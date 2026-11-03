"""Rebuild fixed boss documentary data from complete pinned source records."""
from copy import deepcopy
from hashlib import sha256
from html.parser import HTMLParser
from pathlib import Path
import argparse
import json
import re

ROOT = Path(__file__).resolve().parents[1]
PACK = 'research/p3-boss-phase-309'
DATA = 'rouge/data/boss-phase-reference.json'
MANIFEST = PACK + '/source-manifest.json'
TARGET = ('ro6_b_6', 'enemy_2150_shchmr', 0)
BATTLE = 'rouge/data/battle-previews.json'
SKILLS = 'rouge/data/enemy-skill-references.json'
TEMPLATE_SHA = '49eb7493639f5710b78ea124bccfb6ad383719c4cff11cac6da58275e553b8b9'
FROZEN_HANDOFF_SHA = 'b2c2318fc8f3dc35c6e9844375505e70d58835954ffe25a0672a21cc33cfcecd'
REVIEW_HANDOFF_SHA = '49bb65f61e33ab5752a10af85143ddb4b41bf386ce908e53236e7ff81ba46253'
PHASE_NAMES = ['第一形态', '灾厄形态(一)', '第二形态', '灾厄形态(二)', '第三形态', '飞行形态']
MODE_LITERALS = [['灾厄形态(一)', '灾厄形态(二)'], ['第二形态', '第三形态'],
                 ['第三形态'], ['第三形态'], ['飞行形态'], ['飞行形态']]


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf8')


def pin(raw):
    return {'sha256': sha256(raw).hexdigest(), 'bytes': len(raw)}


def require(value, message):
    if not value:
        raise ValueError(message)


def same(one, two):
    if type(one) is not type(two):
        return False
    if type(one) is dict:
        return one.keys() == two.keys() and all(type(k) is str and same(one[k], two[k]) for k in two)
    if type(one) is list:
        return len(one) == len(two) and all(same(a, b) for a, b in zip(one, two))
    return one == two


class Node:
    def __init__(self, tag, attrs):
        self.tag, self.attrs, self.children = tag, dict(attrs), []


class Document(HTMLParser):
    VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.nodes, self.stack = [], [Node('root', [])]
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs)
        self.nodes.append(node)
        self.stack[-1].children.append(node)
        if tag not in self.VOID:
            self.stack.append(node)
    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID:
            self.handle_endtag(tag)
    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                break
    def handle_data(self, text):
        self.stack[-1].children.append(text)


def serial(node):
    return node if isinstance(node, str) else {'tag': node.tag, 'attributes': node.attrs,
                                              'children': [serial(child) for child in node.children]}


def visible(node):
    if isinstance(node, str):
        return node
    if node.tag in ('script', 'style') or 'display:none' in node.attrs.get('style', '').replace(' ', ''):
        return ''
    if node.tag == 'br':
        return '\n'
    return ''.join(visible(child) for child in node.children) + ('\n' if node.tag in ('p', 'li', 'dt', 'dd') else '')


def reference(player, modes):
    ref = deepcopy(player)
    ref.update(stage_id=TARGET[0], enemy_id=TARGET[1], level=TARGET[2], boss_name='玻利瓦尔，症结之核')
    for phase in ref['phases']:
        phase['id'] = phase['phase_id']
    for skill, labels in zip(ref['skills'], modes):
        skill['original_documented_modes'] = deepcopy(skill['documented_modes'])
        skill['documented_modes'] = deepcopy(labels)
    ref['common_documented_context']['reading_notes'] = [
        ('文献说明注：' + note) if '未用完的延长灾厄' in note else note
        for note in ref['common_documented_context']['reading_notes']]
    return ref


def build(root=ROOT, output_root=None, *, enemy_database=None):
    root = Path(root)
    output = root if output_root is None else Path(output_root)
    authority_root = output if (output / PACK / 'HANDOFF.json').is_file() else root
    handoff_raw = (authority_root / PACK / 'HANDOFF.json').read_bytes()
    require(sha256(handoff_raw).hexdigest() == FROZEN_HANDOFF_SHA, 'Frozen original research handoff changed')
    handoff = json.loads(handoff_raw)
    originals = {}
    for name, expected in handoff['files'].items():
        raw = (authority_root / PACK / name).read_bytes()
        require(same(pin(raw), expected), 'Complete frozen research member changed: ' + name)
        originals[PACK + '/' + name] = raw
    review_raw = (authority_root / PACK / 'final-review/HANDOFF.json').read_bytes()
    require(sha256(review_raw).hexdigest() == REVIEW_HANDOFF_SHA, 'Independent review handoff changed')
    review_handoff = json.loads(review_raw)
    for name, expected in review_handoff['files'].items():
        raw = (authority_root / PACK / 'final-review' / name).read_bytes()
        require(same(pin(raw), expected), 'Complete independent review member changed: ' + name)
        originals[PACK + '/final-review/' + name] = raw
    player = json.loads(originals[PACK + '/player-reading-data-candidate.json'])
    selected = json.loads(originals[PACK + '/selected-original-records.json'])
    modes = json.loads(originals[PACK + '/final-review/seven-complete-visible-cards.json'])
    review = json.loads(originals[PACK + '/final-review/source-review.json'])
    require(same(player['identity'], dict(zip(('stage_id', 'enemy_id', 'level'), TARGET))), 'Exact target identity required')
    require([row['name'] for row in player['phases']] == PHASE_NAMES, 'All six documented entries required')
    require(len(player['skills']) == 6 and len(player['transitions']) == 7, 'Complete documented skills and transitions required')
    html = originals[PACK + '/boss-complete.html'].decode('utf8')
    require(re.search(r'"wgRevisionId"\s*:\s*435612\b', html), 'Exact complete boss revision required')
    stage_html = originals[PACK + '/stage-complete.html'].decode('utf8')
    require(re.search(r'"wgRevisionId"\s*:\s*420841\b', stage_html), 'Exact complete stage revision required')
    cards = [node for node in Document(html).nodes if {'ak-card__body', 'skill_card'} <= set(node.attrs.get('class', '').split())]
    require(len(cards) == len(modes['cards']) == 7, 'Seven complete document cards required')
    labels = []
    for index, (card, extracted) in enumerate(zip(cards, modes['cards'])):
        if index < 6:
            title = next(node for node in card.children if isinstance(node, Node) and 'ak-card__title' in node.attrs.get('class', '').split())
            current_labels = re.findall(r'\[([^\[\]]+)\]', visible(title))
            require(current_labels == MODE_LITERALS[index] == extracted['documented_mode_labels'], 'Complete header mode extraction mismatch')
            require(same(serial(card), player['skills'][index]['complete_DOM']), 'Complete original skill DOM mismatch')
            effect = next(node for node in card.children if isinstance(node, Node) and node.tag == 'p')
            require(visible(effect).strip() == player['skills'][index]['effect_text'] == extracted['complete_visible_effect'], 'Complete effect text mismatch')
            labels.append(current_labels)
        else:
            require(same(serial(card), player['common_documented_context']['complete_DOM']), 'Complete common ability DOM mismatch')
            require(visible(card).strip() == player['common_documented_context']['text'], 'Complete common abilities mismatch')
    phase_skills = {row['name']: row['skill_ids'] for row in player['phases']}
    for skill, names in zip(player['skills'], labels):
        require([name for name in PHASE_NAMES if skill['skill_id'] in phase_skills[name]] == names, 'Phase ownership differs from actual header labels')
    require(bool(review['additional_document_tooltip_notes']), 'Cycle inheritance explanatory tooltip required')
    build_inputs = {}
    for source in selected['source_files']:
        name = source['file']
        path = Path(enemy_database) if enemy_database is not None and name.endswith('/enemy_database.json') else root / name
        if not path.is_file() and name.endswith('/level_rogue6_b-6.json'):
            path = root / ('research/p3-spawn-candidates-299/levels/' + source['sha256'] + '.json')
        raw = path.read_bytes()
        require(same(pin(raw), {key: source[key] for key in ('sha256', 'bytes')}), 'Complete build authority changed: ' + name)
        build_inputs[name] = raw
    database = json.loads(next(raw for name, raw in build_inputs.items() if name.endswith('/enemy_database.json')))
    level = json.loads(next(raw for name, raw in build_inputs.items() if name.endswith('/level_rogue6_b-6.json')))
    battle, skill_table = json.loads(build_inputs[BATTLE]), json.loads(build_inputs[SKILLS])
    require(same(next(row for row in database['enemies'] if row['Key'] == TARGET[1]), selected['enemy_database_complete_record']), 'Complete enemy database record mismatch')
    level_refs = [row for row in level['enemyDbRefs'] if row['id'] == TARGET[1]]
    require(len(level_refs) == 1 and same(level_refs[0], selected['stage_complete_enemyDbRefs_record']), 'Whole original level reference mismatch')
    require(type(level_refs[0]['level']) is int and level_refs[0]['level'] == 0 and level_refs[0]['useDb'] is True and level_refs[0]['overwrittenData'] is None, 'Exact selected database binding required')
    require(same(battle['stages'][TARGET[0]], selected['canonical_stage_complete']), 'Whole current fixed stage mismatch')
    require(same(next(row for row in battle['stages'][TARGET[0]]['enemies'] if row['id'] == TARGET[1] and type(row['level']) is int and row['level'] == 0), selected['canonical_enemy_complete']), 'Whole current selected enemy mismatch')
    require(same(skill_table['definitions'][TARGET[1]], selected['current_skill_definition_complete']), 'Whole current skill definition mismatch')
    require(same(skill_table['bindings'][TARGET[0]][TARGET[1] + '@0'], selected['current_skill_binding_complete']), 'Whole current skill binding mismatch')
    unknown = {**{key: None for key in ('actual_phase', 'actual_transition', 'actual_damage', 'actual_elapsed_time', 'actual_target', 'actual_current_server_eligibility', 'phase_stats')},
               **{key: False for key in ('current_server_verified', 'numerical_phase_model_added', 'run_state_updated', 'inventory_updated', 'modifiers_changed', 'maps_changed')}}
    data = {'schema': 'boss_phase_reference_v1', 'reference': reference(player, labels), 'selected_originals': selected,
            'complete_battle_source': battle['source'], 'complete_skill_source': skill_table['source'], 'actual_and_mutation_fields': unknown}
    outputs = {DATA: encoded(data)}
    runtime_names = [PACK + '/' + name for name in ('selected-original-records.json', 'player-reading-data-candidate.json',
                     'boss-complete.html', 'stage-complete.html', 'http-source-records.json',
                     'final-review/seven-complete-visible-cards.json', 'final-review/source-review.json')]
    runtime = {DATA: pin(outputs[DATA]), **{name: pin(originals[name]) for name in runtime_names}}
    template = (authority_root / PACK / 'backend-template.py').read_bytes()
    require(sha256(template).hexdigest() == TEMPLATE_SHA, 'Fixed backend template changed')
    authority = {name: pin(raw) for name, raw in originals.items() if name not in runtime}
    authority.update({PACK + '/HANDOFF.json': pin(handoff_raw), PACK + '/final-review/HANDOFF.json': pin(review_raw),
                      PACK + '/backend-template.py': pin(template)})
    authority.update({name: pin(raw) for name, raw in build_inputs.items()})
    manifest = {'schema': 'boss_phase_source_manifest_v1', 'data_file': DATA, 'data_sha256': sha256(outputs[DATA]).hexdigest(),
                'target': list(TARGET), 'runtime_files': runtime, 'build_authority_files': authority,
                'all_runtime_members_required_for_each_target_query': True, 'runtime_full_database_hashing': False,
                'runtime_scope': 'Fresh complete selected public records and both full fixed HTMLs; compare the entire selected live cache objects. No per-query full database, level, or battle catalogue hashing.',
                'build_scope': 'Full pinned database, level, battle catalogue, skill table and complete documentary sources are checked at rebuild; local cached database can be supplied explicitly with --enemy-database using the same exact SHA.',
                'actual_state_or_numeric_model_added': False}
    outputs[MANIFEST] = encoded(manifest)
    outputs['rouge/boss_phase_reference.py'] = template.decode('utf8').replace('__DATA_SHA__', sha256(outputs[DATA]).hexdigest()).replace('__MANIFEST_SHA__', sha256(outputs[MANIFEST]).hexdigest()).encode('utf8')
    for name, raw in outputs.items():
        path = output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    receipt = {'kind': 'SECTION309_SOURCE_BUILD_NOT_PRODUCT_ACCEPTANCE', 'target': list(TARGET),
               'documented_entries': 6, 'documented_skill_cards': 6, 'documented_transitions': 7,
               'runtime_source_members': len(runtime), 'numeric_model_added': False,
               'outputs': {name: pin(raw) for name, raw in outputs.items()}}
    (output / PACK / 'build-receipt.json').write_bytes(encoded(receipt))
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--output-root', type=Path)
    parser.add_argument('--enemy-database', type=Path)
    parser.add_argument('--check', action='store_true', help='Rebuild in a temporary output and compare exact generated bytes')
    args = parser.parse_args()
    if args.check:
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            # Input sources remain at --root; only generated files go to this temp directory.
            result = build(args.root, target, enemy_database=args.enemy_database)
            for name in result['outputs']:
                require((target / name).read_bytes() == (args.root / name).read_bytes(), 'Generated current bytes differ: ' + name)
    else:
        result = build(args.root, args.output_root, enemy_database=args.enemy_database)
    print(json.dumps(result, ensure_ascii=False))
