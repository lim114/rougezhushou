"""Build three exact documentary entries; never infer an engine skill binding."""
from copy import deepcopy
from pathlib import Path
from hashlib import sha256
import argparse
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.build_boss_hunt_reference_311 import Document, Node, cls, visible, serial

PACK = 'research/p3-gold-boss-312'
DATA = 'rouge/data/gold-boss-reference.json'
MANIFEST = PACK + '/source-manifest.json'
FROZEN_SHA = '2804ab9fbe9569625b0da82f146e2490135458710b55ce53e54c318c47363409'
TARGETS = (('ro6_b_2', 'enemy_2140_shsgzd', 0), ('ro6_b_2', 'enemy_2142_shsggd', 0),
           ('ro6_b_2_b', 'enemy_2141_shsgz2', 0))
ENEMIES = ('enemy_2140_shsgzd', 'enemy_2141_shsgz2', 'enemy_2142_shsggd')
STAGES = ('ro6_b_2', 'ro6_b_2_b')
NAMES = dict(zip(ENEMIES, ('德莱昂', '“征服者”德莱昂', '赤金条')))
ACTUAL_FIELDS = ('actual_mode', 'actual_plunder_buff', 'actual_gold_present', 'actual_exit',
                 'actual_reward', 'actual_elapsed_time', 'actual_target', 'actual_route',
                 'phase_stats', 'actual_damage')
FALSE_FIELDS = ('current_server_verified', 'numerical_phase_model_added', 'run_state_updated',
                'inventory_updated', 'modifiers_changed', 'maps_changed')


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
        return one.keys() == two.keys() and all(type(k) is str and same(one[k], two[k]) for k in one)
    if type(one) is list:
        return len(one) == len(two) and all(same(a, b) for a, b in zip(one, two))
    return one == two


