"""Rebuild source-bound two-actor boss cycle reading; no runtime simulation."""
from copy import deepcopy
from hashlib import sha256
from html.parser import HTMLParser
from pathlib import Path
import argparse
import json
import re

ROOT = Path(__file__).resolve().parents[1]
PACK = 'research/p3-boss-cycle-310'
DATA = 'rouge/data/boss-cycle-reference.json'
MANIFEST = PACK + '/source-manifest.json'
TARGETS = (('ro6_b_5', 'enemy_2147_shophm', 0), ('ro6_b_5', 'enemy_2148_shorbb', 0))
ENEMIES = ('enemy_2147_shophm', 'enemy_2148_shorbb', 'enemy_2149_shorsm')
FROZEN_HANDOFF_SHA = '6252d3ef3cee23aab3854ae01e3c1a389a555f7ceb8129da91b74dac805a2bd6'
REVIEW_HANDOFF_SHA = '6fc6753177478b9867a96733dc87a6a291f96890794b07e5faa1972642dc6003'
TEMPLATE_SHA = '7ca70588d8c7fc0ff363c9552111fe3924ae9fe59f2d4ca08ee22550195be48c'
PLAYER = PACK + '/final-review/player-reading-data-proposal-grouped.json'
EXTRACTED = PACK + '/final-review/complete-visible-cards-and-tooltips.json'


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
        return one.keys() == two.keys() and all(type(key) is str and same(one[key], two[key]) for key in two)
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
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
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
    return ''.join(visible(child) for child in node.children) + ('\n' if node.tag in ('p', 'li', 'dt', 'dd', 'tr') else '')


def has_class(node, name):
    return name in node.attrs.get('class', '').split()


def verify_documents(blobs, original, extracted, records):
    documents = {}
    for source in records:
        raw = blobs[PACK + '/' + source['file']]
        require(same(pin(raw), {key: source[key] for key in ('sha256', 'bytes')}), 'Complete HTTP source pin differs')
        html = raw.decode('utf8')
        require(source['status'] == 200 and re.search(r'"wgRevisionId"\s*:\s*' + re.escape(source['revision']) + r'\b', html), 'Complete source revision differs')
        documents[source['title']] = Document(html)
    skill_count = ability_count = 0
    for actor, entry in original.items():
        doc = documents[actor]
        cards = [node for node in doc.nodes if has_class(node, 'ak-card__body') and has_class(node, 'skill_card')]
        require(len(cards) == len(entry['cards']), 'Complete original card count differs')
        reviewed = [card for card in extracted['cards'] if card['actor'] == actor]
        require(len(cards) == len(reviewed), 'Reviewed card count differs')
        for index, (node, old, review) in enumerate(zip(cards, entry['cards'], reviewed)):
            require(old['card_index'] == review['card_index'] == index and same(serial(node), old['complete_DOM']), 'Whole card DOM differs')
            title = next((child for child in node.children if isinstance(child, Node) and has_class(child, 'ak-card__title')), None)
            header = visible(title).strip() if title is not None else None
            modes = re.findall(r'\[([^\[\]]+)\]', header or '')
            body = '\n'.join(visible(child).strip() for child in node.children if isinstance(child, Node) and child.tag == 'p')
            require(header == old['complete_visible_header'] == review['complete_visible_header'], 'Full header differs')
            require(modes == old['documented_modes'] == review['documented_mode_labels'], 'Mode labels differ')
            require(body == old['complete_visible_body'] == review['complete_visible_body'], 'Full visible body differs')
            require(visible(node).strip() == review['complete_visible_card'], 'Full reviewed card differs')
            if title is None:
                ability_count += 1
                require(review['kind'] == 'ability', 'Ability must not become an extra skill')
            else:
                skill_count += 1
                require(review['kind'] == 'skill', 'Skill role differs')
        for table in entry['tables']:
            matching = [node for node in doc.nodes if node.tag == 'table' and same(serial(node), table['complete_DOM'])]
            require(len(matching) == 1 and visible(matching[0]).strip() == table['complete_visible_text'], 'Whole original device table DOM differs')
    require((skill_count, ability_count) == (7, 2), 'Seven boss skills and two ability cards required')
    module_doc = documents['源阶方模块']
    tables = [node for node in module_doc.nodes if node.tag == 'table' and has_class(node, 'wikitable')]
    module = extracted['module']
    require(sum(visible(node).strip() == module['complete_visible_table'] for node in tables) == 1, 'Complete module mechanism table differs')
    require(len(module['skill_tables']) == 1, 'Separate complete module skill table required')
    skill_table = module['skill_tables'][0]
    require(sum(visible(node).strip() == skill_table['complete_visible_table'] for node in tables) == 1, 'Complete module skill table differs')
    require('源阶方自身最大生命值8%' in skill_table['complete_visible_table'], 'Complete documented module success effect required')
    return skill_count, ability_count


