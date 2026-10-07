"""Build the reviewed Wang/TRP-X direct token cost parameter from pinned data."""
import argparse
import hashlib
import json
from pathlib import Path

COMMIT='a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'
HASHES={
    'character_table':'68e3a3b5ee0d407ce234afaa5867c6fda6379a6843c7d5317a7bbda4779f8697',
    'battle_equip_table':'006687f201a823abf31c6a1c57b2269099bd3ea375c2ec3ae5595cc98a1ec460',
    'uniequip_table':'b508483cc87c03d8313f4dd8dfc1b9195bc50385a8dfec51d17e657cb26ffad9',
}
OP='char_2027_wang';TOKEN='token_10064_wang_stone1';MODULE='uniequip_002_wang'


def build(character_path,battle_path,uniequip_path):
    sources={};tables={}
    for name,path in zip(HASHES,(character_path,battle_path,uniequip_path)):
        raw=Path(path).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=HASHES[name]:
            raise ValueError(name+' does not match the reviewed pinned source')
        tables[name]=json.loads(raw)
        sources[name]={'sha256':HASHES[name],
            'url':f'https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/{COMMIT}/zh_CN/gamedata/excel/{name}.json'}
    char=tables['character_table'][OP]
    if TOKEN not in char['displayTokenDict']:raise ValueError('reviewed token pair missing')
    module=tables['uniequip_table']['equipDict'][MODULE]
    if module['charId']!=OP:raise ValueError('reviewed module owner missing')
    stages=[]
    for i,phase in enumerate(tables['battle_equip_table'][MODULE]['phases']):
        values=phase['tokenAttributeBlackboard'][TOKEN]
        index=next(i for i,b in enumerate(values) if b['key']=='cost')
        stages.append({'module_level':phase['equipLevel'],'cost_add':values[index]['value'],
            'source_selector':f'battle_equip_table.{MODULE}.phases[{i}].tokenAttributeBlackboard.{TOKEN}[{index}]'})
    return {'schema_version':1,'scope':'token_module_cost_reference','source_commit':COMMIT,'sources':sources,
        'rules':[{'operator_id':OP,'token_id':TOKEN,'module_id':MODULE,
            'module_unlock_elite':int(module['unlockEvolvePhase'][-1]),'module_unlock_level':module['unlockLevel'],
            'module_source_selector':f'uniequip_table.equipDict.{MODULE}','stages':stages}]}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--character',required=True,type=Path)
    parser.add_argument('--battle',required=True,type=Path)
    parser.add_argument('--uniequip',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    data=build(args.character,args.battle,args.uniequip)
    args.output.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'source_commit':COMMIT,'module':MODULE,'cost_additions':[s['cost_add'] for s in data['rules'][0]['stages']]}))
