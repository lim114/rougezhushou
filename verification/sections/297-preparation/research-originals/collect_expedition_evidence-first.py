"""Cache-only evidence/actual read-only API inspection, not product acceptance."""
from pathlib import Path
from datetime import datetime, timezone
from copy import deepcopy
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


def pin(path):
    raw = (ROOT / path).read_bytes()
    return {'path': path, 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}


def main():
    from bs4 import BeautifulSoup
    from rouge.event_planning import choice_resources
    from rouge.player_node_information import node_information_text

    paths = ['.cache/p3-287-event-research/fixed-game-topic.json',
        'research/p3-choice-recruitment-290/prts-events-427904.html',
        'research/p3-choice-recruitment-290/prts-events-440271.html',
        'research/p3-stage-context/community-main.html',
        'rouge/data/node-catalog.json', 'rouge/event_planning.py',
        'rouge/player_node_information.py', 'rouge/node_catalog.py']
    source_before = {path: pin(path) for path in paths}
    fixed = json.loads((ROOT / paths[0]).read_bytes())['details']['rogue_6']
    raw_catalog = json.loads((ROOT / 'rouge/data/node-catalog.json').read_bytes())
    event = next(e for e in raw_catalog['events'] if e['id'] == 'community_group_024')
    ids = ['choice_ro6_scout_1', 'choice_ro6_scout_3', 'choice_ro6_scout_2', 'choice_ro6_scout_4']
    scenes = ['scene_ro6_scout_enter', 'scene_ro6_scout_1', 'scene_ro6_scout_2', 'scene_ro6_scout_3']
    constants = {key: deepcopy(value) for key, value in fixed['gameConst'].items()
                 if 'exped' in key.lower()}
    detail = {key: deepcopy(value) for key, value in fixed['detailConst'].items()
              if 'exped' in key.lower()}
    beacon = fixed['gameConst']['expedEndingRelic']
    dom = {}
    for path in paths[1:3]:
        soup = BeautifulSoup((ROOT / path).read_bytes(), 'html.parser')
        start = soup.find('div', class_='scene', attrs={'data-name': '未涉足之树'})
        assert start is not None
        group = start.find_parent('div', class_='IS-event-data')
        rows = []
        for number, scene in enumerate(group.find_all('div', class_='scene')):
            rows.append({'number': number, 'attributes': dict(scene.attrs),
                'text': scene.get_text(' ', strip=True), 'html': str(scene),
                'choices': [{'attributes': dict(c.attrs), 'text': c.get_text(' ', strip=True),
                             'html': str(c)} for c in scene.find_all('div', class_='choose')]})
        dom[path] = rows
    soup = BeautifulSoup((ROOT / paths[3]).read_bytes(), 'html.parser')
    excerpts = []
    for element in soup.select('dd, li'):
        text = element.get_text(' ', strip=True)
        if ('干员将在下一层开始时归来' in text or '尝试探索树的源头' in text or
            '无法在先行一步中被选择' in text or
            ('干员归来时还可获得随机加工品' in text) or
            '可不选择干员并“确认”重新选择选项' in text):
            excerpts.append({'tag': element.name, 'text': text, 'html': str(element)})
    observations = []
    for scene in event['scenes']:
        result = choice_resources(event['id'], scene['key'])
        observations.append({'scene_key': scene['key'], 'result': result})
    player = node_information_text({'kind': 'event', 'record': event})
    source_after = {path: pin(path) for path in paths}
    assert source_before == source_after
    output = {'kind': 'p3-expedition-candidate-source-and-readonly-observation',
        'checked_at_utc': datetime.now(timezone.utc).isoformat(),
        'sources_before': source_before, 'sources_after': source_after,
        'primary_commit': 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add',
        'primary_choices': {key: fixed['choices'][key] for key in ids},
        'primary_scenes': {key: fixed['choiceScenes'][key] for key in scenes},
        'gameConst': constants, 'detailConst': detail,
        'beacon_item': fixed['items'].get(beacon),
        'beacon_relic': fixed['relics'].get(beacon),
        'beacon_relic_params': fixed['relicParams'].get(beacon),
        'community_event': event, 'pinned_event_dom': dom,
        'pinned_main_excerpts': excerpts,
        'actual_public_readonly_observation': observations,
        'actual_player_text': player,
        'operation_scope': {'production_writes': 0, 'private_reads_or_writes': 0,
            'Qt': 0, 'game': 0, 'chat': 0, 'Git_mutation': 0},
        'is_product_acceptance': False}
    dest = HERE / 'expedition-evidence-and-observation.json'
    dest.write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps({'output': str(dest.relative_to(ROOT)), 'sha256': hashlib.sha256(dest.read_bytes()).hexdigest(),
        'bytes': dest.stat().st_size, 'sources_unchanged': source_before == source_after,
        'event_dom_scene_counts': {key: len(value) for key, value in dom.items()},
        'pinned_main_excerpt_count': len(excerpts),
        'explanatory_hope_rows': [row for scene in observations for row in scene['result']['rows']
            if row['presentation_role'] == 'explanatory_text' and row['resource_references']],
        'beacon_name': output['beacon_item']['name']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