def build(root=ROOT, output_root=None, *, enemy_database=None, original_level=None):
    root = Path(root)
    output = root if output_root is None else Path(output_root)
    authority_root = output if (output / PACK / 'HANDOFF.json').is_file() else root
    raw_handoff = (authority_root / PACK / 'HANDOFF.json').read_bytes()
    require(sha256(raw_handoff).hexdigest() == FROZEN_HANDOFF_SHA, 'Original research freeze changed')
    handoff = json.loads(raw_handoff)
    blobs = {}
    for name, expected in handoff['files'].items():
        raw = (authority_root / PACK / name).read_bytes()
        require(same(pin(raw), expected), 'Whole original research member changed: ' + name)
        blobs[PACK + '/' + name] = raw
    raw_review = (authority_root / PACK / 'final-review/HANDOFF_FINAL.json').read_bytes()
    require(sha256(raw_review).hexdigest() == REVIEW_HANDOFF_SHA, 'Final independent review freeze changed')
    review = json.loads(raw_review)
    for name, expected in review['files'].items():
        raw = (authority_root / PACK / 'final-review' / name).read_bytes()
        require(same(pin(raw), expected), 'Whole final review member changed: ' + name)
        blobs[PACK + '/final-review/' + name] = raw
    selected = json.loads(blobs[PACK + '/selected-original-records.json'])
    original_cards = json.loads(blobs[PACK + '/complete-document-cards.json'])
    extracted = json.loads(blobs[EXTRACTED])
    proposal = json.loads(blobs[PLAYER])
    records = json.loads(blobs[PACK + '/http-source-records.json'])
    skill_count, ability_count = verify_documents(blobs, original_cards, extracted, records)
    require(proposal['not_a_linear_timeline'] is True and len(proposal['flow_groups']) == 4, 'Condition branches must not become a linear timeline')
    require([topic['id'] for topic in proposal['topics']] == ['flow', 'lorentz', 'cube', 'module'], 'Four complete reading topics required')
    require(len(proposal['skills']) == 7 and len(proposal['documentary_flow']) == 7, 'Complete documentary flow and boss skills required')
    require(same(proposal['primary_full_tuple'], list(TARGETS[0])) and same(proposal['supporting_full_tuple'], list(TARGETS[1])), 'Only the two exact entry identities are supported')
    inputs = {}
    for source in selected['source_files']:
        name = source['file']
        if enemy_database is not None and name.endswith('/enemy_database.json'):
            path = Path(enemy_database)
        elif original_level is not None and name.endswith('/level_rogue6_b-5.json'):
            path = Path(original_level)
        else:
            path = root / name
        raw = path.read_bytes()
        require(same(pin(raw), {key: source[key] for key in ('sha256', 'bytes')}), 'Complete large build authority changed: ' + name)
        inputs[name] = raw
    battle = json.loads(inputs['rouge/data/battle-previews.json'])
    skills = json.loads(inputs['rouge/data/enemy-skill-references.json'])
    database = json.loads(next(raw for name, raw in inputs.items() if name.endswith('/enemy_database.json')))
    level = json.loads(next(raw for name, raw in inputs.items() if name.endswith('/level_rogue6_b-5.json')))
    require(same(level, selected['complete_original_level']), 'Whole original level differs')
    require(same(battle['stages']['ro6_b_5'], selected['complete_canonical_stage']), 'Whole fixed current stage differs')
    for enemy in ENEMIES:
        require(same(next(row for row in database['enemies'] if row['Key'] == enemy), selected['complete_original_enemy_records'][enemy]), 'Whole database enemy record differs: ' + enemy)
        refs = [row for row in level['enemyDbRefs'] if row['id'] == enemy]
        require(len(refs) == 1 and type(refs[0]['level']) is int and refs[0]['level'] == 0 and same(refs, selected['complete_stage_enemyDbRefs'][enemy]), 'Whole stage enemy references differ')
        require(same(skills['definitions'][enemy], selected['complete_skill_definitions'][enemy]), 'Whole skill definition differs')
        require(same(skills['bindings']['ro6_b_5'][enemy + '@0'], selected['complete_skill_bindings'][enemy]), 'Whole selected skill binding differs')
    require('trap_324_shmbmb' in json.dumps(level['predefines'], ensure_ascii=False), 'Original predefined module identity is absent')
    ref = deepcopy(proposal)
    ref['source_player_proposal_kind'] = ref.pop('kind')
    ref['kind'] = 'documented_boss_cycle_reference'
    ref['documentary_source_cards'] = original_cards
    ref['reviewed_complete_documentation'] = extracted
    ref['source_documents'] = records
    ref['player_unknowns'] = ['本局双方当前模式、实际发动与切换时刻。',
        '模块实际数量、分组、位置、是否存活，以及治疗与受伤结果。',
        '首次低于半血是否已经触发，以及之后是否保留。',
        '本局实际目标、路线、位置和结算结果。',
        '当前难度下的完整属性、加成、伤害和实际倒计时。']
    unknown = {**{name: None for name in ('actual_lorentz_mode', 'actual_cube_mode', 'actual_modules',
        'actual_half_hp_gate', 'actual_skill', 'actual_transition', 'actual_elapsed_time', 'actual_target', 'actual_route', 'phase_stats', 'actual_damage')},
        **{name: False for name in ('current_server_verified', 'numerical_phase_model_added', 'run_state_updated', 'inventory_updated', 'modifiers_changed', 'maps_changed')}}
    entry_names = {enemy: next(row['name'] for row in battle['stages']['ro6_b_5']['enemies'] if row['id'] == enemy and type(row['level']) is int and row['level'] == 0) for _, enemy, _ in TARGETS}
    data = {'schema': 'boss_cycle_reference_v1', 'targets': [list(target) for target in TARGETS],
            'entry_names': entry_names, 'reference': ref, 'complete_battle_source': battle['source'],
            'complete_skill_source': skills['source'], 'actual_and_mutation_fields': unknown}
    outputs = {DATA: encoded(data)}
    runtime_names = [PACK + '/' + name for name in ('selected-original-records.json', 'candidate-assessment.json',
        'complete-document-cards.json', 'http-source-records.json', 'lorentz-complete.html', 'cube-complete.html',
        'module-complete.html', 'stage-complete.html', 'final-review/source-review.json',
        'final-review/complete-visible-cards-and-tooltips.json', 'final-review/player-reading-data-proposal-grouped.json')]
    runtime = {DATA: pin(outputs[DATA]), **{name: pin(blobs[name]) for name in runtime_names}}
    template = (authority_root / PACK / 'backend-template.py').read_bytes()
    require(sha256(template).hexdigest() == TEMPLATE_SHA, 'Exact backend template differs')
    build_sources = {name: pin(raw) for name, raw in blobs.items() if name not in runtime}
    build_sources.update({PACK + '/HANDOFF.json': pin(raw_handoff), PACK + '/final-review/HANDOFF_FINAL.json': pin(raw_review), PACK + '/backend-template.py': pin(template)})
    build_sources.update({name: pin(raw) for name, raw in inputs.items()})
    manifest = {'schema': 'boss_cycle_source_manifest_v1', 'data_file': DATA, 'data_sha256': sha256(outputs[DATA]).hexdigest(),
        'targets': [list(target) for target in TARGETS], 'runtime_files': runtime, 'build_authority_files': build_sources,
        'all_runtime_members_required_for_each_target_query': True, 'runtime_full_database_hashing': False,
        'runtime_scope': 'Fresh complete small public source files and full selected current stage/three skill objects; no per-query full large catalogue/database hashing.',
        'build_scope': 'Complete frozen HTML, card DOM, module table, original enemy database, level, battle catalogue and skill table are independently verified before reconstruction.',
        'actual_state_or_numeric_model_added': False}
    outputs[MANIFEST] = encoded(manifest)
    runtime_literal = '{' + ', '.join(repr(name) for name in sorted(runtime)) + '}'
    outputs['rouge/boss_cycle_reference.py'] = template.decode('utf8').replace('__DATA_SHA__', sha256(outputs[DATA]).hexdigest()).replace('__MANIFEST_SHA__', sha256(outputs[MANIFEST]).hexdigest()).replace('__RUNTIME_FILES__', runtime_literal).encode('utf8')
    for name, raw in outputs.items():
        destination = output / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(raw)
    receipt = {'kind': 'SECTION310_SOURCE_BUILD_NOT_PRODUCT_ACCEPTANCE', 'targets': [list(target) for target in TARGETS],
        'boss_skill_cards': skill_count, 'ability_cards': ability_count, 'separate_module_skill_tables': len(extracted['module']['skill_tables']),
        'documentary_flow_records': len(ref['documentary_flow']), 'flow_groups': len(ref['flow_groups']),
        'runtime_source_members': len(runtime), 'numeric_model_added': False, 'outputs': {name: pin(raw) for name, raw in outputs.items()}}
    (output / PACK / 'build-receipt.json').write_bytes(encoded(receipt))
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--output-root', type=Path)
    parser.add_argument('--enemy-database', type=Path)
    parser.add_argument('--original-level', type=Path)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.check:
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            result = build(args.root, target, enemy_database=args.enemy_database, original_level=args.original_level)
            for name in result['outputs']:
                require((target / name).read_bytes() == (args.root / name).read_bytes(), 'Generated bytes differ: ' + name)
    else:
        result = build(args.root, args.output_root, enemy_database=args.enemy_database, original_level=args.original_level)
    print(json.dumps(result, ensure_ascii=False))