def build(root=ROOT, output_root=None):
    root = Path(root)
    raw_frozen = (root / PACK / 'frozen-sources.json').read_bytes()
    require(sha256(raw_frozen).hexdigest() == FROZEN_SHA, 'Frozen source authority differs')
    frozen = json.loads(raw_frozen)
    blobs = {PACK + '/frozen-sources.json': raw_frozen}
    for name, expected in frozen['files'].items():
        require('/' not in name and '\\' not in name and ':' not in name and name not in ('.', '..'), 'Unsafe source')
        raw = (root / PACK / name).read_bytes()
        require(same(pin(raw), expected), 'Complete source member differs: ' + name)
        blobs[PACK + '/' + name] = raw
    selected = json.loads(blobs[PACK + '/selected-original-authority.json'])
    raw_sources = {}
    for name, expected in selected['source_files'].items():
        raw = (root / name).read_bytes()
        require(same(pin(raw), expected), 'Original build input differs: ' + name)
        raw_sources[name] = raw
    battle = json.loads(raw_sources['rouge/data/battle-previews.json'])
    skills = json.loads(raw_sources['rouge/data/enemy-skill-references.json'])
    database = json.loads(raw_sources['.cache/game-data/levels/enemydata/enemy_database.json'])
    for field, value in (('complete_battle_source', battle['source']), ('complete_skill_source', skills['source'])):
        require(same(value, selected[field]), 'Whole canonical source differs')
    for eid in ENEMIES:
        require(same(skills['definitions'][eid], selected['complete_skill_definitions'][eid]), 'Definition differs')
        require(same([r for r in database['enemies'] if r['Key'] == eid], selected['complete_original_enemy_records'][eid]), 'Original enemy differs')
    for sid in STAGES:
        stage = battle['stages'][sid]
        require(same(stage, selected['complete_canonical_stages'][sid]), 'Complete stage differs')
        path = '.cache/game-data/levels/' + stage['level_source']['url'].split('/levels/')[1]
        level = json.loads(raw_sources[path])
        require(same(level, selected['complete_original_levels'][sid]), 'Complete original level differs')
        require(same({k: v for k, v in skills['bindings'][sid].items() if k.split('@')[0] in ENEMIES},
                     selected['complete_skill_bindings'][sid]), 'Complete selected bindings differ')
        require(all(row['useDb'] is True for row in level['enemyDbRefs'] if row['id'] in ENEMIES), 'Non-database target requires separate evidence')
    for sid, eid, level in TARGETS:
        require(len([e for e in battle['stages'][sid]['enemies'] if e['id'] == eid and type(e['level']) is int and e['level'] == level]) == 1,
                'Exact canonical target must be unique')
    require(not any(e['id'] == ENEMIES[2] for e in battle['stages']['ro6_b_2_b']['enemies']),
            'Preserve the fixed gold-reference absence; do not infer runtime absence')
    extracts = json.loads(blobs[PACK + '/complete-cards.json'])
    records = json.loads(blobs[PACK + '/http-source-records.json'])
    require(len(records) == 5 and set(extracts) == {r['title'] for r in records}, 'Five full source pages required')
    counts = {'skills': 0, 'abilities': 0}
    for record in records:
        raw = blobs[PACK + '/' + record['file']]
        require(same(pin(raw), {k: record[k] for k in ('sha256', 'bytes')}), 'Actual response pin differs')
        require(record['status'] == 200 and re.search(rb'"wgRevisionId"\s*:\s*' + str(record['revision']).encode() + rb'\b', raw), 'Observed revision differs')
        doc = Document(raw.decode('utf8'))
        nodes = [n for n in doc.nodes if cls(n, 'ak-card__body') and cls(n, 'skill_card')]
        cards = extracts[record['title']]['cards']
        require(len(nodes) == len(cards) and same(extracts[record['title']]['source'], record), 'Whole card selection differs')
        for node, card in zip(nodes, cards):
            title = next((c for c in node.children if cls(c, 'ak-card__title')), None)
            header = visible(title).strip() if title else None
            require(same(serial(node), card['complete_DOM']) and header == card['header'], 'Full card DOM/header differs')
            require(visible(node).strip() == card['full'] and same([visible(c).strip() for c in node.children if isinstance(c, Node) and c.tag == 'p'], card['paragraphs']), 'Full card text differs')
            counts['skills' if header else 'abilities'] += 1
    require(counts == {'skills': 6, 'abilities': 3}, 'Six skills and three abilities required')
    proposal = json.loads(blobs[PACK + '/player-reading.json'])
    require([t['id'] for t in proposal['topics']] == ['conditions', 'flight', 'gold', 'plunder_exit'], 'Complete four-topic scope required')
    for topic in proposal['topics']:
        for evidence in topic['evidence']:
            require(evidence['actor'] in NAMES.values(), 'Unknown document actor')
            require(all(type(i) is int and 0 <= i < len(extracts[evidence['actor']]['cards']) for i in evidence['card_indices']), 'Invalid exact source card')
    runtime = {key: deepcopy(selected[key]) for key in ('complete_battle_source', 'complete_skill_source', 'complete_canonical_stages', 'complete_skill_definitions', 'complete_skill_bindings')}
    blobs[PACK + '/runtime-selected-authority.json'] = encoded(runtime)
    refs = {}
    for sid, eid, level in TARGETS:
        ref = deepcopy(proposal)
        ref.update(stage_id=sid, enemy_id=eid, level=level, entry_name=NAMES[eid], stage_name=battle['stages'][sid]['name'])
        ref['version_notice'] = proposal['version_notes'][eid]
        ref['skills'] = []
        # Each exact boss retains its own full cards; gold has no documented skill card.
        actor = NAMES[eid]
        for i, card in enumerate(extracts[actor]['cards']):
            if card['header']:
                ref['skills'].append({'name': card['header'].split('\n')[0], 'full_header': card['header'],
                    'text': '\n'.join(card['paragraphs']), 'topic_id': 'plunder_exit' if i == 2 else 'flight',
                    'source_actor': actor, 'card_index': i})
        refs[sid + '/' + eid] = ref
    data = {'schema': 'gold_boss_reference_v1', 'targets': [list(t) for t in TARGETS], 'references': refs,
            'complete_document_cards': extracts, 'actual_and_mutation_fields': {**{k: None for k in ACTUAL_FIELDS}, **{k: False for k in FALSE_FIELDS}},
            'no_engine_skill_mapping_added': True, 'whole_card_counts': counts}
    blobs[DATA] = encoded(data)
    # Large raw database/levels are build-only. Every public documentary member is rechecked at runtime.
    manifest = {'schema': 'gold_boss_source_manifest_v1', 'data_file': DATA, 'data_sha256': sha256(blobs[DATA]).hexdigest(),
                'frozen_sha256': FROZEN_SHA, 'runtime_files': {n: pin(raw) for n, raw in sorted(blobs.items())},
                'runtime_full_database_hashing': False, 'all_runtime_members_required_for_each_target_query': True}
    blobs[MANIFEST] = encoded(manifest)
    if output_root is not None:
        for name, raw in blobs.items():
            path = Path(output_root) / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
    return blobs


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--output-root', type=Path)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    files = build(args.root, args.output_root)
    if args.check:
        for name, raw in files.items():
            require((args.root / name).read_bytes() == raw, 'Published generated member differs: ' + name)
    print(json.dumps({'public_members_rebuilt': len(files), 'whole_document_cards': {'skills': 6, 'abilities': 3},
                      'data_sha256': sha256(files[DATA]).hexdigest(), 'manifest_sha256': sha256(files[MANIFEST]).hexdigest()}, ensure_ascii=False))
