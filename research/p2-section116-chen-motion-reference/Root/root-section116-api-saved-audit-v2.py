"""Root-only Saved comparison. No project import or formatter re-execution."""
import hashlib,json,re,sys
from pathlib import Path
B=Path('/workspace/.continuation')
H=B/'section109-empty-target-original-probe-source-v1/native_evidence.py'
assert hashlib.sha256(H.read_bytes()).hexdigest()=='f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a'
sys.path.insert(0,str(H.parent))
from native_evidence import read_record,assert_native_equal,freeze,source_map
G=json.loads((B/'section116-candidate-source-v1.json').read_text())
assert source_map('/workspace/rougezhushou')==G['source_sha256']
IDS={'chen_motion_front','chen_motion_back'}
def load(name):
    d=B/name;o=json.loads((d/'observations.json').read_text())
    assert o['observation_complete'] and o['consumer_error_count']==0
    assert o['actual_completed_cases']==43 and o['actual_public_calls']==172 and o['actual_native_records']==215
    rows={}
    for m in o['records']:
        v=read_record(d/'native',m)
        assert_native_equal(v['after'],v['before'],m['case']+':'+m['phase'])
        if m['kind']=='actual-public-consumer':
            assert v['error'] is None
            rows[m['case'],m['phase']]=v
    return rows
old=load('section116-original-api-actual-v1');new=load('section116-candidate-api-actual-v1')
assert old.keys()==new.keys()
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
references=0
for (case,phase),n in new.items():
    o=old[case,phase]
    if phase=='calculate_damage':
        candidate=freeze(n['result']);blocks=[s for s in candidate['report']['sections'] if s['id'] in IDS]
        caller=n['after'][0];face=caller.get('chen_motion_orientation');expected=0 if face is None else (2 if face=='both' else 1)
        assert len(blocks)==expected,(case,face)
        for b in blocks:
            values={x['key']:x['value'] for x in b['metrics']}
            assert values['actual_damage'] is None and values['actual_end'] is None
            assert sum('资源SHA-256：' in x for x in b['notes'])==3
            assert any('不代表实际执行顺序' in x for x in b['notes'])
            references+=1
        candidate['report']['sections'][:]=[s for s in candidate['report']['sections'] if s['id'] not in IDS]
        assert_native_equal(candidate,o['result'],case+':full native result without only new reference sections')
        assert_native_equal(n['after'],o['after'],case+':original candidate caller')
    elif phase=='format_estimate':assert_native_equal(n['result'],o['result'],case+':complete estimate text')
    else:
        result=new[case,'calculate_damage']['result'];titles=[s['title'] for s in result['report']['sections'] if s['id'] in IDS]
        assert strip_text(n['result'],titles)==o['result'],(case,phase,'complete old text after exact new sections')
assert source_map('/workspace/rougezhushou')==G['source_sha256']
receipt={'kind':'ROOT_ACTUAL_SAVED_116_ORIGINAL_CANDIDATE_WHOLE_NATIVE_AUDIT','passed':True,'workflow_complete':True,'source_drift':[],'cases':43,'native_records_decoded':430,'numeric_and_estimate_unchanged':True,'whole_report_text_unchanged_after_only_reference_sections':True,'original_reference_blocks_added':references,'formatter_reexecution':False,'native_windows_game_chat_verified':False}
out=B/'section116-api-saved-actual-v2.json';assert not out.exists();out.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');print(json.dumps(receipt))
