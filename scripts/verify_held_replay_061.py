"""Six scoped actual-reader regressions against the preserved 0.60 source."""
import argparse
import json
from pathlib import Path
import time
import verify_hybrid_059 as replay

ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'.cache/research/held-performance-061/actual-reader'


def main():
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=('prepare','run','summary'))
    args=parser.parse_args()
    if args.mode=='prepare':
        FOLDER.mkdir(exist_ok=False)
        replay.BEFORE=ROOT/'.cache/batch-061-before'
        replay.make_package(FOLDER)
        selected={'kaltsit_owned:native','run-mechanist-selected:native','run-relic-multicard:native',
                  'myrtle_owned:animation','main-menu-independent-0','operator-to-main-menu'}
        cases=[c for c in replay.planned_cases() if c['id'] in selected]
        assert len(cases)==6
        replay.write(FOLDER/'inventory.json',{'cases':cases,'baseline_version':'0.60.0',
            'source_sha256':replay.public_seal(),'runner_sha256':replay.sha(__file__),
            'worker_sha256':replay.sha(replay.__file__),'private_state_copied':False})
    elif args.mode=='run':
        replay.replay(FOLDER,55)
    else:
        current=replay.public_seal();chosen={}
        for path in sorted(FOLDER.glob('paired-*/rows/*.json')):
            row=replay.read(path)
            if row['source_sha256']==current and row['verifier_sha256']==replay.sha(replay.__file__):
                chosen[row['case']]=(path,row)
        wanted={c['id'] for c in replay.read(FOLDER/'inventory.json')['cases']}
        metrics={}
        for group in ('cold','continuous','negative','transition'):
            metrics[group]={}
            for mode in ('baseline','current'):
                times=[f['performance']['total_ms'] for _,r in chosen.values() if r['group']==group
                       for f in r['outputs'][mode]['frames'][r['measure_from_frame']:]]
                metrics[group][mode]={'times_ms':times,'count':len(times),
                    'p50_ms':replay.percentile(times,.5),'p95_ms':replay.percentile(times,.95)}
        result={'version':'0.61.0','passed':wanted==set(chosen) and all(r['passed'] for _,r in chosen.values()),
            'strict_equal_cases':sum(r['passed'] for _,r in chosen.values()),'missing_cases':sorted(wanted-set(chosen)),
            'source_sha256':current,'replay_receipts':{p.relative_to(ROOT).as_posix():replay.sha(p) for p,_ in chosen.values()},
            'runner_sha256':replay.sha(__file__),'worker_sha256':replay.sha(replay.__file__),
            'metrics':metrics,'excluded_nested_keys':['elapsed_ms'],'private_state_copied':False,
            'game_actions':0,'chat_requests':0,'all_p1_complete':False,
            'limits':['Existing development samples, not independent holdout.',
                      'Three cold cases, one actual animation pair, one main-menu negative and a concatenated transition.',
                      'Small paired timings are descriptive; background application remained running.']}
        replay.write(FOLDER/('summary-'+str(time.time_ns())+'.json'),result)
        assert result['passed'],result['missing_cases']
        replay.write(ROOT/'HELD_REPLAY_0.61_VERIFICATION.json',result)
        print(json.dumps({'passed':result['passed'],'strict_equal_cases':result['strict_equal_cases'],'metrics':metrics}),flush=True)


if __name__=='__main__':main()
