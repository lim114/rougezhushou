#!/usr/bin/env python3
"""Read-only public API probe on frozen c3ccf25; writes external audit files only."""
from __future__ import annotations
import copy
import hashlib
import json
import math
import sys
import traceback
from collections import Counter
from contextlib import nullcontext
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
BASELINE = ROOT / 'baseline'
sys.path.insert(0, str(BASELINE))
sys.dont_write_bytecode = True
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.summons import module_rules
import rouge.reporting as reporting

OP = 'char_110_deepcl'
TOKEN = 'token_10001_deepcl_tentac'
MOD = 'uniequip_002_deepcl'
ABSENT = object()


def safe(value):
    """Explicit tagged input labels for nonfinite floats; no JSON NaN token."""
    if isinstance(value, float) and not math.isfinite(value):
        return {'__nonfinite_float__': 'nan' if math.isnan(value) else '+inf' if value > 0 else '-inf'}
    if isinstance(value, dict):
        return {str(k): safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe(v) for v in value]
    return value


def canonical(value):
    return json.dumps(safe(value), sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def file_hashes():
    return {str(p.relative_to(BASELINE)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(BASELINE.rglob('*')) if p.is_file() and p.suffix in ('.py', '.json')}


def differences(a, b, path='$'):
    if isinstance(a, dict) and isinstance(b, dict):
        out=[]
        for key in sorted(set(a) | set(b)):
            if key not in a or key not in b:
                out.append({'path': path+'.'+key, 'left': safe(a.get(key, '<absent>')), 'right': safe(b.get(key, '<absent>'))})
            else:
                out.extend(differences(a[key], b[key], path+'.'+key))
        return out
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return [{'path': path, 'left_length': len(a), 'right_length': len(b)}]
        return [row for i, (x, y) in enumerate(zip(a,b)) for row in differences(x, y, f'{path}[{i}]')]
    if type(a) is not type(b) or a != b:
        return [{'path': path, 'left': safe(a), 'right': safe(b), 'left_type': type(a).__name__, 'right_type': type(b).__name__}]
    return []


freeze = json.loads((ROOT/'baseline-freeze.json').read_text())
source_before = file_hashes()
if source_before != freeze['files']:
    raise AssertionError('Frozen public source hash inventory differs before probe')
catalog_before = digest(catalog())
rules_before = digest(module_rules())
records = []
report_calls = []
original_report = reporting.build_report


def observed_report(scenario, result):
    # Diagnostic observer only: copies the existing state; ALWAYS calls original.
    report_calls.append({'prepared_scenario': copy.deepcopy(scenario),
                         'existing_result_before_report': copy.deepcopy(result)})
    return original_report(scenario, result)


def invoke(scenario, context, count_label, synthetic=False, instrument=True):
    before = canonical(scenario)
    report_calls.clear()
    record = {'id': len(records)+1, 'context': context, 'count_label': count_label,
              'input': safe(copy.deepcopy(scenario)), 'synthetic_guard_fixture': synthetic,
              'diagnostic_report_observer': instrument}
    try:
        result = calculate_damage(scenario)
        record.update(status='returned', result=result, result_sha256=digest(result))
    except Exception as exc:
        record.update(status='raised', exception={'type': type(exc).__name__, 'message': str(exc),
                                                  'traceback': traceback.format_exc()})
    record['caller_unchanged'] = before == canonical(scenario)
    if not record['caller_unchanged']:
        raise AssertionError('Public call mutated caller input')
    if instrument:
        record['observed_report_calls'] = copy.deepcopy(report_calls)
        record['model_reached_report'] = bool(report_calls)
        if report_calls:
            record['pre_report_result_sha256'] = digest(report_calls[-1]['existing_result_before_report'])
    records.append(record)
    return record


def scenario_for(training, skill, mode, rank):
    data = {'operator':OP, 'skill':skill, 'skill_rank':rank, 'timing': {'mode':mode},
            'window_seconds':10, **training}
    return data


trainings = {
    'e0_no_module': {'elite':0,'level':45,'module_id':None,'module_level':0},
    'e1_no_module': {'elite':1,'level':60,'module_id':None,'module_level':0},
    'e1_locked_module': {'elite':1,'level':60,'module_id':MOD,'module_level':3},
    'e2_no_module': {'elite':2,'level':70,'module_id':None,'module_level':0},
    'e2_locked_level39': {'elite':2,'level':39,'module_id':MOD,'module_level':3},
    'e2_qualified_level40': {'elite':2,'level':40,'module_id':MOD,'module_level':3},
}
main_values = [('absent_default',ABSENT), ('int_zero',0), ('int_one',1), ('float_one',1.0),
               ('string_zero','0'), ('string_one','1'), ('string_decimal_one','1.0'), ('bool_true',True)]
contexts={}
reporting.build_report = observed_report
try:
    for training_name, training in trainings.items():
        ranks = (1,7) if training['elite'] < 2 else (1,10)
        for skill in (1,2):
            for mode in ('continuous','frames'):
                for rank in ranks:
                    name = f'main/{training_name}/s{skill}/{mode}/rank{rank}'
                    context_records={}
                    for label, value in main_values:
                        scenario = scenario_for(training,skill,mode,rank)
                        if value is not ABSENT:
                            scenario['summon_count']=value
                        context_records[label] = invoke(scenario,name,label)
                    contexts[name]=context_records
    qualified = {'elite':2,'level':70,'module_id':MOD,'module_level':3}
    extra_values = [('bool_false',False),('float_zero',0.0),('string_decimal_zero','0.0'),
                    ('string_scientific_one','1e0'),('int_two',2),('int_cap',7),('int_cap_plus_one',8)]
    error_values = [('none',None),('empty_string',''),('bad_string','unknown'),('empty_list',[]),
                    ('empty_dict',{}),('negative_int',-1),('negative_string','-1'),
                    ('fractional_float',1.5),('fractional_string','1.5'),
                    ('infinite_float',float('inf')),('negative_infinite_float',float('-inf')),('nan_float',float('nan'))]
    for skill in (1,2):
        for mode in ('continuous','frames'):
            for label,value in extra_values+error_values:
                scenario = scenario_for(qualified,skill,mode,10)
                scenario['summon_count']=value
                invoke(scenario,f'extra/qualified/s{skill}/{mode}/rank10',label)
    inactive_values = [('absent_default',ABSENT),('bool_true',True),('bool_false',False),('string_one','1'),
                       ('string_decimal_one','1.0'),('bad_string','unknown'),('fractional_float',1.5),
                       ('negative_int',-1),('nan_float',float('nan'))]
    inactive_contexts={}
    for op in ('mechanist','char_151_myrtle','char_1037_amiya3'):
        for mode in ('continuous','frames'):
            name=f'inactive/{op}/{mode}/s1'
            cur={}
            for label,value in inactive_values:
                scenario={'operator':op,'skill':1,'elite':2,'skill_rank':10,'timing':{'mode':mode},'window_seconds':10}
                if value is not ABSENT:
                    scenario['summon_count']=value
                cur[label]=invoke(scenario,name,label)
            inactive_contexts[name]=cur
    # Existing public test contract, explicitly synthetic: do not assert live layer is unknown.
    synthetic_rules=copy.deepcopy(module_rules())
    synthetic_rules[MOD]['hp_composition_verified']=False
    synthetic_records=[]
    with patch('rouge.summons.module_rules',return_value=synthetic_rules):
        for skill in (1,2):
            for mode in ('continuous','frames'):
                for label,value in [('int_zero',0),('int_one',1),('string_one','1'),('int_two',2)]:
                    scenario=scenario_for(qualified,skill,mode,10)
                    scenario.update(summon_count=value,effects=[{'kind':'hp_pct','value':.5,'target_scope':'all_units'}],
                                    relic_ids=['rogue_6_relic_legacy_91'])
                    synthetic_records.append(invoke(scenario,f'synthetic_hp_layer_pending/s{skill}/{mode}',label,True))
finally:
    reporting.build_report = original_report

# Observer equivalence controls execute the ORIGINAL unwrapped public path again.
observer_controls=[]
for source in [records[0],records[4],records[6],records[224],records[228],records[230],
               next(r for r in records if r['context'].startswith('inactive/')),
               next(r for r in records if r['count_label']=='bool_false' and r['context'].startswith('extra/'))]:
    scenario=copy.deepcopy(source['input'])
    # These fixed control inputs contain no nonfinite floats or synthetic fixture.
    replay=invoke(scenario,'observer_equivalence/'+str(source['id']),source['count_label'],instrument=False)
    same=(source['status']==replay['status'] and
          (source.get('result_sha256')==replay.get('result_sha256') if source['status']=='returned' else
           source['exception']['type']==replay['exception']['type'] and source['exception']['message']==replay['exception']['message']))
    observer_controls.append({'observed_id':source['id'],'unwrapped_id':replay['id'],'same_public_outcome':same})

pairings=[]
for name, cur in contexts.items():
    for left,right in [('absent_default','int_one'),('int_zero','string_zero'),('int_one','float_one'),
                       ('int_one','string_one'),('int_one','string_decimal_one'),('int_one','bool_true')]:
        a,b=cur[left],cur[right]
        item={'context':name,'left_id':a['id'],'right_id':b['id'],'left':left,'right':right,
              'statuses':[a['status'],b['status']]}
        if a['status']=='returned' and b['status']=='returned':
            item['classification']='both_returned'
            item['whole_result_identical']=a['result_sha256']==b['result_sha256']
            item['whole_result_differences']=differences(a['result'],b['result'])
            nonreport_a={k:v for k,v in a['result'].items() if k!='report'}
            nonreport_b={k:v for k,v in b['result'].items() if k!='report'}
            item['nonreport_result_identical']=digest(nonreport_a)==digest(nonreport_b)
        elif a['status']=='returned' and b['status']=='raised':
            item['classification']='numeric_returned_other_raised'
            item['exception']={k:b['exception'][k] for k in ('type','message')}
        elif a['status']=='raised' and b['status']=='raised':
            item['classification']='both_rejected_not_a_pass'
            item['same_error_type_message']=(a['exception']['type'],a['exception']['message'])==(b['exception']['type'],b['exception']['message'])
        else:
            item['classification']='other_asymmetry'
        if a.get('model_reached_report') and b.get('model_reached_report'):
            item['model_before_report_identical']=a['pre_report_result_sha256']==b['pre_report_result_sha256']
        pairings.append(item)

inactive_checks=[]
for name,cur in inactive_contexts.items():
    default=cur['absent_default']
    for label,record in cur.items():
        if label=='absent_default':
            continue
        inactive_checks.append({'context':name,'default_id':default['id'],'other_id':record['id'],
                                'label':label,'both_returned':default['status']==record['status']=='returned',
                                'whole_result_identical':default.get('result_sha256')==record.get('result_sha256')
                                if default['status']==record['status']=='returned' else False})

synthetic_checks=[]
for record in synthetic_records:
    existing=record['observed_report_calls'][-1]['existing_result_before_report'] if record.get('observed_report_calls') else None
    item={'id':record['id'],'context':record['context'],'status':record['status'],
          'synthetic_only':True,'live_module_layer_asserted_unknown':False}
    if existing is not None:
        token=next(t for t in existing['relic_token_stats'] if t['id']==TOKEN)
        item.update(hp=token['hp'],regeneration_rate=token['regeneration_rate'],
                    hp_composition_pending=token['module_reference']['hp_composition_pending'],
                    complete=existing['complete'])
    if record['status']=='returned':
        sections={s['id']:s for s in record['result']['report']['sections']}
        item['regeneration_metrics']={m['key']:m['value'] for m in sections.get('regeneration',{}).get('metrics',[])}
    else:
        item['exception']={k:record['exception'][k] for k in ('type','message')}
    synthetic_checks.append(item)

source_after=file_hashes()
summary={
    'utc':datetime.now(timezone.utc).isoformat(),'frozen_head':freeze['frozen_head'],
    'source_scope':freeze['scope'],'implementation_patch_created':False,'tracked_source_edits':False,
    'wine_gui_game_run':False,'private_state_read':False,'nonfinite_input_encoding':'tagged float labels, JSON allow_nan=False; not used as successful numeric validation',
    'diagnostic_instrumentation':'Temporarily observes deep copies before original build_report. Original always executes, exceptions are preserved. No source edit or report replacement.',
    'calls_total':len(records),'status_counts':dict(Counter(r['status'] for r in records)),
    'synthetic_calls':len(synthetic_records),'observer_equivalence_controls':observer_controls,
    'all_observer_controls_same':all(r['same_public_outcome'] for r in observer_controls),
    'pair_classification_counts':dict(Counter(r['classification'] for r in pairings)),
    'pair_model_before_report_equal_count':sum(r.get('model_before_report_identical') is True for r in pairings),
    'pair_nonreport_equal_count':sum(r.get('nonreport_result_identical') is True for r in pairings),
    'report_error_calls':[{'id':r['id'],'context':r['context'],'count_label':r['count_label'],
                          'exception':{k:r['exception'][k] for k in ('type','message')}}
                         for r in records if r['status']=='raised' and r.get('model_reached_report')],
    'inactive_checks':inactive_checks,'all_inactive_results_unchanged':all(r['whole_result_identical'] for r in inactive_checks),
    'synthetic_guard_checks':synthetic_checks,
    'all_caller_inputs_unchanged':all(r['caller_unchanged'] for r in records),
    'cached_catalog_before_sha256':catalog_before,'cached_catalog_after_sha256':digest(catalog()),
    'cached_catalog_unchanged':catalog_before==digest(catalog()),
    'cached_module_rules_before_sha256':rules_before,'cached_module_rules_after_sha256':digest(module_rules()),
    'cached_module_rules_unchanged':rules_before==digest(module_rules()),
    'source_hashes_before':source_before,'source_hashes_after':source_after,
    'frozen_source_unchanged':source_before==source_after==freeze['files'],
    'failure_calls_are_passes':False,
}
(ROOT/'public-outcomes.json').write_text(json.dumps({'records':safe(records),'paired_observations':pairings},ensure_ascii=False,indent=2,allow_nan=False)+'\n')
(ROOT/'SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
assert summary['all_observer_controls_same']
assert summary['all_inactive_results_unchanged']
assert summary['all_caller_inputs_unchanged'] and summary['cached_catalog_unchanged'] and summary['cached_module_rules_unchanged']
assert summary['frozen_source_unchanged']
print(json.dumps({k:summary[k] for k in ('frozen_head','calls_total','status_counts','synthetic_calls','pair_classification_counts',
                                       'all_observer_controls_same','all_inactive_results_unchanged','all_caller_inputs_unchanged',
                                       'cached_catalog_unchanged','cached_module_rules_unchanged','frozen_source_unchanged')},ensure_ascii=False))
