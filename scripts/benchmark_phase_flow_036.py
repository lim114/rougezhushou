"""Paired local benchmarks, using the audited pre-edit local source copy."""
import copy,hashlib,json,statistics,sys,time,tracemalloc,types
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import rouge.damage as current
import rouge.catalog as catalogs
import rouge.relics as relics
import rouge.run_modifiers as run_modifiers


def main():
    baseline=ROOT/'.cache/batch-036-before/rouge/damage.py'
    manifest=json.loads((baseline.parents[1]/'manifest.json').read_text(encoding='utf-8'))
    assert hashlib.sha256(baseline.read_bytes()).hexdigest()==manifest['rouge/damage.py']
    old=types.ModuleType('rouge._phase_baseline_036');old.__package__='rouge'
    exec(compile(baseline.read_text(encoding='utf-8'),str(baseline),'exec'),old.__dict__)
    scenarios=[
        {'operator':'mechanist','skill':1,'relic_ids':['rogue_6_relic_legacy_95']},
        {'operator':'char_133_mm','skill':1,'relic_ids':['rogue_6_relic_legacy_96']},
        {'operator':'char_1044_hsgma2','skill':1,'relic_ids':['rogue_6_relic_legacy_97']},
        {'operator':'mechanist','skill':1,'relic_ids':['rogue_6_relic_legacy_95','rogue_6_start_4',
                                                    'rogue_6_relic_fight_25'],
         'target_enemy':{'stage_id':'ro6_n_1_2','enemy_id':'enemy_1093_ccsbr','level':0},
         'run_config':{'difficulty':{'value':9}},'char_buff_ids':['rogue_6_from_relic_9']},
    ]
    # Preparation counters check the performance contract; public full outputs
    # are checked separately. Neither source opens user state or performs I/O.
    rows=[]
    for scenario in scenarios:
        original=copy.deepcopy(scenario)
        assert old.calculate_damage(scenario)==current.calculate_damage(scenario)
        counts={}
        for label,module in (('before',old),('after',current)):
            with patch.object(catalogs,'operator_attributes',wraps=catalogs.operator_attributes) as attributes,\
                 patch.object(relics,'prepare',wraps=relics.prepare) as rules,\
                 patch.object(run_modifiers,'prepare_run',wraps=run_modifiers.prepare_run) as environment:
                module.calculate_damage(scenario)
                counts[label]={'cultivation':attributes.call_count,'relics':rules.call_count,
                               'run_environment':environment.call_count}
        durations={'before':[],'after':[]}
        for repeat in range(7):
            order=(('before',old),('after',current)) if repeat%2==0 else (('after',current),('before',old))
            for label,module in order:
                started=time.perf_counter();module.calculate_damage(scenario)
                durations[label].append((time.perf_counter()-started)*1000)
        peaks={}
        # Allocation tracing can dominate large timeline calculations. Measure
        # one bounded representative; other cases use untraced paired latency.
        if not rows:
            for label,module in (('before',old),('after',current)):
                tracemalloc.start()
                module.calculate_damage(scenario)
                _,peaks[label]=tracemalloc.get_traced_memory();tracemalloc.stop()
        before=statistics.median(durations['before']);after=statistics.median(durations['after'])
        assert scenario==original
        assert counts['after']=={'cultivation':1,'relics':1,'run_environment':1}
        if peaks:assert peaks['after']<peaks['before'],peaks
        rows.append({'scenario':scenario,'preparation_calls':counts,'paired_repeats':7,
            'durations_ms':durations,'median_ms':{'before':before,'after':after},
            'median_reduction_percent':100*(1-after/before),'traced_peak_bytes':peaks,
            'traced_peak_reduction_percent':100*(1-peaks['after']/peaks['before']) if peaks else None})
        print(json.dumps({'case':len(rows),'median_ms':rows[-1]['median_ms'],
                          'peak_bytes':peaks}),flush=True)
    receipt={'version':'0.36.0','verified_at':time.time(),'passed':True,'cases':rows,
        'baseline_source_sha256':manifest['rouge/damage.py'],
        'current_source_sha256':hashlib.sha256((ROOT/'rouge/damage.py').read_bytes()).hexdigest(),
        'chat_requests':0,'game_actions':0,'private_state_used':False,
        'allocation_samples':1,'allocation_trace_scope':'first representative only',
        'pilot_note':'An earlier four-case pilot completed, but allocation tracing with explicit Mei animation override took several minutes. Bounded rechecks trace only the first representative.',
        'limits':['Warm local paired measurements only; no whole-page recognition timing or live-combat accuracy claim.',
                  'Tracemalloc measures Python allocations; it does not measure whole-process resident memory.',
                  'Every phase and existing unknown still participates; no numerical mechanism was added.']}
    (ROOT/'PERFORMANCE_0.36_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'passed':True,'cases':len(rows)}),flush=True)


if __name__=='__main__':main()
