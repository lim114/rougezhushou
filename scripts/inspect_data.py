import json
from pathlib import Path

root = Path(__file__).resolve().parents[1] / '.cache' / 'game-data'
def read(name):
    return json.loads((root / f'{name}.json').read_text(encoding='utf-8'))
chars, skills, rogue = read('character_table'), read('skill_table'), read('roguelike_topic_table')
for char_id, char in chars.items():
    if char.get('name') in ['凯尔希·思衡托', '凛御银灰', '机械师']:
        print(char_id, char['name'], [(p['maxLevel'], p['attributesKeyFrames'][-1]['data']['atk'], p['attributesKeyFrames'][-1]['data']['baseAttackTime']) for p in char['phases']])
        for s in char['skills']:
            level = skills[s['skillId']]['levels'][-1]
            print(s['skillId'], level['name'], 'duration', level['duration'], 'bb', level['blackboard'])
        print('talents', [(c.get('name'), c.get('description'), c.get('blackboard')) for t in char.get('talents',[]) for c in t['candidates'] if c['unlockCondition']['phase']=='PHASE_2' and c['requiredPotentialRank']==0])
print('rogue keys', list(rogue))
for key, value in rogue.items():
    print(key, list(value)[:12] if isinstance(value,dict) else type(value).__name__)
