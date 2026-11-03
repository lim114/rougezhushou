"""Independent strict saved-row oracle, with zero API imports or calls."""
from pathlib import Path
import hashlib
import json

OUT=Path(__file__).resolve().parent
AUTHOR=Path('/workspace/.continuation/p2-neural-condition-text-input-083')
def sha(data):return hashlib.sha256(data).hexdigest()
def save(name,value):
    with (OUT/name).open('x',encoding='utf-8') as f:
        json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
names=['public-baseline083.json','public-draft083.json','saved-comparison083.json','compare_saved083.py']
bindings=[]
for name in names:
    source=AUTHOR/name;data=source.read_bytes()
    target=OUT/'fixed-author-saved-results'/name
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('xb') as f:f.write(data)
    assert source.read_bytes()==data
    bindings.append({'source_path':str(source),'archive_path':str(target.relative_to(OUT)),
                     'bytes':len(data),'sha256':sha(data)})
old=json.loads((OUT/'fixed-author-saved-results/public-baseline083.json').read_bytes())
new=json.loads((OUT/'fixed-author-saved-results/public-draft083.json').read_bytes())
receipt=json.loads((OUT/'fixed-author-saved-results/saved-comparison083.json').read_bytes())
cases=json.loads((OUT/'fixed-author-inputs/public-cases083.json').read_bytes())
assert len(old)==len(new)==len(cases)==432
changed=[];same=[];errors=[];targets=[]
for index,(a,b,scenario) in enumerate(zip(old,new,cases,strict=True)):
    assert a['index']==b['index']==index and a['scenario']==b['scenario']==scenario
    assert ('result'in a) != ('error'in a)
    if 'error'in a:
        assert b==a,('exact complete old-error row',index,a.get('error'),b.get('error'))
        errors.append(index)
        continue
    fields=[]
    if scenario['operator']in ['char_1042_phatm2','char_4204_mantra']:
        if not scenario.get('target_enemy'):fields.append('enemy_is_boss')
        fields.append('enemy_in_neural_break')
    field=next((name for name in fields if isinstance(scenario.get(name),str)),None)
    if scenario.get('target_enemy'):
        targets.append({'index':index,'target_enemy':scenario['target_enemy'],
                        'boss_text_overridden':isinstance(scenario.get('enemy_is_boss'),str)})
    if field is None:
        assert b==a,('all JSON and all three text fields',index)
        assert all(name in a for name in ['result','report_text','technical_report_text','estimate_text'])
        same.append(index)
    else:
        expected={'index':index,'scenario':scenario,
                  'error':{'type':'ValueError','message':field+' 不接受文本条件；请使用布尔值。'}}
        assert b==expected,('all actual consumed text must reject',index,field,b.get('error'))
        changed.append({'index':index,'field':field,'operator':scenario['operator'],
                        'skill':scenario['skill'],'legacy_success':True})
assert changed==receipt['accepted_to_explicit_text_error']
assert same==receipt['whole_record_same_accepted']
assert errors==receipt['exact_same_olderrors']
assert receipt['passed']is True and receipt['API_calls']==0 and receipt['saved_pairs']==432
assert [len(changed),len(same),len(errors)]==[116,256,60]
unique_targets={json.dumps(row['target_enemy'],sort_keys=True) for row in targets}
assert len(unique_targets)==2
save('saved-author-recomparison083.json',{'status':'passed','saved_pairs':432,'new_API_calls':0,
    'counts':{'text_rejected':116,'whole_success_unchanged':256,'exact_old_errors_unchanged':60},
    'oracle':'For every baseline success derive processed field consumption from fixed actual owner/all-skills and selected-enemy identity override; do not assume unchanged success is valid by observing a diff.',
    'all_input_rows_bound_to_frozen_case_list':True,'all_row_indexes_and_shapes_checked':True,
    'all_success_rows_include_complete_JSON_and_all_three_texts':True,'all_old_error_rows_exactly_preserved':True,
    'all_changed_rows_are_exact_expected_only_str_errors':True,'author_receipt_arrays_strictly_equal':True,
    'unique_accepted_selected_targets':2,'accepted_target_rows':targets,'bindings':bindings,
    'threshold_clock_helpers_not_changed':True,'Qt':False,'Wine':False,'tracked_mutations':False})
print(json.dumps({'status':'passed','saved_pairs':432,'new_API_calls':0,
    'counts':[116,256,60],'recomparison_sha256':sha((OUT/'saved-author-recomparison083.json').read_bytes())}))
