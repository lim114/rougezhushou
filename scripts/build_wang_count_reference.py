"""Source-bound ordinary Wang token counts, independent of automatic/skill spawns."""
import argparse,hashlib,json
from pathlib import Path
COMMIT='a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'
OP='char_2027_wang';TOKEN='token_10064_wang_stone1';MODULE='uniequip_002_wang'

def build(root,evidence):
    root=Path(root);evidence=Path(evidence)
    old=json.loads((root/'rouge/data/token-module-cost-reference.json').read_text(encoding='utf8'))
    tables={}
    for key,ref in old['sources'].items():
        raw=(root/'.cache/game-data'/(key+'.json')).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=ref['sha256']:raise ValueError('Pinned table changed: '+key)
        tables[key]=json.loads(raw)
    chars=tables['character_table'];equip=tables['uniequip_table']['equipDict'][MODULE]
    if equip['charId']!=OP or TOKEN not in chars[OP]['displayTokenDict']:raise ValueError('Wrong bound owner/token/module')
    native=json.loads((evidence/'selected-current-metadata.json').read_text(encoding='utf8'))
    enums={t['name']:{f['name']:f.get('default') for f in t['fields']} for t in native['selected']}
    if enums['Torappu.AttributeType']['MAX_DEPLOY_COUNT']['value']!=16 or enums['Torappu.AttributeType']['MAX_DECK_STACK_CNT']['value']!=22:
        raise ValueError('Count attribute enum changed')
    if enums['Torappu.AttributeModifierData+AttributeModifier+FormulaItemType']['ADDITION']['value']!=0:
        raise ValueError('Addition enum changed')
    prefab=json.loads((evidence/'wang-token-prefab.json').read_text(encoding='utf8'))
    mono=json.loads((evidence/'monoscripts-current.json').read_text(encoding='utf8'))
    types={}
    for source in mono['sources']:
        for obj in source['monoscripts']:
            d=obj['data'];h=bytes(d['m_PropertiesHash'][f'bytes[{i}]'] for i in range(16)).hex()
            types.setdefault(h,set()).add(d['m_Namespace']+'.'+d['m_ClassName'])
    indexed={t['index']:t['old_type_hash'] for t in prefab['types']}
    objects={o['path_id']:o for o in prefab['objects']}
    passive=objects[8401454738812396056];talent=objects[-6271364357277982184]
    if types[indexed[passive['type_index']]]!={'Torappu.Battle.Abilities.PassiveBuffAbility'} or types[indexed[talent['type_index']]]!={'Torappu.Battle.Talent'}:
        raise ValueError('Current MonoScript class binding changed')
    if passive['data']['m_GameObject']!=talent['data']['m_GameObject']:raise ValueError('Wrong talent holder')
    if objects[talent['data']['m_GameObject']['m_PathID']]['data']['m_Name']!='1':raise ValueError('Wrong hidden talent key')
    if talent['data']['_attachInDummy']!=1 or passive['data']['_attachPassiveBuffsOnDummy']!=1:
        raise ValueError('Count talent is not attached to dummy')
    modifiers=passive['data']['_buffs'][1]['attributes']['attributeModifiers']
    if modifiers!=[{'attributeType':a,'formulaItem':0,'value':0.,'loadFromBlackboard':1,'fetchBaseValueFromSourceEntity':0} for a in (16,22)]:
        raise ValueError('Count modifier fields changed')
    methods=[]
    for name in ('wang-counts-current.json','wang-convert-current.json'):
        cfg=json.loads((evidence/name).read_text(encoding='utf8'))
        if cfg['dll_sha256']!=native['dll_sha256'] or cfg['metadata_sha256']!=native['metadata_sha256']:
            raise ValueError('Current static sources disagree')
        for method in cfg['methods']:
            if not method['cfg_bounded_traversal_finished'] or method['limits']:raise ValueError('Incomplete count CFG')
            with Path(cfg['source_game_dll']).open('rb') as native_file:
                if hashlib.file_digest(native_file,'sha256').hexdigest()!=native['dll_sha256']:
                    raise ValueError('Current native file changed')
                for row in method['instructions']:
                    expected=bytes.fromhex(row['bytes']);native_file.seek(int(row['physical_offset'],16))
                    if native_file.read(len(expected))!=expected:raise ValueError('Current instruction bytes changed')
            methods.append({'name':method['method']['Name'],'address':hex(method['method']['Address']),
                'instructions':method['instruction_count'],'sha256':method['reachable_bytes_sha256']})
    phases=[]
    for i,phase in enumerate(chars[TOKEN]['phases']):
        first,last=phase['attributesKeyFrames'][0]['data'],phase['attributesKeyFrames'][-1]['data']
        if any(first[key]!=last[key] for key in ('maxDeployCount','maxDeckStackCnt')):raise ValueError('Nonconstant count phase')
        phases.append({'elite':i,'manual_concurrent_base':first['maxDeployCount'],
            'held_base':first['maxDeckStackCnt'],
            'source_selector':f'character_table.{TOKEN}.phases[{i}].attributesKeyFrames[0].data'})
    candidates=[]
    for i,c in enumerate(chars[TOKEN]['talents'][0]['candidates']):
        bb={b['key']:b['value'] for b in c['blackboard']}
        candidates.append({'elite':int(c['unlockCondition']['phase'][-1]),'level':c['unlockCondition']['level'],
            'required_potential_rank':c['requiredPotentialRank'],
            'manual_concurrent_add':bb['max_deploy_count'],'held_add':bb['max_deck_stack_cnt'],
            'source_selector':f'character_table.{TOKEN}.talents[0].candidates[{i}]'})
    module_stages=[]
    for i,p in enumerate(tables['battle_equip_table'][MODULE]['phases']):
        bb=p['tokenAttributeBlackboard'][TOKEN]
        found=next((j,b) for j,b in enumerate(bb) if b['key']=='max_deploy_count')
        module_stages.append({'module_level':p['equipLevel'],'manual_concurrent_add':found[1]['value'],
            'held_add':0,'source_selector':f'battle_equip_table.{MODULE}.phases[{i}].tokenAttributeBlackboard.{TOKEN}[{found[0]}]'})
    return {'schema_version':1,'operator_id':OP,'token_id':TOKEN,'module_id':MODULE,
        'scope':'ordinary_cultivation_token_card_counts','source_commit':COMMIT,'sources':old['sources'],
        'phases':phases,'potential_candidates':candidates,
        'module_unlock_elite':int(equip['unlockEvolvePhase'][-1]),'module_unlock_level':equip['unlockLevel'],
        'module_stages':module_stages,
        'compiled_native_reference':{'base_version':prefab['base_version'],'dll_sha256':native['dll_sha256'],
            'metadata_sha256':native['metadata_sha256'],'token_bundle_sha256':prefab['source_sha256'],
            'token_asset':prefab['asset_path'],'modifier_binding':modifiers,
            'method_count':len(methods),'instructions':sum(m['instructions'] for m in methods),
            'methods':methods,'current_hotfix_verified':False,'live_counts_verified':False},
        'limitations':['仅普通培养与合法模组的默认手动计数/库存参考；未套用技能期间数量修改或自动额外棋子。',
            '实际在场、当前库存、可用地块与全局部署位未知；不保证能够部署，当前XLua覆盖仍未核验。']}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',required=True,type=Path)
    p.add_argument('--evidence',required=True,type=Path);p.add_argument('--output',required=True,type=Path)
    a=p.parse_args();d=build(a.root,a.evidence)
    a.output.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({'phases':d['phases'],'methods':d['compiled_native_reference']['method_count'],
        'instructions':d['compiled_native_reference']['instructions']},ensure_ascii=False))
