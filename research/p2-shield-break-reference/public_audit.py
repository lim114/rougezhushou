from pathlib import Path
import argparse,copy,hashlib,json,subprocess,sys

ROOT=Path(__file__).resolve().parents[2]
BASELINE=ROOT.parent/'shield-baseline'
OUT=Path(__file__).parent


def scenarios():
    cases=[]
    for mode in ('frames','continuous'):
        for rank in (1,7,10):
            for count in (0,1,2,8,9):
                for duration in (None,20):
                    for window in (None,0,1,10):
                        for timing in ({},{'target_disappears_seconds':0},{'target_windows':[]}):
                            s={'operator':'mechanist','skill':2,'base_attack':1000,'skill_rank':rank,
                               'timing_mode':mode,'shield_break_count':count,'timing':timing}
                            if duration is not None:s['skill_duration_seconds']=duration
                            if window is not None:s['window_seconds']=window
                            cases.append(s)
    for mode in ('frames','continuous'):
        for count in (1,2):
            for extra in ({'window_seconds':'0'},
                          {'window_seconds':10,'timing':{'target_disappears_seconds':'0'}},
                          {'window_seconds':10,'skill_duration_seconds':20,'timing':{'target_disappears_seconds':'0'}}):
                cases.append({'operator':'mechanist','skill':2,'base_attack':1000,'timing_mode':mode,
                              'shield_break_count':count,'timing':{},**extra})
        for count in (0,2):
            for rid in ('rogue_6_relic_fight_1','rogue_6_relic_fight_2'):
                cases.append({'operator':'mechanist','skill':2,'base_attack':1000,'timing_mode':mode,
                              'shield_break_count':count,'skill_duration_seconds':20,'timing':{},
                              'relic_ids':[rid],'relic_context':{'enemy_first_damage_unused':1}})
    for mode in ('frames','continuous'):
        for count in (0,1,2):
            for raw in (float(count),f'{count}.0',f'{count}e0'):
                for extra in ({},{'window_seconds':0},{'window_seconds':10,'skill_duration_seconds':20}):
                    cases.append({'operator':'mechanist','skill':2,'base_attack':1000,'timing_mode':mode,
                                  'shield_break_count':raw,'timing':{},**extra})
    return cases


CAPTURE=r'''
from pathlib import Path
import copy,hashlib,json,sys
sys.path.insert(0,sys.argv[1])
from rouge.damage import calculate_damage
from rouge.catalog import catalog
from rouge.estimate import format_estimate
cases=json.loads(Path(sys.argv[2]).read_text());rows=[]
catsha=hashlib.sha256(json.dumps(catalog(),sort_keys=True).encode()).hexdigest()
for s in cases:
 original=copy.deepcopy(s);r=calculate_damage(s);assert original==s
 skill=r['estimate']['skill'];ref=r.get('shield_break_reference')
 rows.append({'scenario':s,'actual_window_damage':r['total_damage'],'complete':r['complete'],
 'estimate_complete':r['estimate']['complete'],'per_hit':r['per_hit'],'hit_count':r['hits'],
 'skill':{k:skill.get(k) for k in ('duration_seconds','initial_seconds','recharge_seconds','cycle_seconds','total_damage','phase_damage','cycle_damage','cycle_dps','window_damage','window_dps')},
 'known_damage_subtotals':r.get('known_damage_subtotals'),'shield_break_reference':ref,
 'timing_streams':r['timing']['streams'],'recharge_streams':r['timing'].get('recharge_streams',[]),
 'scope':r.get('scope'),'estimate_scenario_scope':r['estimate'].get('scenario_scope'),
 'report_claims_actual_shield_breaks':'仅实际屏障破碎' in format_estimate(r),
 'components':r.get('components'),'report_incomplete':'计算状态：不完整' in format_estimate(r)})
assert catsha==hashlib.sha256(json.dumps(catalog(),sort_keys=True).encode()).hexdigest()
Path(sys.argv[3]).write_text(json.dumps({'cached_catalog_sha256':catsha,'cached_catalog_unchanged':True,'inputs_unchanged':True,'case_count':len(rows),'rows':rows},ensure_ascii=False,indent=2)+'\n')
'''


