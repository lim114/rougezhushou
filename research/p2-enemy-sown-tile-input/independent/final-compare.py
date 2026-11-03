from pathlib import Path
import collections
import gzip
import hashlib
import json

out=Path(__file__).resolve().parent


def read(name):
    with gzip.open(out/name,'rt',encoding='utf-8')as handle:
        return json.load(handle)


def strict(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True)


before=read('discovery64-public.json.gz')
after=read('final-draft-public.json.gz')
assert len(before['records'])==len(after['records'])
changed,unchanged,unexpected,canonical_drift=[],[],[],[]
groups=collections.Counter()
expected_error={'accepted':False,'error_type':'ValueError',
                'error':'enemy_on_sown_tile 不接受文本条件；请使用布尔值。'}
for a,b in zip(before['records'],after['records']):
    assert a['key']==b['key'] and strict(a['input'])==strict(b['input'])
    key=a['key']
    active_text=a['group']=='active_text' or (
        a['group']=='four_sui_context' and isinstance(a['input']['enemy_on_sown_tile'],str))
    if strict(a['outcome'])==strict(b['outcome']):
        unchanged.append(key)
        if active_text:unexpected.append(key)
    else:
        changed.append(key);groups[a['group']]+=1
        if not active_text or strict(b['outcome'])!=strict(expected_error):unexpected.append(key)
    if strict(a['comparison_outcome'])!=strict(b['comparison_outcome']):canonical_drift.append(key)
source_changes=[n for n,h in before['summary']['source_hashes'].items()
                if after['summary']['source_hashes'].get(n)!=h]
receipt={'cases':len(after['records']),
         'public_calls':before['summary']['public_calls']+after['summary']['public_calls'],
         'baseline_reuse':'Same immutable frozen64 discovery results reused after source rehash; no relabeling of another HEAD',
         'comparison':'strict serialized full JSON, preserving numeric types, reports and error types/text',
         'changed_cases':len(changed),'unchanged_cases':len(unchanged),'changed_groups':dict(groups),
         'unexpected_changes':unexpected,'typed_comparison_output_changes':canonical_drift,
         'active_text_accepted':after['summary']['active_text_accepted'],
         'inactive_or_locked_drift':after['summary']['inactive_or_locked_drift'],
         'nontext_math_comparison_drift':after['summary']['nontext_math_comparison_drift'],
         'caller_isolation_errors':after['summary']['caller_isolation_errors'],
         'catalog_preserved':after['summary']['catalog_preserved'],'source_changes':source_changes,
         'source_scope_correct':source_changes==['rouge/operator_engine.py','rouge/operator_options.py'],
         'root_source_edits':0,'author_source_edits':0,'native_validation':False,
         'evidence_sha256':{n:hashlib.sha256((out/n).read_bytes()).hexdigest()
                            for n in('discovery64-public.json.gz','final-draft-public.json.gz')}}
receipt['passed']=not any((unexpected,canonical_drift,receipt['active_text_accepted'],
                          receipt['inactive_or_locked_drift'],receipt['nontext_math_comparison_drift'],
                          receipt['caller_isolation_errors'])) and (
    receipt['catalog_preserved'] and receipt['source_scope_correct'])
(out/'final-matrix-comparison.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(receipt,ensure_ascii=False))
assert receipt['passed']
