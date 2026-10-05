import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CACHE=ROOT/'.cache/game-data/levels'
catalog=json.loads((ROOT/'rouge/data/catalog.json').read_text(encoding='utf-8'))
enemy_db={entry['Key']:entry['Value'] for entry in json.loads((CACHE/'enemydata/enemy_database.json').read_text(encoding='utf-8'))['enemies']}

def apply_defined(target,source):
    if not isinstance(source,dict):return
    for key,value in source.items():
        if isinstance(value,dict) and 'm_defined' in value:
            if value['m_defined']:target[key]=value['m_value']
        elif isinstance(value,dict):
            apply_defined(target.setdefault(key,{}),value)

def text(value):
    return re.sub(r'<[^>]*>','',value or '').replace('\\n','\n')

previews={}
for sid,stage in catalog['stages'].items():
    path=CACHE/(stage['levelId'].lower()+'.json')
    if not path.exists():continue
    level=json.loads(path.read_text(encoding='utf-8'))
    enemies=[]
    for ref in level.get('enemyDbRefs',[]):
        # The serialized enum default is NORMAL when level zero marks it
        # undefined. Explicit later/overwritten definitions still take priority.
        initial=next((v for v in enemy_db.get(ref['id'],[]) if v['level']==0),{}).get('enemyData',{}).get('levelType',{})
        resolved={'levelType':'NORMAL'} if not initial.get('m_defined') and initial.get('m_value')=='NORMAL' else {}
        for version in sorted(enemy_db.get(ref['id'],[]),key=lambda x:x['level']):
            if version['level']<=ref['level']:
                apply_defined(resolved,version['enemyData'])
        apply_defined(resolved,ref.get('overwrittenData'))
        attrs=resolved.get('attributes',{})
        enemies.append({'id':ref['id'],'level':ref['level'],'name':resolved.get('name',ref['id']),
                        'level_type':resolved.get('levelType'),
                        'description':text(resolved.get('description')),
                        'reference_stats':{k:attrs.get(k) for k in ['maxHp','atk','def','magicResistance','baseAttackTime','massLevel']}})
    mapdata=level.get('mapData',{})
    tiles=[{k:t.get(k) for k in ['tileKey','heightType','buildableType','passableMask']} for t in mapdata.get('tiles',[])]
    previews[sid]={'possible_enemies':enemies,'runes':level.get('runes') or [],
        'global_buffs':level.get('globalBuffs') or [],
        'terrain':{'map':mapdata.get('map',[]),'tiles':tiles},
        'limitations':['敌人表含随机特殊敌人；列表不是必定出场名单。','数值为关卡敌人引用的参考属性，未应用本局难度、环境或藏品修正。','不据此推算藏品掉落概率。']}
result={'source':json.loads((ROOT/'.cache/game-data/level-receipt.json').read_text(encoding='utf-8')),'stages':previews}
(ROOT/'rouge/data/previews.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(f'{len(previews)} stage previews; {sum(len(p["possible_enemies"]) for p in previews.values())} enemy references')
