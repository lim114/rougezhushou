"""Record primary data, readable sources, known facts and exact remaining gaps."""
import hashlib,json,sys,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from rouge.catalog import catalog
from rouge.relics import mechanics
from rouge.damage import calculate_damage

def digest(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()

def main():
    folder=ROOT/'.cache/research/summon-038'
    p=catalog()['operators']['char_110_deepcl'];module=p['modules'][0]
    assert module['id']=='uniequip_002_deepcl'
    assert (module['unlock_elite'],module['unlock_level'])==(2,40)
    for index,stage in enumerate(module['levels']):
        assert stage['attributes']==({'max_hp':80.0,'atk':20.0},
            {'max_hp':100.0,'atk':30.0},{'max_hp':115.0,'atk':35.0})[index]
        trait=stage['parts'][0]['overrideTraitDataBundle']['candidates'][0]
        assert trait['blackboard']==[{'key':'cnt','value':3.0,'valueStr':None}]
        parts=[part for part in stage['parts'] if part.get('isToken')]
        if index:
            b=parts[0]['addOrOverrideTalentDataBundle']['candidates'][0]['blackboard']
            assert b==[{'key':'max_hp','value':(.1,.15)[index-1],'valueStr':None}]
        else:assert not parts
    examples=[]
    for stage,ids in ((1,[]),(2,[]),(3,[]),(3,['rogue_6_relic_legacy_134']),
                      (3,['rogue_6_relic_legacy_134','rogue_6_relic_legacy_91'])):
        s={'operator':'char_110_deepcl','skill':1,'elite':2,'level':70,
           'module_id':module['id'],'module_level':stage,'relic_ids':ids}
        r=calculate_damage(s)
        examples.append({'scenario':s,'token':r['relic_token_stats'][0],
                         'skill':r['estimate']['skill']})
    evidence={'version':'0.38.0','verified_at':time.time(),
        'standing_instruction_file':'AGENTS.md','source_commit':mechanics()['commit'],
        'source_pages':['https://prts.wiki/w/深海色','https://prts.wiki/w/触手',
                        'https://prts.wiki/w/游戏数据基础#特殊：藏品符文'],
        'readable_formula_redirect':'https://prts.wiki/w/技能专精',
        'source_revision_pinned':False,'source_snapshot':'.cache/research/summon-038/web-source.json',
        'source_snapshot_sha256':digest('.cache/research/summon-038/web-source.json'),
        'raw_sources_sha256':{n:digest(n) for n in ('.cache/game-data/character_table.json',
            '.cache/game-data/battle_equip_table.json','.cache/game-data/uniequip_table.json',
            '.cache/game-data/skill_table.json','rouge/data/catalog.json')},
        'known_facts':{'token_max_level_hp':2016,'token_cost':5,'token_attack':462,
            'token_defense':335,'module_cost_add':-2,'module_stock_add':3,
            'base_e2_stock':4,'equipped_stock':7,'module_hp_pct':[0,.1,.15],
            'unlock_elite':2,'unlock_level':40,'s1_m3_fixed_regeneration_per_second':70},
        'raw_module':module,'preview_examples':examples,
        'not_established_by_blackboards':['The token talent modifier layer against relic/squad HP runes.',
            'A held limit is not evidence of the actual simultaneous on-field limit.'],
        'remaining_specific_unknowns':['SUM-Y HP composition with other HP sources: composite and dependent percentage regeneration remain unknown.',
            'Actual simultaneous tentacle count: the offline model still supports0..base unlocked stock, up to4.',
            'No actual Deepcolor module page captured this batch; UI cases use isolated synthetic observations.',
            'Other modules and conditional/token scripts have not been completed.'],
        'recognition_change':'none','numerical_relic_rules_change':'none',
        'baseline_preparation_issue':'A synthetic squad id was rejected. Replaced it with the pinned rogue_6_band_6 id; before-change source hashes were checked before resuming the public-only capture.',
        'inherited_evidence':'.cache/research/impact-037/evidence.json',
        'inherited_evidence_sha256':digest('.cache/research/impact-037/evidence.json'),
        'new_backlog':['Battle stage map preview','Spawn times','Spawn positions mapped to battle map',
            'Enemy panel values at selected difficulty and stage version','Enemy mechanics preview'],
        'battle_map_download_authorized':True,'battle_map_assets_downloaded_this_batch':0,
        'chat_requests':0,'game_actions':0,'new_live_combat_measurements':0}
    (folder/'evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'version':evidence['version'],'known_module_stages':3,'examples':len(examples),
        'hp_composition_verified':False,'backlog_items':len(evidence['new_backlog'])}),flush=True)

if __name__=='__main__':main()
