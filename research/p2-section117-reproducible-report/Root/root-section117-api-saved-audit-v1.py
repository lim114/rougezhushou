"""Root Saved full graph/text audit of the single additive report feature."""
import hashlib,json,sys
from pathlib import Path
B=Path('/workspace/.continuation');H=B/'section109-empty-target-original-probe-source-v1/native_evidence.py'
assert hashlib.sha256(H.read_bytes()).hexdigest()=='f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a'
sys.path.insert(0,str(H.parent))
from native_evidence import read_record,assert_native_equal,freeze,source_map
G=json.loads((B/'section117-candidate-source-v1.json').read_text())
assert source_map('/workspace/rougezhushou')==G['source_sha256']
def added(block):return block['id']=='calculation_context' or block['id'].startswith(('event_clock_','output_domain_'))
def load(phase):
    d=B/('section117-'+phase+'-api-actual-v1');o=json.loads((d/'observations.json').read_text())
    assert o['observation_complete'] and o['consumer_error_count']==0 and o['source_and_CORE_unchanged']
    assert (o['actual_completed_cases'],o['actual_public_calls'],o['actual_native_records'])==(19,76,95)
    rows={}
    for m in o['records']:
        v=read_record(d/'native',m);assert_native_equal(v['after'],v['before'],m['case']+':'+m['phase'])
        if m['kind']=='actual-public-consumer':assert v['error'] is None;rows[m['case'],m['phase']]=v
    return rows
def strip_text(text,titles):
    lines=text.split('\n');out=[];i=0
    while i<len(lines):
        if lines[i] in {'【'+t+'】' for t in titles}:
            assert out and out[-1]=='';out.pop();i+=1
            while i<len(lines) and lines[i]!='':i+=1
            continue
        if lines[i] in {t+'：' for t in titles}:
            i+=1
            while i<len(lines) and lines[i].startswith('• '):i+=1
            continue
        out.append(lines[i]);i+=1
    return '\n'.join(out)
old=load('original');new=load('candidate');assert old.keys()==new.keys();count=0;scalar_checks=0
for (case,phase),n in new.items():
    o=old[case,phase]
    if phase=='calculate_damage':
        result=n['result'];candidate=freeze(result);blocks=[s for s in candidate['report']['sections'] if added(s)]
        ids=[s['id'] for s in blocks];assert len(ids)==len(set(ids)) and ids[0]=='calculation_context'
        assert len(blocks)>=2;count+=len(blocks)
        context={x['key']:x['value'] for x in blocks[0]['metrics']}
        assert_native_equal(context['window'],result['estimate']['skill']['window_seconds'],'adopted window reference');scalar_checks+=1
        for key in ('streams','recharge_streams'):
            clocks=[s for s in blocks if s['id'].startswith('event_clock_'+key+'_')]
            streams=result['timing'].get(key,[]) if result['timing'].get('mode')=='frames' else []
            assert len(clocks)==len(streams)
            for index,(b,s) in enumerate(zip(clocks,streams)):
                assert b['id']=='event_clock_'+key+'_'+str(index)
                values={m['key']:m['value'] for m in b['metrics']}
                for field in ('start_frames','release_frames','impact_frames','times_seconds','emitted_impact_frames','emitted_times_seconds'):
                    v=s.get(field)
                    for suffix,wanted in (('_count',len(v) if v is not None else None),('_first',v[0] if v else None),('_last',v[-1] if v else None)):
                        assert_native_equal(values[field+suffix],wanted,'saved independent phase/stream field');scalar_checks+=1
        candidate['report']['sections'][:]=[s for s in candidate['report']['sections'] if not added(s)]
        assert_native_equal(candidate,o['result'],case+':entire native graph after only new report blocks')
        assert_native_equal(n['after'],o['after'],case+':entire original/candidate caller')
    else:
        titles=[s['title'] for s in new[case,'calculate_damage']['result']['report']['sections'] if added(s)]
        assert strip_text(n['result'],titles)==o['result'],(case,phase,'complete text after exact additive tables')
assert source_map('/workspace/rougezhushou')==G['source_sha256']
r={'kind':'ROOT_ACTUAL_SAVED_117_WHOLE_NATIVE_AND_THREE_TEXT_AUDIT','passed':True,'workflow_complete':True,'source_drift':[],'cases':19,'native_records_decoded':190,'new_report_blocks':count,'stored_stream_scalar_checks':scalar_checks,'whole_numeric_graph_and_caller_unchanged':True,'whole_three_texts_unchanged_after_only_added_tables':True,'project_formatter_reexecution':False,'native_windows_game_chat_verified':False}
O=B/'section117-api-saved-actual-v1.json';assert not O.exists();O.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps(r))
