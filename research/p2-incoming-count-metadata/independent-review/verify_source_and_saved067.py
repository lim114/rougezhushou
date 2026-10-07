from pathlib import Path
import hashlib,json,gzip,collections,datetime

B=Path('/workspace/.continuation/p2-incoming-count-metadata-067')
R=Path('/workspace/rougezhushou')
F=Path('/workspace/.continuation/p2-incoming-count-report-audit-067')
OUT=Path(__file__).parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=json.loads((B/'source-receipt.json').read_bytes())
freeze=json.loads((F/'freeze-receipt.json').read_bytes())
for name,digest in freeze['files'].items():assert sha(F/'frozen'/name)==digest,name
raws={}
for name,record in source['sources'].items():
    path=Path(record['path']);assert sha(path)==record['sha256'],name
    raws[name]=json.loads(path.read_bytes())
op=raws['character_table']['char_1042_phatm2']
selectors={
    'character_table.char_1042_phatm2.talents[0].candidates':op['talents'][0]['candidates'],
    'character_table.char_1042_phatm2.talents[1].candidates':op['talents'][1]['candidates'],
    'skill_table.skchr_phatm2_3.levels[9]':raws['skill_table']['skchr_phatm2_3']['levels'][9]}
assert selectors==source['selectors']
for candidate in op['talents'][1]['candidates']:
    assert candidate['unlockCondition']=={'phase':'PHASE_2','level':1}
    assert {v['key']:v['value'] for v in candidate['blackboard']}['value']==70
for name,record in source['reused_research'].items():assert sha(R/name)==record['sha256'],name
for name,digest in source['artifact_hashes'].items():assert sha(B/name)==digest,name
assert sha(B/'metadata.patch')=='a8bae03fe3b1a7ab34da2b26fce646352c02f80decf0b4819cd2dda41407848b'
baseline=(F/'frozen/rouge/operator_engine.py').read_bytes()
draft=(B/'draft/rouge/operator_engine.py').read_bytes()
old=b"'attacks_requested':int(self.s['enemy_attack_count']),"
new=b"'attacks_requested':int(self.option('enemy_attack_count',0,maximum=10000,integer=True)),"
assert baseline.count(old)==1 and draft.count(new)==1
assert draft.replace(new,old,1)==baseline

with gzip.open(B/'paired-full-outcomes.json.gz','rt') as f:paired=json.load(f)
with gzip.open(B/'prior-readonly-audit/public-outcomes.json.gz','rt') as f:prior=json.load(f)
counts=collections.Counter();aliases={'one_decimal_text':'one_int','one_exp_text':'one_int',
    'twenty_decimal_text':'twenty_int','twenty_exp_text':'twenty_int','maximum_exp_text':'maximum_int'}
assert paired['baseline_head']==prior['head']==freeze['head']
assert len(paired['cases'])==len(prior['cases'])==1620
for name,row in paired['cases'].items():
    assert row['scenario']==prior['cases'][name]['scenario']
    assert row['before']==prior['cases'][name]['outcome']
    if row['before']==row['after']:
        counts['whole_outcomes_unchanged']+=1
        counts['old_errors_unchanged' if row['after']['error'] is not None else 'successes_unchanged']+=1
    else:
        label=name.rsplit(':',1)[1];assert label in aliases
        control=name.rsplit(':',1)[0]+':'+aliases[label]
        assert row['after']==prior['cases'][control]['outcome']
        assert row['before']['result'] is None
        assert row['before']['error']['type']=='ValueError'
        assert row['before']['error']['message'].startswith('invalid literal for int() with base 10:')
        assert row['after']['error'] is None
        ref=row['after']['result']['neural_incoming_reference']
        assert not ref['events_scheduled'] and ref['attack_times_seconds'] is None
        counts['legal_alias_errors_recovered']+=1
alias_pairs=json.loads((B/'prior-readonly-audit/paired-outcome-comparison.json').read_bytes())['pairs']
for pair in alias_pairs.values():
    assert paired['cases'][pair['left']]['after']==paired['cases'][pair['right']]['after']
assert counts['whole_outcomes_unchanged']==1440
assert counts['old_errors_unchanged']==520 and counts['legal_alias_errors_recovered']==180
assert len(alias_pairs)==528
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'baseline_commit':freeze['head'],
    'frozen_files_verified':len(freeze['files']),'fresh_raw_source_hashes_verified':True,
    'exact_source_selector_count':len(selectors),'prior_research_hashes_verified':len(source['reused_research']),
    'code_difference_only_validated_metadata_conversion':True,'raw_boolean_guard_and_source_gates_unchanged':True,
    'numeric_none_scope_clock_and_damage_formula_bytes_unchanged':True,
    'saved_author_outcome_pairs_strictly_recompared':len(paired['cases']),
    'saved_author_counts':counts,'saved_alias_pairs_strictly_equal':len(alias_pairs),
    'author_calls_not_reexecuted':3240,'current_source_hashes':source['artifact_hashes'],
    'actual_attack_times_first_tick_and_native_binding_unknown':True,
    'native_or_wine_or_gui_validation':False}
(OUT/'source-and-saved-comparison.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(out,ensure_ascii=False))