def main():
    cases=scenarios();(OUT/'scenarios.json').write_text(json.dumps(cases,ensure_ascii=False,indent=2)+'\n')
    for label,path in (('baseline',BASELINE),('draft',ROOT)):
        subprocess.run([sys.executable,'-c',CAPTURE,str(path),str(OUT/'scenarios.json'),str(OUT/f'public-{label}.json')],check=True)
    before=json.loads((OUT/'public-baseline.json').read_text());after=json.loads((OUT/'public-draft.json').read_text())
    assert before['cached_catalog_sha256']==after['cached_catalog_sha256']
    groups={'zero_declaration_values_preserved':0,'explicit_empty_or_enemy_zero_actual_zero':0,'positive_unplaced_actual_unknown':0}
    ordinary_equal=0
    for b,a in zip(before['rows'],after['rows'],strict=True):
        s=b['scenario'];assert s==a['scenario']
        assert a['per_hit']==b['per_hit']
        assert a['hit_count']==b['hit_count']
        assert a['timing_streams']==b['timing_streams']
        assert a['recharge_streams']==b['recharge_streams']
        assert not a['complete'] and not a['estimate_complete']
        assert not a['report_claims_actual_shield_breaks']
        assert a['scope']==a['estimate_scenario_scope']
        assert '声明总破屏次数的法术爆炸条件参考，事件时刻未知' in a['scope']
        for k in ('duration_seconds','initial_seconds','recharge_seconds','cycle_seconds'):
            assert a['skill'][k]==b['skill'][k]
        count=int(float(s['shield_break_count']));life=s['timing'].get('target_disappears_seconds')
        alive=life is None or float(life)!=0
        empty='window_seconds' in s and float(s['window_seconds'])==0
        assert a['shield_break_reference']['declared_count_damage_reference']==b['per_hit']*count
        if count==0:
            groups['zero_declaration_values_preserved']+=1
            assert a['components']==b['components']
            assert a['actual_window_damage']==b['actual_window_damage']
            for k in ('total_damage','phase_damage','cycle_damage','cycle_dps','window_damage'):
                assert a['skill'][k]==b['skill'][k]
        elif not alive or empty:
            groups['explicit_empty_or_enemy_zero_actual_zero']+=1
            assert a['actual_window_damage']==0
            assert a['skill']['window_damage']==0
        else:
            groups['positive_unplaced_actual_unknown']+=1
            assert a['actual_window_damage'] is None
            assert a['skill']['window_damage'] is None
        if count and 'skill_duration_seconds' in s:
            excluded=b['per_hit']*b['hit_count']
            for k in ('total_damage','phase_damage','cycle_damage'):
                expected=max(0,b['skill'][k]-excluded) if alive else 0
                assert a['known_damage_subtotals'][k]==expected
            if not alive:
                for k in ('total_damage','phase_damage','cycle_damage','cycle_dps'):
                    assert a['skill'][k]==0
            ordinary_equal+=1
    result={'public_entry':'rouge.damage.calculate_damage','case_count':len(cases),'categories':groups,
        'manual_duration_ordinary_subtotals_retained':ordinary_equal,'per_hit_reference_preserved':True,
        'sp_and_manual_duration_parameters_preserved':True,'existing_attack_streams_preserved':True,
        'numeric_string_zero_cases':12,'public_reference_only_first_damage_cases':8,
        'legacy_decimal_scientific_count_cases':54,'zero_declaration_components_preserved':True,'inherited_report_scope_no_actual_shield_claim':True,'input_and_cached_catalog_preserved':True,'native_event_times_verified':False,'tracked_edits':False}
    (OUT/'public-comparison.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__':main()
