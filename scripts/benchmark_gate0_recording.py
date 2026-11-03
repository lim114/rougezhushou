"""Replay identical recorded observations, measuring only the recording path."""
from contextlib import closing
import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from rouge.session_recording import SessionRecorder
from scripts.gate0_report import percentile


def benchmark(path, repeats=5):
    rows=[json.loads(line)for line in path.read_text('utf8').splitlines()]
    state={};samples=[]
    for row in rows:
        if row['event']=='state_baseline':state=deepcopy(row['state'])
        if row['event']=='sample':
            state.update(row['state_diff'])
            observation={key:row.get(key)for key in ('page','captured_at','performance','capture_ms','map')}
            observation['_sampling']=row.get('sampling');observation['stage']={'id':row.get('stage_id')}
            replay_state=deepcopy(state)
            replay_state['id']=replay_state.pop('run_id')
            samples.append((observation,replay_state,{'applied':row['applied'],'reason':row['reason'],'ui_ms':row['ui_ms']}))
    if not samples:raise ValueError('会话中没有可复放的采样记录。')
    results={'scope':'recording_path_only_same_observations_not_capture_or_OCR','samples':len(samples),'repeats':repeats}
    with tempfile.TemporaryDirectory(prefix='rouge-gate0-benchmark-')as tmp:
        # One complete warm-up precedes alternating on/off rounds.
        with closing(SessionRecorder(Path(tmp)/'warmup',scenario='normal'))as recorder:
            for observation,state,kwargs in samples:recorder.sample(observation,state,**kwargs)
        measurements={False:[],True:[]};drains=[]
        for index in range(repeats):
            for enabled in ((False,True)if index%2==0 else(True,False)):
                recorder=SessionRecorder(Path(tmp)/str(index),scenario='normal')if enabled else None
                try:
                    for observation,state,kwargs in samples:
                        start=time.perf_counter_ns()
                        if recorder is not None:recorder.sample(observation,state,**kwargs)
                        measurements[enabled].append((time.perf_counter_ns()-start)/1000)
                finally:
                    if recorder is not None:
                        start=time.perf_counter_ns();recorder.close();drains.append((time.perf_counter_ns()-start)/1000000)
        for enabled,values in measurements.items():
            results['enabled'if enabled else'disabled']={'median_us':percentile(values,.5),'p95_us':percentile(values,.95),'events':len(values)}
        results['queue_drain_p95_ms']=percentile(drains,.95)
    return results


if __name__=='__main__':
    parser=argparse.ArgumentParser(description='同一日志输入的记录路径开销；不重跑OCR')
    parser.add_argument('events',type=Path);parser.add_argument('--repeats',type=int,default=5)
    args=parser.parse_args()
    if args.repeats<1:parser.error('--repeats 至少为1')
    print(json.dumps(benchmark(args.events,args.repeats),ensure_ascii=False,indent=2))
