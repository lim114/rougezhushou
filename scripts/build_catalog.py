"""Extract reproducible, small profiles from the pinned public data snapshot."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / '.cache' / 'game-data'
def read(name):
    return json.loads((CACHE / f'{name}.json').read_text(encoding='utf-8'))

chars, skills, topic = read('character_table'), read('skill_table'), read('roguelike_topic_table')
chars.update(read('char_patch_table')['patchChars'])
equip_meta,equip_battle=read('uniequip_table'),read('battle_equip_table')
detail = topic['details']['rogue_6']
operators = {}
attributes={'maxHp':'hp','atk':'attack','def':'defense','magicResistance':'resistance',
            'respawnTime':'redeploy_seconds','attackSpeed':'attack_speed','blockCnt':'block_count',
            'baseAttackTime':'interval','spRecoveryPerSec':'sp_recovery','cost':'deployment_cost'}
selection=json.loads((ROOT/'rouge/data/common-operators.json').read_text(encoding='utf-8'))
aliases={'char_1052_kalts2':'kaltsit','char_1045_svash2':'silverash','char_4230_mcnist':'mechanist'}
selected_ids=[cid for entry in selection['operators'] for cid in entry.get('forms',[entry['id']])]
for char_id in selected_ids:
    key=aliases.get(char_id,char_id)
    char = chars[char_id]
    modules=[]
    for mid in equip_meta['charEquip'].get(char_id,[]):
        meta=equip_meta['equipDict'][mid]
        if meta['type']=='INITIAL':continue
        module=equip_battle.get(mid,{})
        modules.append({'id':mid,'name':meta['uniEquipName'],'type':meta['typeName1']+'-'+meta['typeName2'],
            'unlock_elite':int(meta['unlockEvolvePhase'][-1]),'unlock_level':meta['unlockLevel'],
            'levels':[{'level':p['equipLevel'],'attributes':{b['key']:b['value'] for b in p['attributeBlackboard']},
                       'parts':p['parts']} for p in module.get('phases',[])]})
    operators[key] = {
        'id': char_id, 'name': char['name'], 'profession': char['profession'].lower(),
        'position': char['position'].lower(), 'trust_attack': char['favorKeyFrames'][-1]['data']['atk'],
        'subprofession_id':char['subProfessionId'],
        'trait':char.get('trait'),
        'tokens': {cid:{'name':chars[cid]['name'],'position':chars[cid]['position'].lower(),
            'subprofession_id':chars[cid]['subProfessionId'],'phases':[
            {'max_level':p['maxLevel'],'frames':[{'level':f['level'],**{target:f['data'][source] for source,target in attributes.items()}}
                for f in p['attributesKeyFrames']]} for p in chars[cid]['phases']]}
            for cid in (char.get('displayTokenDict') or {}) if cid in chars},
        'modules':modules,
        'trust_stats':{target:char['favorKeyFrames'][-1]['data'][source] for source,target in attributes.items()},
        'potential_bonuses':[(p.get('buff') or {}).get('attributes',{}).get('attributeModifiers',[]) for p in char['potentialRanks']],
        'talents':[[{'phase':int(t['unlockCondition']['phase'][-1]),'level':t['unlockCondition']['level'],
                    'potential_rank':t['requiredPotentialRank'],'name':t['name'],'description':t['description'],
                    'values':{b['key']:b['value'] for b in t['blackboard']}}
                   for t in talent['candidates'] if t['name']] for talent in char['talents']],
        'phases': [{'max_level': p['maxLevel'], 'frames': [
            {'level': f['level'], **{target:f['data'][source] for source,target in attributes.items()}}
            for f in p['attributesKeyFrames']]} for p in char['phases']],
        'skills': [{ 'id': s['skillId'],'unlock_elite':int(s['unlockCond']['phase'][-1]), 'levels': [
            {'name': l['name'], 'duration': l['duration'], 'description': l['description'],
             'duration_type':l['durationType'],'sp_type':l['spData']['spType'],
             'sp_cost':l['spData']['spCost'],'initial_sp':l['spData']['initSp'],
             'sp_increment':l['spData']['increment'],'max_charges':l['spData']['maxChargeTime'],
             'values': {b['key']: b['value'] for b in l['blackboard']}}
            for l in skills[s['skillId']]['levels']]} for s in char['skills']],
    }

# Only map unconditional effects whose application scope is explicit in the data.
# Other effects remain visible in the catalog and are reported as uncalculated.
safe_relics = {f'rogue_6_relic_legacy_{i}' for i in [2,3,4,5,6,7,8,9,10,12,13,14,15,16,17,18,19,20,64,68,69,71,75,89,90,142]}
safe_relics |= {f'rogue_6_relic_legacy_{i}{suffix}' for i in [23,24,25,26,27,28,29,30,31,45,46] for suffix in ['', '_a', '_b', '_c']}
safe_relics |= {'rogue_6_relic_fight_25', 'rogue_6_relic_fight_29', 'rogue_6_relic_book_7'}
relics = {}
for rid, item in detail['items'].items():
    if item.get('type') != 'RELIC':
        continue
    effects = []
    if rid in safe_relics:
        for buff in detail['relics'].get(rid, {}).get('buffs', []):
            bb = {x['key']: x.get('valueStr') if x.get('valueStr') is not None else x.get('value') for x in buff['blackboard']}
            scope = {'profession': bb.get('selector.profession', '').lower(), 'position': bb.get('selector.buildable', '')}
            if buff['key'] == 'char_attribute_mul':
                for attr,kind in [('atk','attack_pct'),('max_hp','hp_pct'),('def','defense_pct')]:
                    if attr in bb:effects.append({'kind':kind,'value':bb[attr],**scope})
            if buff['key'] == 'char_attribute_add':
                for attr,kind in [('attack_speed','attack_speed'),('magic_resistance','resistance_flat')]:
                    if attr in bb:effects.append({'kind':kind,'value':bb[attr],**scope})
            if buff['key']=='global_buff_stack' and bb.get('key')=='modify_sp_recover[normal]':
                effects.append({'kind':'sp_recovery','value':bb['sp_recovery_per_sec']})
            if buff['key'] == 'global_buff_stack_base_one':
                dtype = {'enemy_damage_scale[phy]': 'physical', 'enemy_damage_scale[mag]': 'magic'}.get(bb.get('key'))
                if dtype:
                    effects.append({'kind': 'damage_taken', 'value': bb['damage_scale'] - 1, 'damage_type': dtype})
    relics[rid] = {'name': item['name'], 'usage': item.get('usage'), 'effects': effects,
                   'supported': bool(effects), 'rarity': item.get('rarity')}

data = {'source': read('receipt'), 'selection':selection, 'operators': operators, 'relics': relics,
        'node_types': detail['nodeTypeData'],
        'difficulties': sorted({v['grade'] for v in detail['difficulties']}),
        'endings': [{'id': k, 'name': v['name']} for k,v in detail['endings'].items()],
        'stages': {k: {field: v.get(field) for field in ['name','levelId','code','description','difficulty','isBoss','isElite']}
                   for k,v in detail['stages'].items()}}
target = ROOT / 'rouge' / 'data' / 'catalog.json'
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'{len(operators)} operators, {len(relics)} relics ({sum(r["supported"] for r in relics.values())} supported), {len(data["stages"])} stages')
