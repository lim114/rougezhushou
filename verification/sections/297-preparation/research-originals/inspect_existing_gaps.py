"""Pure existing public-source inventory for a proposed P3 section, not a test."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def pin(name):
    raw = (ROOT / name).read_bytes()
    return {'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}


def main():
    catalog = json.loads((ROOT / 'rouge/data/node-catalog.json').read_bytes())
    rewards = json.loads((ROOT / 'rouge/data/node-reward-reference.json').read_bytes())
    auxiliary = json.loads((ROOT / 'research/p3-auxiliary-mechanisms/selected-original.json').read_bytes())
    renderers = []
    for bundle in auxiliary['native_sources']:
        for prefab in bundle['selected_prefabs']:
            objects = {o['path_id']: o for o in prefab['objects']}
            renderers.append({'asset': prefab['asset_path'], 'sprite_renderers': [
                {'object_path_id': o['path_id'], 'game_object_name': objects[o['data']['m_GameObject']['m_PathID']]['data']['m_Name'],
                 'sprite_pointer': o['data'].get('m_Sprite')} for o in objects.values() if o['class_id'] == 212]})
    selections = []
    for event in catalog['events']:
        rows = []
        for scene in event['scenes']:
            for choice in scene['choices']:
                text = ' '.join(str(choice.get(k) or '') for k in ('title', 'description', 'conditional'))
                if any(w in text for w in ('获得【', '获得〖', '获得“', '获得「', '获得收藏品', '获得加工品', '解锁')):
                    rows.append({'scene_key': scene['key'], 'choice': choice})
        if rows:
            selections.append({'event_id': event['id'], 'title': event['title'], 'rows': rows})
    output = {'source_pins': {name: pin(name) for name in (
        'PROJECT_PROGRESS.md', 'rouge/data/node-catalog.json', 'rouge/data/node-reward-reference.json',
        'research/p3-auxiliary-mechanisms/selected-original.json',
        '.cache/p3-auxiliary-images-research/git-attempt2/readback-receipt.json')},
        'old_auxiliary_sprite_renderers': renderers,
        'selected_named_result_choices': selections,
        'existing_named_reward_records': rewards['event_rewards'],
        'peeking_event': next(e for e in catalog['events'] if e['id'] == 'community_group_031'),
        'not_a_product_check': True, 'production_Qt_Git_game_chat_private_operations': 0}
    destination = HERE / 'existing-gap-inventory.json'
    with destination.open('x', encoding='utf8') as stream:
        stream.write(json.dumps(output, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'named_reward_records': len(rewards['event_rewards']),
        'documented_item_choice_candidates': len(selections),
        'old_auxiliary_sprite_renderers': renderers,
        'peeking_scenes': len(output['peeking_event']['scenes']),
        'output_sha256': hashlib.sha256(destination.read_bytes()).hexdigest()}, ensure_ascii=False))


if __name__ == '__main__':
    main()
