"""Cache-only exact original choice and region-effect relationship inventory."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
PRIMARY='.cache/p3-287-event-research/fixed-game-topic.json'
CATALOG='rouge/data/node-catalog.json'
raw=(ROOT/PRIMARY).read_bytes()
assert hashlib.sha256(raw).hexdigest()=='f5867e55d09472253083486174aa47bd94dd48b07684b74b60a5b29ca00eda86'
data=json.loads(raw);detail=data['details']['rogue_6']
catalog=json.loads((ROOT/CATALOG).read_bytes())
choices={key:value for key,value in detail['choices'].items() if '希望的沃土' in (value.get('description') or '')}
community=[]
for event in catalog['events']:
    for scene in event['scenes']:
        for choice in scene['choices']:
            if '希望的沃土' in (choice.get('description') or ''):
                community.append({'event_id':event['id'],'event_title':event['title'],'scene':scene,'choice':choice})
hits=[]


def walk(value,path):
    if isinstance(value,dict):
        if value.get('name')=='“希望的沃土”':hits.append({'path':path,'complete_record':value})
        for key,item in value.items():walk(item,path+[str(key)])
    elif isinstance(value,list):
        for index,item in enumerate(value):walk(item,path+[str(index)])


walk(data['customizeData']['rogue_6'],['customizeData','rogue_6'])
result={'kind':'future-region-source-inventory-not-feature','checked_at':datetime.now(timezone.utc).isoformat(),
        'source':{'path':PRIMARY,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),
                  'commit':'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'},
        'current_catalog_sha256':hashlib.sha256((ROOT/CATALOG).read_bytes()).hexdigest(),
        'complete_original_choices':choices,'community_choices':community,'complete_named_region_records':hits,
        'production_private_Qt_tests_Git_game_chat_operations':False}
target=HERE/'future-region-inventory.json';target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'output':str(target.relative_to(ROOT)),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
    'original_ids':list(choices),'community':[{'event':c['event_id'],'scene':c['scene']['key'],'choice':c['choice']['key'],
        'title':c['choice']['title'],'description':c['choice']['description'],'original_ids':c['choice']['game_choice_ids']} for c in community],
    'effects':hits},ensure_ascii=False,indent=2))
