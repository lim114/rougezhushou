"""Reconstruct fixed choice documents from complete pinned public records.

Default compares existing outputs. --write only writes DATA and final manifest
under the explicit output root. No Qt, project imports, network or private state.
"""
import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
PACK = 'research/p3-curiosity-node-rules-304'
AUTHORITY_CONFIG = PACK + '/source-authority.json'
AUTHORITY_SHA256 = 'b1fa5e5046696d27df40094aa851b642a447ed6b791c1a5b116b850bb1576d70'  # Filled from the preserved revision3 source handoff.
SELECTED = PACK + '/selected-authority-records.json'
RULE_MAP = PACK + '/choice-rule-map.json'
DATA = 'rouge/data/curiosity-node-rules.json'
MANIFEST = PACK + '/source-manifest.json'
TOPIC = 'research/p3-future-region-effects-300/game-topic-complete.json'
PRIOR = 'verification/sections/301-preparation/future-notes-and-ritual-research/complete-candidate-originals-and-DOM.json'
CATALOG = 'rouge/data/node-catalog.json'
CATALOG_SHA256 = '7df1d94bb69650eb19fc811af661e54d44bf07d72b1c0793de511adc1b2e915d'
EVENT_IDS = ('community_group_030', 'community_group_031')
IDENTITIES = (
    ('community_group_030', 'community_group_030:scene:0', 'community_group_030:scene:0:choice:0', ['choice_ro6_end1_1']),
    ('community_group_030', 'community_group_030:scene:0', 'community_group_030:scene:0:choice:1', ['choice_ro6_end1_2']),
    ('community_group_031', 'community_group_031:scene:0', 'community_group_031:scene:0:choice:0', ['choice_ro6_end2_1', 'choice_ro6_end2_4']),
    ('community_group_031', 'community_group_031:scene:0', 'community_group_031:scene:0:choice:1', ['choice_ro6_end2_2']),
    ('community_group_031', 'community_group_031:scene:2', 'community_group_031:scene:2:choice:0', ['choice_ro6_end2_3']),
)
ACTUAL_FIELDS = ('actual_choice', 'actual_node_id', 'actual_marker', 'actual_transformation',
                 'actual_revisit', 'actual_consumed', 'actual_reward', 'actual_quantity', 'actual_eligible')
RELATED = {'stage_id': 'ro6_b_5', 'title': '混沌源阶理论', 'reference_only': True, 'immediate_transition': None}


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf8')


def pin(raw):
    return {'sha256': sha256(raw).hexdigest(), 'bytes': len(raw)}


def read(root, relative):
    path = PurePosixPath(relative)
    if path.is_absolute() or '..' in path.parts or '\\' in relative or ':' in relative:
        raise ValueError('Fixed public relative path required.')
    target = root.joinpath(*path.parts)
    if target.is_symlink() or not target.resolve().is_relative_to(root.resolve()):
        raise ValueError('Fixed source escaped root.')
    return target.read_bytes()


def same(value, expected):
    if type(value) is not type(expected): return False
    if type(expected) is dict:
        return value.keys() == expected.keys() and all(same(value[k], expected[k]) for k in value)
    if type(expected) is list:
        return len(value) == len(expected) and all(same(a, b) for a, b in zip(value, expected))
    return value == expected


def unknowns():
    return {**dict.fromkeys(ACTUAL_FIELDS), 'inventory_updated': False,
            'calculation_applied': False, 'run_state_updated': False}


