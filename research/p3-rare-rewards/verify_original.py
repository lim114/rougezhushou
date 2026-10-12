"""Independently compare the public excerpts against complete pinned JSON bytes."""
from pathlib import Path
import argparse
import hashlib
import json


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def checked(path, source):
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != source['sha256'] or len(raw) != source['bytes']:
        raise ValueError('Original source byte identity failed: ' + path.name)
    return json.loads(raw)


def verify(cache):
    here = Path(__file__).parent
    original = read(here / 'selected-original.json')
    topic = checked(cache / 'roguelike_topic_table.json', original['topic_source'])['details']['rogue_6']
    db = checked(cache / 'levels/enemydata/enemy_database.json', original['database_source'])
    assert topic['gameConst']['mimicEnemyIds'] == original['mimic_ids']
    identities = {}
    for i, row in enumerate(db['enemies']):
        if row['Key'] in original['mimic_ids']:
            identities[row['Key']] = {'source_selector': f'$.enemies[{i}]', 'raw': row}
    assert identities == original['database_identities']
    assert set(topic['stages']) == set(original['stages'])
    for sid, row in topic['stages'].items():
        assert original['stages'][sid] == {'id': sid, 'name': row['name'],
            'difficulty': row['difficulty'], 'level_key': row['levelId'].lower() + '.json',
            'source_selector': '$.details.rogue_6.stages.' + sid}
    queue_count = 0
    for key, excerpt in original['levels'].items():
        raw = checked(cache / 'levels' / key, excerpt['source'])
        queues = []
        for wi, wave in enumerate(raw.get('waves') or []):
            for fi, fragment in enumerate(wave.get('fragments') or []):
                actions = fragment.get('actions') or []
                if any(a.get('actionType') == 'SPAWN' and a.get('key') in original['mimic_ids'] for a in actions):
                    queues.append({'source_selector': f'$.waves[{wi}].fragments[{fi}]', 'raw_actions': actions})
        for branch_id, branch in (raw.get('branches') or {}).items():
            for pi, phase in enumerate(branch.get('phases') or []):
                actions = phase.get('actions') or []
                if any(a.get('actionType') == 'SPAWN' and a.get('key') in original['mimic_ids'] for a in actions):
                    queues.append({'source_selector': '$.branches[' + json.dumps(branch_id) + f'].phases[{pi}]',
                        'raw_actions': actions})
        assert queues == excerpt['queues_with_rare_spawns']
        refs = [{'source_selector': f'$.enemyDbRefs[{i}]', 'raw': row}
            for i, row in enumerate(raw.get('enemyDbRefs') or []) if row.get('id') in original['mimic_ids']]
        assert refs == excerpt['enemy_db_refs']
        initial = [{'source_selector': f'$.enemies[{i}]', 'raw': row}
            for i, row in enumerate(raw.get('enemies') or [])
            if isinstance(row, dict) and (row.get('id') in original['mimic_ids'] or row.get('enemyId') in original['mimic_ids'])]
        assert initial == excerpt['initial_enemy_records']
        queue_count += len(queues)
    return {'status': 'PASS_FIXED_ORIGINAL_EXCERPTS', 'game_commit': original['game_commit'],
        'topic_sha256': original['topic_source']['sha256'], 'database_sha256': original['database_source']['sha256'],
        'mimic_identities': len(identities), 'stages': len(original['stages']),
        'full_original_level_bytes': len(original['levels']), 'exact_containing_queues': queue_count,
        'short_documented_quantity_source_native_verified': False,
        'actual_server_reward_script_verified': False, 'actual_spawn_or_grants_verified': False,
        'game_operations': 0, 'private_state_writes': 0, 'chat_messages': 0}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cache', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = verify(args.cache)
    if args.output:
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(result))
