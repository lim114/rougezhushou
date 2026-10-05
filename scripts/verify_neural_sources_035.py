"""Verify researched source prerequisites without inventing secondary clocks."""
import hashlib,json,math,sys,time,unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from verify_offline_scope_030 import NAMES,output
from rouge.damage import calculate_damage
from rouge.relics import mechanics
from rouge.offline_scope import scope_counts

FILES=('AGENTS.md','rouge/operator_engine.py','rouge/elemental_relics.py','rouge/reporting.py',
    'rouge/app.py','pyproject.toml','tests/test_neural_sources_035.py','scripts/verify_neural_sources_035.py')


def digest(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8-sig'))


def main():
    start=time.perf_counter();folder=ROOT/'.cache/neural-035';folder.mkdir(parents=True,exist_ok=True)
    hashes={name:digest(name) for name in FILES}
    modules=NAMES+['tests.test_offline_relics_031','tests.test_spawn_hp_033',
        'tests.test_relic_grade_sync_032','tests.test_run_reuse_guards_032','tests.test_sampling_flow',
        'tests.test_neural_relic_034','tests.test_neural_sources_035']
    with (folder/'tests.log').open('w',encoding='utf-8') as log:
        tested=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(modules))
    assert tested.wasSuccessful(),str(folder/'tests.log')
    rows=read('.cache/neural-035/before-public-results.json');assert len(rows)==348
    unchanged=changed=0
    for row in rows:
        s=row['scenario'];old=row['result'];r=calculate_damage(s);current=output(r)
        if s['operator']!='char_1042_phatm2' or s['skill']!=3:
            assert current==old,s;unchanged+=1;continue
        changed+=1
        for key in ('base_stats','deployment_cost','relic_token_stats','relic_protection'):
            assert current[key]==old[key],(s,key)
        for key in ('initial_seconds','recharge_seconds','cycle_seconds','duration_seconds',
                    'total_healing','phase_healing','cycle_healing','cycle_hps','window_healing',
                    'window_hps','skill_attack','skill_attack_speed'):
            assert current['skill'][key]==old['skill'][key],(s,key)
        arts_before=[c for c in old['components'] if c['damage_type']=='magic']
        arts_now=[c for c in current['components'] if c['damage_type']=='magic']
        assert arts_now==arts_before,s
        assert math.isclose(r['known_damage_subtotals']['window_damage'],sum(c['total'] for c in arts_before)),s
        assert current['total_damage'] is None and current['skill']['cycle_dps'] is None
        assert not any(c['name']=='神经损伤爆发' for c in current['components'])
    assert unchanged==344 and changed==4
    data=mechanics();previous=read('FINAL_0.34_VERIFICATION.json')
    assert digest('rouge/data/relic-mechanics.json')==previous['source_sha256']['rouge/data/relic-mechanics.json']
    source=read('.cache/game-data/receipt.json')
    for name in ('skill_table','character_table'):
        assert digest('.cache/game-data/'+name+'.json')==source['files'][name]['sha256'],name
    raw=read('.cache/game-data/skill_table.json')
    level=raw['skchr_phatm2_3']['levels'][9]
    board={b['key']:b['value'] for b in level['blackboard']}
    assert board['ep_damage_ratio']==.1 and board['interval']==1
    assert board['talent@ep_break_recover_speed']==.5
    assert '造成过' in level['description'] and '直至爆发' in level['description']
    evidence={'version':'0.35.0','verified_at':time.time(),'checked_date':'2026-10-03',
        'user_rule':'未知项不耗费精力猜测机制，直接去查阅资料，此规则应在之后的每一次操作中都应用',
        'standing_instruction_file':'AGENTS.md','source_commit':source['commit'],
        'primary_sources':{n:source['files'][n] for n in ('skill_table','character_table')},
        'skill_id':'skchr_phatm2_3','raw_skill_level_10':level,
        'community_url':'https://prts.wiki/w/酒神#技能',
        'established':['A prior neural-damage source from this operator during S3 is required; passage of time alone does not activate it.',
            'The ongoing source is 10% ATK every second until burst; source parameters alone do not establish phase/lifecycle.',
            'No actual S1 attack implies no attack-attached neural buildup.',
            'No source evidence says mere range exit removes the S3 secondary status.'],
        'unknowns':['Secondary first tick, refresh, post-burst reapplication and post-skill lifetime.',
            'River periodic first/end ticks and interaction with cooldown acceleration.',
            'Exact client binding for S1 multi-hit times and other preexisting timing approximations.'],
        'searches':['酒神 空剧场 每秒 神经损伤 攻击间隔 时机','酒神 空剧场 每秒 结算',
            '酒神 空剧场 离开','phatm2 ep_damage_ratio','酒神 空剧场 持续神经损伤 site:ngabbs.com',
            '酒神 持续损伤 首跳 site:prts.wiki','河谷祭祈 神经 首跳 site:bilibili.com',
            '河谷祭祈.zip','疗养礼品卡 叠加 攻速 site:prts.wiki'],
        'unverified_leads':[
            {'collection_page':'https://www.bilibili.com/video/BV1uyKp6PE2N/',
             'listed_episode':'〖树海机制〗河谷祭祈.zip具体数值',
             'status':'Collection title found; actual episode content not recovered. Public view API returned HTTP 412; no timing fact inferred.'},
            {'page':'https://www.bilibili.com/video/BV11xMC6XEhR/',
             'linked_sheet':'https://docs.qq.com/sheet/DUFhxeHFCaXJwS0Vl?tab=caf4qn',
             'status':'Boss drop-pool research lead only; sheet contents and weights not verified in this batch.'}],
        'policy':'Reuse established evidence; targeted source lookup for new unknowns; do not guess numerical defaults.'}
    research=ROOT/'.cache/research/neural-035';research.mkdir(parents=True,exist_ok=True)
    (research/'evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf-8')
    assert hashes=={n:digest(n) for n in FILES}
    receipt={'version':'0.35.0','passed':True,'verified_at':time.time(),
        'tests_run':tested.testsRun,'current_tests_passed':tested.testsRun-len(tested.skipped),
        'new_tests':20,'historical_combat_tests_skipped':len(tested.skipped),
        'skipped_tests':[{'test':t.id(),'reason':reason} for t,reason in tested.skipped],
        'failures':len(tested.failures),'errors':len(tested.errors),'test_modules':modules,
        'test_log':'.cache/neural-035/tests.log','test_log_sha256':digest('.cache/neural-035/tests.log'),
        'public_before_after_cases':348,'unchanged_cases':unchanged,'changed_s3_cases':changed,
        'baseline_sha256':digest('.cache/neural-035/before-public-results.json'),
        'raw_relic_data_unchanged':True,'data_rule_counts':data['counts'],'offline_scope':scope_counts(data),
        'source_hashes':hashes,'chat_requests':0,'game_actions':0,'new_live_combat_measurements':0,
        'elapsed_seconds':time.perf_counter()-start,
        'limits':['No secondary first-tick/refresh/lifecycle is invented; affected neural totals and burst counts remain unknown.',
            'Only known arts subtotal is retained when secondary buildup changes neural sequencing.',
            'Preexisting S1 multi-hit timing/client binding and other skill gaps remain disclosed.',
            'No new relic completeness, recognition speed, full-inventory accuracy or live-combat measurements.']}
    (ROOT/'NEURAL_0.35_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ('passed','current_tests_passed','new_tests','public_before_after_cases',
        'unchanged_cases','changed_s3_cases','historical_combat_tests_skipped','elapsed_seconds')}),flush=True)


if __name__=='__main__':main()