def reconstruct(repo_root, source_root):
    config_raw = read(source_root, AUTHORITY_CONFIG)
    assert pin(config_raw)['sha256'] == AUTHORITY_SHA256, 'Fixed source-authority bytes changed.'
    config = json.loads(config_raw)
    assert config['schema'] == 'curiosity-node-rules-source-authority-v1'
    assert config['selected_whole_records_file'] == SELECTED
    assert config['current_server_or_callback_verified'] is False
    source_raws = {AUTHORITY_CONFIG: config_raw}
    for name, expected in config['files'].items():
        raw = read(source_root, name)
        assert same(pin(raw), expected), name
        source_raws[name] = raw
    for name, expected in config['build_authority_files'].items():
        raw = read(repo_root, name)
        assert same(pin(raw), expected), name
        source_raws[name] = raw
    current_raw = read(repo_root, CATALOG)
    assert pin(current_raw)['sha256'] == CATALOG_SHA256
    source_raws[CATALOG] = current_raw
    selected = json.loads(source_raws[SELECTED]); rules = json.loads(source_raws[RULE_MAP])
    game = json.loads(source_raws[TOPIC])['details']['rogue_6']
    prior = json.loads(source_raws[PRIOR])
    current = {key: next(event for event in json.loads(current_raw)['events'] if event['id'] == key) for key in EVENT_IDS}
    assert same(selected['complete_current_events'], current)
    assert same(current, {key: prior['complete_events'][key] for key in EVENT_IDS})
    assert same(selected['source_pins'], config['build_authority_files'])
    assert selected['game_commit'] == 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'
    assert selected['existing_battle_entry_not_new'] is True
    assert selected['exact_battle_title'] == RELATED['title']
    for key, value in selected['complete_original_choices'].items():
        assert same(value, game['choices'][key]) and same(value, prior['complete_original_choices'][key]), key
    for key, value in selected['complete_original_scenes'].items():
        assert same(value, game['choiceScenes'][key]) and same(value, prior['complete_original_scenes'][key]), key
    for selected_key, primary_key in (('complete_items', 'items'), ('complete_relics', 'relics')):
        for key, value in selected[selected_key].items():
            assert same(value, game[primary_key][key]) and same(value, prior[selected_key][key]), key
    assert len(selected['complete_original_choices']) == 6 and len(selected['complete_original_scenes']) == 6
    assert len(selected['complete_items']) == len(selected['complete_relics']) == 14
    assert same(selected['complete_related_stage'], game['stages']['ro6_b_5'])
    assert same(selected['complete_ending_documentation'], prior['main_complete_ending_blocks']['end2'])
    assert same(selected['complete_catalog_DOMs'], {
        revision: {key: prior['event_complete_DOMs'][revision][key] for key in EVENT_IDS}
        for revision in ('427904', '440271')})
    assert rules['schema'] == 'curiosity_node_choice_rule_map_v1' and len(rules['choices']) == 5
    context = rules['node_context_reference']
    assert type(context['documented_main_floor']) is int and context['documented_main_floor'] == 5 and context['actual_node_ids'] is None
    document = selected['complete_ending_documentation']['text']
    for ref in context['source_refs']:
        assert ref['text'] in document
    rows = []
    for rule, identity in zip(rules['choices'], IDENTITIES):
        event_id, scene_key, choice_key, original_ids = identity
        assert (rule['event_id'], rule['scene_key'], rule['choice_key']) == identity[:3]
        assert rule['reference_id'] == choice_key and rule['original_choice_ids'] == original_ids
        event = current[event_id]
        scene = next(scene for scene in event['scenes'] if scene['key'] == scene_key)
        choice = next(choice for choice in scene['choices'] if choice['key'] == choice_key)
        assert rule['choice_title'] == choice['title'] and rule['choice_description'] == choice['description']
        assert rule['condition_text'] == choice['conditional'] and choice['game_choice_ids'] == original_ids
        expected_related = RELATED if choice_key in (IDENTITIES[2][2], IDENTITIES[4][2]) else None
        assert same(rule['related_stage_reference'], expected_related)
        for entry in rule['documented_rules']:
            assert set(entry) == {'rule_id', 'title', 'text', 'source_refs'} and entry['source_refs']
            for ref in entry['source_refs']:
                if ref.get('selector') == 'main_complete_ending_blocks.end2.text':
                    assert ref['text'] in document
                elif ref.get('selector') == 'exact_five_choice_rows':
                    assert ref['choice_key'] == choice_key and ref['file'] == SELECTED
                else:
                    raise AssertionError('Unbound rule source selector.')
        originals = {key: selected['complete_original_choices'][key] for key in original_ids}
        expected_source_row = {'event_id': event_id, 'scene_key': scene_key, 'choice_key': choice_key,
                               'complete_community_choice': choice, 'complete_original_choice_candidates': originals,
                               'original_choice_candidate_selection_unknown': len(original_ids) > 1}
        assert same(selected['exact_five_choice_rows'][len(rows)], expected_source_row)
        rows.append({**deepcopy(rule), 'scene_number': event['scenes'].index(scene) + 1,
                     'choice_number': scene['choices'].index(choice) + 1,
                     'catalog_choice': choice, 'original_choices': originals,
                     'original_choice_candidate_selection_unknown': len(original_ids) > 1, **unknowns()})
    assert rows[2]['original_choices']['choice_ro6_end2_1']['displayData']['itemId'] == 'rogue_6_end_2_change'
    assert rows[2]['original_choices']['choice_ro6_end2_4']['displayData']['itemId'] is None
    packet = {'schema': 'curiosity_node_rules_v1', 'event_ids': list(EVENT_IDS), 'expected_events': current,
              'choices': rows, 'node_context_reference': context,
              'complete_original_choices': selected['complete_original_choices'],
              'complete_original_scenes': selected['complete_original_scenes'],
              'configuration_references': {'items': selected['complete_items'], 'relics': selected['complete_relics'],
                                           'related_stage': selected['complete_related_stage']},
              **{key: rules[key] for key in ('source', 'source_reference', 'notice', 'unknowns')},
              'original_entry_restored': False, 'current_server_verified': False, **unknowns()}
    result = {DATA: encoded(packet)}
    all_raws = {**source_raws, **result}
    runtime_names = (DATA, SELECTED, RULE_MAP, AUTHORITY_CONFIG, CATALOG)
    runtime = {name: pin(all_raws[name]) for name in runtime_names}
    manifest = {'schema': 'curiosity_node_rules_source_manifest_v1', 'event_ids': list(EVENT_IDS),
                'data_file': DATA, 'data_sha256': pin(result[DATA])['sha256'],
                'selected_authority_file': SELECTED, 'rule_map_file': RULE_MAP,
                'files': {name: pin(raw) for name, raw in sorted(all_raws.items())},
                'runtime_files': runtime,
                'build_authority_files': {name: pin(raw) for name, raw in sorted(all_raws.items()) if name not in runtime},
                'runtime_reads_complete_primary_table': False, 'runtime_verifies_complete_original_bytes': False,
                'all_runtime_members_required_for_each_target_query': True,
                'counts': {'events': 2, 'community_choices': 5, 'primary_choice_candidates': 6,
                           'complete_scenes': 6, 'complete_items': 14, 'complete_relics': 14,
                           'related_choice_references': 2, 'new_battle_links': 0},
                'source': rules['source']}
    result[MANIFEST] = encoded(manifest)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', type=Path, default=ROOT)
    parser.add_argument('--source-root', type=Path)
    parser.add_argument('--output-root', type=Path)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    source_root = args.source_root or args.repo_root
    output_root = args.output_root or args.repo_root
    result = reconstruct(args.repo_root.resolve(), source_root.resolve())
    for name, raw in result.items():
        target = output_root / name
        if args.write:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
        else:
            assert target.read_bytes() == raw, name
    manifest = json.loads(result[MANIFEST])
    print(json.dumps({'kind': 'SOURCE_BUILD_ONLY_NOT_PRODUCT_OR_NATIVE_ACCEPTANCE', 'write': args.write,
                      'counts': manifest['counts'], 'runtime_files': len(manifest['runtime_files']),
                      'runtime_bytes_with_manifest': sum(value['bytes'] for value in manifest['runtime_files'].values()) + len(result[MANIFEST]),
                      'data_sha256': pin(result[DATA])['sha256'], 'manifest_sha256': pin(result[MANIFEST])['sha256'],
                      'Qt_tests_network_run_or_game_operations': False}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
