"""Build the full playable roster for recognition, independently of damage rules."""
import json
import hashlib
from pathlib import Path

root=Path(__file__).resolve().parents[1]
cache=root/'.cache/game-data'
def read(name):return json.loads((cache/f'{name}.json').read_text(encoding='utf-8'))
chars,skills,meta,battle=map(read,('character_table','skill_table','uniequip_table','battle_equip_table'))
patch_file=cache/'char_patch_table.json'
chars.update(read('char_patch_table')['patchChars'])
aliases={'char_1052_kalts2':'kaltsit','char_1045_svash2':'silverash','char_4230_mcnist':'mechanist'}
attributes={'maxHp':'hp','atk':'attack','def':'defense','magicResistance':'resistance',
            'respawnTime':'redeploy_seconds','attackSpeed':'attack_speed','blockCnt':'block_count',
            'baseAttackTime':'interval','spRecoveryPerSec':'sp_recovery','cost':'deployment_cost'}
profiles={}
for char_id,char in chars.items():
    if not char_id.startswith('char_') or char.get('isNotObtainable') or not char.get('phases'):continue
    modules=[];initial_modules=[]
    for module_id in meta['charEquip'].get(char_id,[]):
        equip=meta['equipDict'][module_id]
        if equip['type']=='INITIAL':initial_modules.append(equip['uniEquipName']);continue
        modules.append({'id':module_id,'name':equip['uniEquipName'],
            'type':equip['typeName1']+'-'+equip['typeName2'],
            'unlock_elite':int(equip['unlockEvolvePhase'][-1]),'unlock_level':equip['unlockLevel'],
            'levels':[{'level':p['equipLevel'],'attributes':{b['key']:b['value'] for b in p['attributeBlackboard']}}
                      for p in battle.get(module_id,{}).get('phases',[])]})
    profiles[aliases.get(char_id,char_id)]={
        'id':char_id,'name':char['name'],'aliases':[char['name'],char['appellation']],
        'profession':char['profession'].lower(),'position':char['position'].lower(),
        'subprofession':meta['subProfDict'].get(char['subProfessionId'],{}).get('subProfessionName'),
        'rarity':int(char['rarity'][-1]),'modules':modules,'initial_modules':initial_modules,
        'phases':[{'max_level':p['maxLevel'],'frames':[
            {'level':f['level'],**{target:f['data'][source] for source,target in attributes.items()}}
            for f in p['attributesKeyFrames']]} for p in char['phases']],
        'trust_stats':{target:char['favorKeyFrames'][-1]['data'][source] for source,target in attributes.items()},
        'potential_bonuses':[(p.get('buff') or {}).get('attributes',{}).get('attributeModifiers',[]) for p in char['potentialRanks']],
        'skills':[{'id':s['skillId'],'unlock_elite':int(s['unlockCond']['phase'][-1]),
                   'levels':[{'name':l['name'],'initial_sp':l['spData']['initSp'],'sp_cost':l['spData']['spCost']}
                             for l in skills[s['skillId']]['levels']]}
                  for s in char.get('skills',[]) if s.get('skillId')],
    }
target=root/'rouge/data/operator-profiles.json'
source=read('receipt')
source['files']['char_patch_table']={'url':f'https://raw.githubusercontent.com/{source["repository"]}/{source["commit"]}/zh_CN/gamedata/excel/char_patch_table.json',
    'sha256':hashlib.sha256(patch_file.read_bytes()).hexdigest(),'bytes':patch_file.stat().st_size}
target.write_text(json.dumps({'source':source,'operators':profiles},ensure_ascii=False,separators=(',',':')),encoding='utf-8')
print(f'{len(profiles)} playable operator profiles; damage rules remain separate')
