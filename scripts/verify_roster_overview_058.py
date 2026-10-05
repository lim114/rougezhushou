"""Additional real-OCR unselected roster proof, retaining the 22-case verifier."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
HYBRID=ROOT/'scripts/verify_hybrid_058.py'
SPEC=importlib.util.spec_from_file_location('hybrid_058',HYBRID)
H=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(H)


def main():
    epoch=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT/'.cache/research/hybrid-058/epoch-current'
    sample=next(s for s in H.read(H.OLD_INVENTORY)['samples'] if s['id']=='run-roster')
    case={'id':'run-roster:native','frames':[H.frame(sample)],'group':'cold',
          'provenance':'preexisting unselected roster development sample; also visual asset training source'}
    folder=epoch/('roster-overview-'+str(time.time_ns()));folder.mkdir()
    start=H.public_seal();verifier=H.sha(__file__);hybrid=H.sha(HYBRID)
    casepath=folder/'case.json';H.write(casepath,case);outputs={}
    for label,package in (('baseline',epoch/'baseline-source'),('current',ROOT)):
        destination=folder/(label+'.json')
        p=subprocess.run([sys.executable,str(HYBRID),'worker','--package',str(package),'--case',str(casepath),
                          '--output',str(destination)],capture_output=True,text=True,encoding='utf-8')
        if p.returncode:
            H.write(folder/'failure.json',{'label':label,'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
            raise RuntimeError('Additional roster worker failed; full diagnostic preserved')
        outputs[label]=H.read(destination)
    before=outputs['baseline']['frames'][0]['observation'];after=outputs['current']['frames'][0]['observation']
    differences=H.differences(H.strict(before),H.strict(after))
    route=outputs['current']['frames'][0]['performance'].get('routing',{})
    matched=(after['page']=='run_roster' and route.get('strategy')=='visual_region_ocr'
             and route.get('candidates')==['run_roster'] and route.get('semantic_verified') is True)
    stable=start==H.public_seal() and verifier==H.sha(__file__) and hybrid==H.sha(HYBRID)
    receipt={'passed':not differences and matched and stable,'case':case,'outputs':outputs,
        'strict_semantic_differences':differences,'route_verified':matched,'source_stable':stable,
        'source_sha256':start,'verifier_sha256':verifier,'hybrid_verifier_sha256':hybrid,
        'baseline_package_seal_sha256':H.sha(epoch/'baseline-package-seal.json'),
        'all_fact_confidence_geometry_leaves_compared':True,'excluded_keys':['elapsed_ms'],
        'private_state_read':False,'game_actions':0,'chat_requests':0}
    receipt['case_receipt']={'path':casepath.relative_to(ROOT).as_posix(),'sha256':H.sha(casepath)}
    receipt['worker_receipts']={label:{'path':(folder/(label+'.json')).relative_to(ROOT).as_posix(),
        'sha256':H.sha(folder/(label+'.json'))} for label in outputs}
    H.write(folder/'receipt.json',receipt)
    entry={**receipt,'immutable_receipt':{'path':(folder/'receipt.json').relative_to(ROOT).as_posix(),
        'sha256':H.sha(folder/'receipt.json')}}
    H.write(ROOT/'ROSTER_0.58_VERIFICATION.json',entry)
    print(json.dumps({'receipt':str(folder/'receipt.json'),'passed':receipt['passed'],
        'strict_differences':differences,'route':route,
        'times_ms':{k:v['frames'][0]['performance']['total_ms'] for k,v in outputs.items()}},ensure_ascii=False),flush=True)


if __name__=='__main__':main()
