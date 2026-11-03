"""Actual public-only equivalence, call counts and profiled small-sample times."""
from copy import deepcopy
import cProfile
import gzip
import hashlib
import io
import json
from pathlib import Path
import pstats
import sys
import tempfile
import time
import types
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT))
from rouge import node_catalog as catalog,choice_recruitment_results


def load(name,path):
    module=types.ModuleType('rouge.'+name)
    module.__package__='rouge'
    module.__file__=str(ROOT/'rouge/event_planning.py')
    exec(compile(path.read_bytes(),str(path),'exec'),module.__dict__)
    return module


def canonical(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')
def digest(value):return hashlib.sha256(canonical(value)).hexdigest()


def main():
    before=load('_resources_before290',HERE/'before-event-planning.py')
    after=load('_resources_candidate290',HERE/'candidate-event-planning.py')
    counters={'before':0,'after':0}
    profiles={'before':cProfile.Profile(),'after':cProfile.Profile()}
    modules={'before':before,'after':after}
    for label,module in modules.items():
        original=module.choice_eligibility
        def counted(*args,_label=label,_original=original,**kwargs):
            counters[_label]+=1
            return _original(*args,**kwargs)
        module.choice_eligibility=counted
    contexts=[{},
        {'floor':2,'node_type':'不期而遇','entry_mode':'content','resources':{'hope':20,'gold':3,'hp':5,'ap':2}},
        {'floor':1,'difficulty':3,'node_type':'作战','entry_mode':'natural'}]
    checks=[]
    def check(name,value):checks.append({'label':name,'passed':bool(value)})
    matrix=[]
    outputs={'before':[],'after':[]}
    actual_seconds={'before':0.0,'after':0.0}
    events=deepcopy(catalog._data()['events'])
    ordinal=0
    for context_index,context in enumerate(contexts):
        for event in events:
            for scene in event['scenes']:
                record={'context_index':context_index,'event_id':event['id'],'scene_key':scene['key'],
                        'choice_count':len(scene['choices'])}
                results={}
                order=('before','after') if ordinal%2==0 else ('after','before')
                for label in order:
                    args=(event['id'],scene['key'],deepcopy(context))
                    input_before=deepcopy(args)
                    count_before=counters[label]
                    started=time.perf_counter()
                    result=profiles[label].runcall(modules[label].choice_resources,*args)
                    elapsed=time.perf_counter()-started
                    record[label+'_profiled_seconds']=elapsed
                    record[label+'_eligibility_calls']=counters[label]-count_before
                    record[label+'_sha256']=digest(result)
                    actual_seconds[label]+=elapsed
                    results[label]=result
                    check(label+':input_unchanged:'+str(ordinal),args==input_before)
                    outputs[label].append({'context_index':context_index,'event_id':event['id'],
                        'scene_key':scene['key'],'output':result})
                check('exact_output:'+str(ordinal),results['before']==results['after'])
                check('before_calls:'+str(ordinal),record['before_eligibility_calls']==len(scene['choices']))
                check('after_calls:'+str(ordinal),record['after_eligibility_calls']==bool(scene['choices']))
                matrix.append(record)
                ordinal+=1
    valid_event='community_group_018'
    valid_scene=valid_event+':scene:0'
    invalid_inputs=[
        (None,valid_scene,None),('',valid_scene,None),(1,valid_scene,None),('not-real',valid_scene,None),
        (valid_event,None,None),(valid_event,'',None),(valid_event,1,None),(valid_event,'not-real',None),
        (valid_event,'community_group_007:scene:0',None),
        *[(valid_event,valid_scene,context) for context in (
            [],True,{'floor':True},{'floor':0},{'floor':7},{'difficulty':True},{'difficulty':16},
            {'special_region':0},{'entry_mode':'invalid'},{'resources':[]},{'resources':{'gold':-1}},
            {'resources':{'hp':True}},{'gold':True},{'gold':-1},
            {'gold':3,'resources':{'gold':4}},{'item_quantities':{'test':True}},
            {'item_presence':{'test':1}},{'inventory_complete':1}))]
    exceptions=[]
    def outcome(module,args):
        original=deepcopy(args)
        try:result={'returned':module.choice_resources(*args)}
        except Exception as error:result={'exception_type':type(error).__module__+'.'+type(error).__qualname__,
                                         'message':str(error),'args':list(error.args)}
        check('invalid_input_unchanged:'+str(len(exceptions)),args==original)
        return result
    for args in invalid_inputs:
        old=outcome(before,deepcopy(args))
        new=outcome(after,deepcopy(args))
        check('invalid_outcome:'+str(len(exceptions)),old==new)
        exceptions.append({'input':args,'before':old,'after':new,'equal':old==new})
    # A full valid source control followed by a changed temporary public HTML,
    # then a second external query. No hash/typed gate is mocked or weakened.
    manifest=json.loads((ROOT/choice_recruitment_results.MANIFEST).read_text(encoding='utf-8'))
    fresh=[]
    with tempfile.TemporaryDirectory(prefix='rouge-290-query-opt-public-') as directory:
        clone=Path(directory)
        for relative in [choice_recruitment_results.MANIFEST,*manifest['files']]:
            destination=clone/relative
            destination.parent.mkdir(parents=True,exist_ok=True)
            destination.write_bytes((ROOT/relative).read_bytes())
        with patch.object(choice_recruitment_results,'ROOT',clone):
            for phase in ('valid','tampered'):
                if phase=='tampered':
                    html=clone/'research/p3-choice-recruitment-290/prts-events-440271.html'
                    html.write_bytes(html.read_bytes()+b' ')
                results={}
                for label,module in modules.items():
                    calls_before=counters[label]
                    result=module.choice_resources(valid_event,valid_scene)
                    ref=next(r for r in result['rows'] if r['choice_key']==valid_scene+':choice:1')['choice_eligibility']['recruitment_result_reference']
                    check('source_'+phase+':'+label,ref['status']==('documented_reference' if phase=='valid' else 'unknown'))
                    check('source_role_'+phase+':'+label,ref['annotation_role']==('selection_result' if phase=='valid' else None))
                    fresh.append({'phase':phase,'module':label,'eligibility_calls':counters[label]-calls_before,
                                  'full_output':result})
                    results[label]=result
                check('fresh_source_output:'+phase,results['before']==results['after'])
    check('real_source_still_valid',choice_recruitment_results.source_data() is not None)
    for label in modules:
        profiles[label].dump_stats(str(HERE/(label+'-matrix.pstats')))
        stream=io.StringIO()
        pstats.Stats(profiles[label],stream=stream).sort_stats('cumulative').print_stats(35)
        (HERE/(label+'-profile.txt')).write_text(stream.getvalue(),encoding='utf-8')
        compressed=gzip.compress(canonical(outputs[label]),mtime=0)
        (HERE/(label+'-matrix-output.json.gz')).write_bytes(compressed)
    result={'scope':'Actual public scene-query equivalence only; no GUI/full/OCR performance inference.',
        'contexts':contexts,'event_groups':len(events),'scene_count':sum(len(e['scenes']) for e in events),
        'matrix_queries_per_module':len(matrix),'matrix_records':matrix,
        'matrix_profiled_seconds':actual_seconds,
        'matrix_eligibility_calls':{label:sum(r[label+'_eligibility_calls'] for r in matrix) for label in modules},
        'invalid_input_count':len(exceptions),'invalid_input_outcomes':exceptions,'warm_source_probes':fresh,
        'checks':checks,'failed_checks':sum(not r['passed'] for r in checks),
        'timing_limits':['Single local profiled pass with alternating order; not a robust benchmark or timeout-cause proof.',
            'Profiled function calls and fresh file checks are included; serialization and source clones are excluded from matrix timing.',
            'No comparison to whole offline suite, OCR or end-to-end sampling speed.'],
        'live_file_untouched':hashlib.sha256((ROOT/'rouge/event_planning.py').read_bytes()).hexdigest()==hashlib.sha256((HERE/'before-event-planning.py').read_bytes()).hexdigest(),
        'private_state_or_gui_accessed':False}
    with (HERE/'public-equivalence-and-profile.json').open('x',encoding='utf-8') as stream:json.dump(result,stream,ensure_ascii=False,indent=2)
    print(json.dumps({k:result[k] for k in ('event_groups','scene_count','matrix_queries_per_module',
        'matrix_profiled_seconds','matrix_eligibility_calls','invalid_input_count','failed_checks','live_file_untouched')},ensure_ascii=False))
    raise SystemExit(int(result['failed_checks']>0 or not result['live_file_untouched']))


if __name__=='__main__':main()
