"""Offline public-calculator conformance sweep; not a combat-accuracy claim."""
import hashlib
import json
import math
import sys
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate


def verify(scenario):
    result=calculate_damage(scenario)
    for key in ('total_damage','total_healing'):
        value=result.get(key,0)
        assert math.isfinite(value) and value>=0,(scenario,key,value)
    estimate=result['estimate']
    for key,value in estimate['base_stats'].items():
        assert math.isfinite(value) and value>=0,(scenario,key,value)
    for key in ('initial_seconds','recharge_seconds','cycle_seconds','duration_seconds','cycle_dps','cycle_hps','total_damage','total_healing'):
        value=estimate['skill'][key]
        assert value is None or (math.isfinite(value) and value>=0),(scenario,key,value)
    text=format_estimate(result)
    assert all(label in text for label in ('预计基础数值：','攻速：','技能情况：','预计回转：','预计初动：','【技能时序】','【状态与依据】'))
    assert result['report']['schema_version']==2
    for block in result['report']['sections']:
        assert '【'+block['title']+'】' in text
        for row in block['metrics']:
            value=row['value']
            assert value is None or (math.isfinite(value) and value>=0),(scenario,block['id'],row)
    return result


def main():
    data=catalog()
    selection=json.loads((ROOT/'rouge/data/common-operators.json').read_text(encoding='utf-8'))
    assert len(selection['operators'])==selection['identity_count']==30
    aliases={p['id']:key for key,p in data['operators'].items()}
    ids=[cid for entry in selection['operators'] for cid in entry.get('forms',[entry['id']])]
    assert len(ids)==len(set(ids))==len(data['operators'])==32
    counts={'skill_rank_cases':0,'cultivation_cases':0,'module_cases':0,'relic_cases':0}
    profiles=[]
    for cid in ids:
        key=aliases[cid];p=data['operators'][key]
        for number,skill in enumerate(p['skills'],1):
            for rank in range(1,11):
                verify({'operator':key,'skill':number,'skill_rank':rank})
                counts['skill_rank_cases']+=1
            # Legal cultivation extremes must use only their unlocked skills/ranks.
            for elite,phase in enumerate(p['phases']):
                if skill['unlock_elite']>elite:continue
                for level,trust,potential in ((1,0,1),(phase['max_level'],100,6)):
                    verify({'operator':key,'skill':number,'elite':elite,'level':level,
                            'trust':trust,'potential':potential,'skill_rank':7 if elite<2 else 10})
                    counts['cultivation_cases']+=1
            for module in p['modules']:
                for module_level in range(1,len(module['levels'])+1):
                    result=verify({'operator':key,'skill':number,'module_id':module['id'],'module_level':module_level})
                    assert not result['estimate']['complete'],'Unmodeled module traits must stay disclosed'
                    counts['module_cases']+=1
            # Real supported all-units and operator-only effects together, then an unknown ID.
            result=verify({'operator':key,'skill':number,'enemy_defense':300,'enemy_resistance':30,
                'relic_ids':['rogue_6_relic_fight_25','rogue_6_relic_legacy_142','rogue_6_relic_legacy_23_c']})
            assert len(result['applied_effects'])>=5
            unknown=verify({'operator':key,'skill':number,'relic_ids':['unknown-verification-relic']})
            assert not unknown['complete'] and not unknown['estimate']['complete']
            counts['relic_cases']+=2
        profiles.append({'id':cid,'key':key,'name':p['name'],'profession':p['profession'],
            'skills':[{'number':i,'name':s['levels'][-1]['name'],'ranks_verified':list(range(1,11)),
                'mode':verify({'operator':key,'skill':i})['estimate']['skill'].get('mode','legacy')}
                for i,s in enumerate(p['skills'],1)]})
    receipt={'verified_at':time.time(),'identity_count':30,'form_profiles':len(profiles),
        'skill_count':sum(len(p['skills']) for p in profiles),'cases':counts,'public_entry':'calculate_damage',
        'sources':selection['sources'],'ranking_claim':False,
        'catalog_sha256':hashlib.sha256((ROOT/'rouge/data/catalog.json').read_bytes()).hexdigest(),
        'calculation_source_sha256':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
            for name in ('rouge/damage.py','rouge/operator_engine.py','rouge/catalog.py','rouge/estimate.py','rouge/reporting.py','rouge/timing.py','rouge/relics.py','rouge/data/relic-mechanics.json','rouge/data/timing-profiles.json')},
        'limits':['遍历仅证明可执行、有限非负和报告/状态契约，不证明每项战斗机制数值精确。',
            '连续供靶机制算例见tests/test_damage.py；逐帧时序算例见tests/test_timing.py；不是30名干员的实战对照。',
            '常规时序已接入，动画模板/皮肤/多段/部分周期分项仍未完整校准；模组隐藏条件、难度/分队/特训及条件藏品仍有缺失。'],
        'chat_requests':0,'game_capture_requests':0,'profiles':profiles}
    (ROOT/'COMMON_OPERATOR_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ('identity_count','form_profiles','skill_count','cases')},ensure_ascii=False))


if __name__=='__main__':main()
