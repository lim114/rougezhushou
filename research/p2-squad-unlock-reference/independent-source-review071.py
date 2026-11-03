"""Independent read-only source checks; writes only its external receipt."""
import collections
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent
BASE = ROOT / 'baseline'
RAW = Path('/workspace/.continuation/p2-after-055-audit/relic-scope/roguelike_topic_table.json')
EXPECTED_SHA = 'f5867e55d09472253083486174aa47bd94dd48b07684b74b60a5b29ca00eda86'
COMMIT = '59531ff2e9475410a84ef0e60836f89793fd35a9'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


freeze = json.loads((ROOT / 'baseline-freeze.json').read_text())
assert freeze['frozen_commit'] == COMMIT and freeze['snapshot_includes_root_wip'] is False
assert freeze['file_count'] == len(freeze['files']) == 2179
committed_entries = subprocess.check_output([
    'git', '-C', '/workspace/rougezhushou', 'ls-tree', '-r', '-z', COMMIT, '--', *freeze['archive_paths']
]).split(b'\0')
committed_blobs = {}
for entry in committed_entries:
    if not entry:
        continue
    meta, name = entry.split(b'\t', 1)
    mode, kind, blob_sha = meta.split()
    assert kind == b'blob'
    committed_blobs[name.decode()] = blob_sha.decode()
assert set(committed_blobs) == set(freeze['files'])
for name, expected in freeze['files'].items():
    data = (BASE / name).read_bytes()
    assert len(data) == expected['bytes'] and hashlib.sha256(data).hexdigest() == expected['sha256'], name
    assert hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() == committed_blobs[name], name

raw_bytes = RAW.read_bytes()
assert len(raw_bytes) == 17943244
assert hashlib.sha256(raw_bytes).hexdigest() == EXPECTED_SHA
raw = json.loads(raw_bytes)
detail = raw['details']['rogue_6']
common = raw['customizeData']['rogue_6']['commonDevelopment']
config = json.loads((BASE / 'rouge/data/run-config.json').read_text())
catalog = json.loads((BASE / 'rouge/data/technology-reference.json').read_text())
assert config['source_sha256'] == catalog['source']['sha256'] == EXPECTED_SHA
assert config['commit'] == catalog['source']['commit'] == 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'
assert all(catalog[key] == value for key, value in common.items())
assert len(common['developments']) == 57
assert dict(collections.Counter(node['nodeType'] for node in common['developments'].values())) == {'NORMAL': 33, 'KEY': 21, 'DIFFICULTY': 3}
assert len(common['developmentsTokens']) == 9
assert len(common['developmentRawTextGroup']) == 6
assert {key: gate['enableGrade'] for key, gate in common['developmentsDifficultyNodeInfos'].items()} == {
    'rogue_6_difficulty_1': 3, 'rogue_6_difficulty_2': 6, 'rogue_6_difficulty_3': 9}

for squad_id, squad in config['squads'].items():
    expected = {**detail['bandRef'][squad_id], **detail['items'][squad_id], 'buffs': detail['relics'][squad_id]['buffs']}
    assert squad == expected, squad_id
assert len(config['squads']) == len(detail['bandRef']) == 22

selected = {}
for squad_id, variant in detail['bandRef'].items():
    if variant['bandLevel'] != 1:
        continue
    item = detail['items'][squad_id]
    condition = item['unlockCondDesc']
    candidates = [
        (node_id, node) for node_id, node in common['developments'].items()
        if condition == '生命游戏中激活“' + node['buffName'] + '”'
        and '“' + item['name'] + '”效果提升' in node['rawDesc']
    ]
    if squad_id == 'rogue_6_band_22':
        assert condition == '机械师提升至精英二阶段' and candidates == []
        node_id = None
        node = None
    else:
        assert len(candidates) == 1, (squad_id, candidates)
        node_id, node = candidates[0]
    selected[squad_id] = {
        'variant': variant, 'name': item['name'], 'original_condition': condition,
        'condition_selector': '$.details.rogue_6.items.' + squad_id + '.unlockCondDesc',
        'technology_id_by_exact_forward_and_reverse_text': node_id,
        'original_node': node,
        'original_gate': common['developmentsDifficultyNodeInfos'].get(node_id),
    }
assert len(selected) == 7
assert {key: value['technology_id_by_exact_forward_and_reverse_text'] for key, value in selected.items() if value['technology_id_by_exact_forward_and_reverse_text']} == {
    'rogue_6_band_2': 'rogue_6_difficulty_1', 'rogue_6_band_5': 'rogue_6_difficulty_2',
    'rogue_6_band_7': 'rogue_6_difficulty_3', 'rogue_6_band_16': 'rogue_6_outbuff_43',
    'rogue_6_band_18': 'rogue_6_outbuff_45', 'rogue_6_band_20': 'rogue_6_outbuff_44',
}

ids = set(common['developments'])
binding_keys = []


def inspect_dict_keys(value, path):
    if isinstance(value, dict):
        for key, child in value.items():
            if key in ids:
                binding_keys.append(path + '.' + key)
            inspect_dict_keys(child, path + '.' + str(key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            inspect_dict_keys(child, path + '[' + str(index) + ']')


inspect_dict_keys(detail, '$.details.rogue_6')
assert binding_keys == []
assert len(detail['charBuffData']) == 15 and len(detail['squadBuffData']) == 0

receipt = {
    'status': 'source_review_passed_final_patch_pending',
    'baseline_commit': COMMIT,
    'baseline_public_files_checked_against_manifest_and_actual_committed_git_blobs': 2179,
    'baseline_contains_no_root_working_tree_files': True,
    'raw_path': str(RAW), 'raw_bytes': len(raw_bytes), 'raw_sha256': EXPECTED_SHA,
    'exact_22_squad_source_composites': True,
    'exact_common_development_projection': True,
    'node_count': 57, 'node_types': {'NORMAL': 33, 'KEY': 21, 'DIFFICULTY': 3},
    'token_count': 9, 'raw_text_group_count': 6, 'gate_count': 3,
    'strengthened_conditions': selected,
    'details_development_id_dictionary_key_bindings': binding_keys,
    'details_char_buff_records': 15, 'details_squad_buff_records': 0,
    'bounded_conclusion': 'Original item text and development text establish six condition-reference links, plus mechanist E2 text. They do not establish account unlock state, actual activation, AND/OR prerequisites, attribute layers, or mode execution semantics.',
    'source_files_sha256': {name: sha(BASE / name) for name in ('rouge/data/run-config.json', 'rouge/data/technology-reference.json', 'rouge/technology.py', 'research/p2-technology/NOTE.md')},
    'no_tracked_edits': True, 'no_private_state_reads': True, 'no_wine_or_gui': True,
}
output = ROOT / 'independent-source-review071.json'
output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'status': receipt['status'], 'conditions': len(selected), 'technology_links': 6,
                  'nodes': 57, 'gates': 3, 'receipt_sha256': sha(output)}, ensure_ascii=False))
