"""Pin difficulty/squad identities and source descriptions from the game snapshot."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'.cache/game-data/roguelike_topic_table.json'
details=json.loads(source.read_text(encoding='utf-8'))['details']['rogue_6']
data={'commit':'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add',
    'source_url':'https://github.com/Kengxxiao/ArknightsGameData/blob/a550f5e048bb94e7cdefc6eb97a4091f0c4c7add/zh_CN/gamedata/excel/roguelike_topic_table.json',
    'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
    'difficulties':{str(d['grade']):d for d in details['difficulties'] if d['modeDifficulty']=='NORMAL'},
    'other_modes':[d for d in details['difficulties'] if d['modeDifficulty']!='NORMAL'],
    'zones':details['zones'],
    'squads':{key:{**value,**details['items'][key],'buffs':details['relics'][key]['buffs']} for key,value in details['bandRef'].items()},
    'difficulty_upgrade_relic_groups':details['difficultyUpgradeRelicGroups'],
    'difficulty_upgrade_relic_labels':{key:value.split('：',1)[0] for key,value in details['detailConst']['difficultyUpgradeRelicDescTable'].items()}}
(ROOT/'rouge/data/run-config.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print({'difficulties':len(data['difficulties']),'squad_variants':len(data['squads'])})
