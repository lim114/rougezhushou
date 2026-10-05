"""Strict boundary preservation plus an explicit current-evidence recovery.

The old half-frame failure is retained. No run/page field is excluded from
diffing: the restored half frame records its complete old/new difference,
then checks an independently pinned native/same-frame/mechanism oracle.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys
import time

import cv2
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
HYBRID=ROOT/'scripts/verify_hybrid_059.py'
BOUNDARY=ROOT/'scripts/verify_popup_boundaries_059.py'
SPEC=importlib.util.spec_from_file_location('hybrid_059_recovery',HYBRID)
H=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(H)
BSPEC=importlib.util.spec_from_file_location('boundary_059_recovery',BOUNDARY)
B=importlib.util.module_from_spec(BSPEC);BSPEC.loader.exec_module(B)
FAILED=ROOT/'.cache/research/hybrid-059/epoch2-current/popup-boundaries/summary-1791183642543098100.json'
OLD_ARCHIVE=ROOT/'.cache/research/hybrid-059/epoch2-current/superseded-source-archive-1791184894271631000/receipt.json'
RECOVERED='myrtle_owned:half_client'


def ref(path):
    path=Path(path);return {'path':path.relative_to(ROOT).as_posix(),'sha256':H.sha(path)}


def prepare(epoch):
    B.prepare(epoch)
    folder=epoch/'popup-recovery';folder.mkdir()
    native_top=H.read(ROOT/'HYBRID_0.58_VERIFICATION.json');native=None
    for rel,pin in native_top['replay_receipts'].items():
        path=ROOT/rel;assert H.sha(path)==pin;row=H.read(path)
        if row['case']=='myrtle_owned:native':native=(path,row);break
    assert native is not None
    path,row=native;observation=row['outputs']['current']['frames'][0]['observation']
    run=observation['run'];member=next(m for m in run['operators'] if m['id']==run['selected_operator'])
    assert member['id']=='char_151_myrtle' and member['name']=='桃金娘'
    assert member['fields']=={} and member['skill_ranks']=={}
    assert member['recipient_buffs']['count']==2 and member['char_buffs_complete'] is True
    mechanics=H.read(ROOT/'rouge/data/relic-mechanics.json')['char_buffs']
    expected_mechanisms={key:mechanics[key] for key in member['char_buff_ids']}
    for entry in member['recipient_buffs']['entries']:
        raw=expected_mechanisms[entry['id']]['raw']
        assert raw['id']==entry['id'] and raw['outerName']==entry['name']
        assert raw['desc']==entry['description'] and raw['iconId']==entry['icon']['id']
    oracle=folder/'oracle.json'
    H.write(oracle,{'native_receipt':ref(path),'native_observation':observation,
        'expected_mechanisms':expected_mechanisms,
        'mechanism_file':ref(ROOT/'rouge/data/relic-mechanics.json'),
        'explanation':'Expected facts from sealed complete native reading and pinned original mechanism data; values are never injected into OCR or the application.',
        'source_relationship':'The half frame is a lossless derivative of this same native public source, not a new holdout.'})
    source=H.read(epoch/'popup-boundaries/inventory.json')
    H.write(folder/'inventory.json',{'cases':source['cases'],'source_sha256':H.public_seal(),
        'verifier_sha256':H.sha(__file__),'hybrid_verifier_sha256':H.sha(HYBRID),
        'boundary_verifier_sha256':H.sha(BOUNDARY),'derived_inventory':ref(epoch/'popup-boundaries/inventory.json'),
        'oracle':ref(oracle),'preserved_failure':ref(FAILED),'preserved_epoch2_archive':ref(OLD_ARCHIVE),
        'baseline_package_seal':ref(epoch/'baseline-package-seal.json'),
        'formal_case_count_unchanged':23,'additional_derived_cases':3,
        'strict_preservation_cases':2,'explicit_recovery_cases':1,
        'private_state_read':False,'game_actions':0,'chat_requests':0})
    print({'prepared':str(folder),'additional_derived_cases':3},flush=True)


def restored_oracle(case,before,after,baseline_frame,folder,source):
    """No broad equality exception: record every change, verify new facts."""
    oracle=H.read(ROOT/source['oracle']['path']);native=oracle['native_observation']['run']
    expected=next(m for m in native['operators'] if m['id']==native['selected_operator'])
    checks=[]
    def check(path,value,wanted):
        same=not H.differences(value,wanted,path)
        checks.append({'path':path,'passed':same,'actual':value,'expected':wanted});return same
    def valid(path,value):
        checks.append({'path':path,'passed':bool(value)});return bool(value)
    check('/before/page',before.get('page'),'unknown');check('/before/run',before.get('run'),None)
    check('/after/page',after.get('page'),'run_roster')
    for key in H.FIELDS:
        if key not in ('page','run'):check('/after/'+key,after.get(key),before.get(key))
    run=after.get('run')
    if not valid('/after/run/is_object',isinstance(run,dict)):return checks,None
    check('/after/run/keys',sorted(run),sorted(native))
    for key in ('page','crew_count','selected_operator','resources','config','config_reuse',
                'tactical_tools','counter_performance','limitations'):
        check('/after/run/'+key,run.get(key),native[key])
    members=run.get('operators',[]);check('/after/run/operators/length',len(members),1)
    member=next((m for m in members if m.get('id')==expected['id']),None)
    if not valid('/after/run/operators/current_owner',isinstance(member,dict)):return checks,None
    check('/owner/keys',sorted(member),sorted(expected))
    for key in ('id','name','scope','fields','skill_ranks','missing_fields','char_buff_ids','char_buffs_complete'):
        check('/owner/'+key,member.get(key),expected[key])
    buffs=member.get('recipient_buffs',{})
    for key in ('operator_id','operator_name','ids','count','complete','status','issues','source'):
        check('/owner/recipient_buffs/'+key,buffs.get(key),expected['recipient_buffs'][key])
    entries=buffs.get('entries',[]);check('/owner/recipient_buffs/entries/length',len(entries),2)
    valid('/owner/recipient_buffs/entries/unique_ids',len({e.get('id') for e in entries})==len(entries))
    for entry in entries:
        key=entry.get('id');mechanism=oracle['expected_mechanisms'].get(key)
        if not valid('/buff/'+str(key)+'/pinned_mechanism',mechanism is not None):continue
        raw=mechanism['raw'];prefix='/buff/'+key
        for field,wanted in (('name',raw['outerName']),('description',raw['desc']),
                              ('source','owned_operator_buff_popup'),('mechanism_source',mechanism['source'])):
            check(prefix+'/'+field,entry.get(field),wanted)
        icon=entry.get('icon',{});check(prefix+'/icon/id',icon.get('id'),raw['iconId'])
        score=icon.get('score');valid(prefix+'/icon/score',type(score) in (int,float) and math.isfinite(score) and .94<=score<=1)
        valid(prefix+'/icon/current_box',len(icon.get('box',[]))==4)
        valid(prefix+'/name/current_box',len(entry.get('name_evidence',{}).get('box',[]))==4)
        valid(prefix+'/description/current_evidence',bool(entry.get('description_evidence')))
    relics=run.get('relics',{})
    check('/after/run/relics/keys',sorted(relics),sorted(native['relics']))
    for key in ('ids','count','cards','counters','unbound_counters','source'):
        check('/after/run/relics/'+key,relics.get(key),native['relics'][key])
    icons=relics.get('icons',[]);check('/after/run/relics/icons/length',len(icons),len(native['relics']['icons']))
    for i,icon in enumerate(icons):
        score=icon.get('score');valid('/relic_icon/'+str(i)+'/score',type(score) in (int,float) and math.isfinite(score) and 0<=score<=1)
        if icon.get('confirmed'):
            valid('/relic_icon/'+str(i)+'/identity_from_native',icon.get('id') in native['relics']['ids'])
    # The same low-resolution frame supplies the count, two names and boxes.
    rawtexts=baseline_frame['actual_raw_ocr'];height,width=after['viewport']['analysis_size'][1],after['viewport']['analysis_size'][0]
    from rouge.viewport import prepare_frame,map_evidence
    def mapped(box):
        value={'box':[[float(x)/width,float(y)/height] for x,y in box]}
        map_evidence(value,after['viewport']);return value['box']
    context=member.get('sources',{}).get('owned_popup_context',{})
    names=sorted([r for r in rawtexts if r[1]==expected['name'] and r[2]>=.95],key=lambda r:min(p[1] for p in r[0]))
    check('/same_frame/exact_owner_name_count',len(names),2)
    if len(names)==2:
        check('/owner/context/owner/box',context.get('owner',{}).get('box'),mapped(names[0][0]))
        check('/owner/context/card/box',context.get('card',{}).get('box'),mapped(names[1][0]))
    header=[r for r in rawtexts if r[1]=='此干员已拥有以下2个收藏品增益' and r[2]>=.95]
    check('/same_frame/current_owned_count_header',len(header),1)
    if len(header)==1:check('/owner/context/header/box',context.get('header',{}).get('box'),mapped(header[0][0]))
    weak=[r for r in rawtexts if r[1]=='收藏品' and .9<=r[2]<.95]
    check('/same_frame/weak_footer_unique',len(weak),1)
    if len(weak)!=1:return checks,None
    box,label,confidence=weak[0];recheck=context.get('footer',{}).get(label,{}).get('footer_recheck',{})
    check('/footer/source',recheck.get('source'),'current_owned_popup_footer_rect_recognizer')
    check('/footer/original_confidence',recheck.get('original_confidence'),confidence)
    for key,value in (('padding_pixels',2),('use_det',False),('use_cls',False)):
        check('/footer/'+key,recheck.get(key),value)
    left=max(0,math.floor(min(p[0] for p in box))-2);top=max(0,math.floor(min(p[1] for p in box))-2)
    right=min(width,math.ceil(max(p[0] for p in box))+2);bottom=min(height,math.ceil(max(p[1] for p in box))+2)
    check('/footer/recheck_box',recheck.get('box'),mapped([[left,top],[right,top],[right,bottom],[left,bottom]]))
    check('/footer/original_box',context.get('footer',{}).get(label,{}).get('box'),mapped(box))
    image,rect=H.image_for(case['frames'][0]);prepared,viewport=prepare_frame(image,rect)
    check('/same_frame/viewport',viewport,after['viewport']);crop=prepared[top:bottom,left:right].copy()
    file=folder/'current-footer-rec-crop.png';ok,encoded=cv2.imencode('.png',crop);assert ok
    with file.open('xb') as stream:stream.write(encoded.tobytes())
    assert np.array_equal(cv2.imdecode(np.fromfile(file,np.uint8),1),crop)
    from rapidocr_onnxruntime import RapidOCR
    from rouge.recognition_cache import CachedOCR
    engine=CachedOCR(RapidOCR(intra_op_num_threads=2,inter_op_num_threads=2));kwargs={'use_det':False,'use_cls':False}
    started=time.perf_counter();result,elapsed=engine(crop,**kwargs);wall=(time.perf_counter()-started)*1000
    result=json.loads(json.dumps(result));valid('/footer/independent_rec/single',bool(result and len(result)==1 and len(result[0])==2))
    if result and len(result)==1 and len(result[0])==2:
        check('/footer/independent_rec/text',result[0][0],label)
        valid('/footer/independent_rec/confidence',type(result[0][1]) in (int,float) and math.isfinite(result[0][1]) and .95<=result[0][1]<=1)
        check('/footer/actual_reported_confidence',recheck.get('confidence'),result[0][1])
    probe=folder/'same-frame-rec-probe.json'
    H.write(probe,{'source_frame':case['frames'][0],'crop':ref(file),'crop_shape':list(crop.shape),
        'crop_bounds_ltrb':[left,top,right,bottom],'current_reported_footer_recheck':recheck,
        'same_frame_baseline_raw_footer':weak[0],'kwargs':kwargs,'raw_output':result,'raw_elapsed':elapsed,
        'wall_ms':wall,'recognition_calls':1,'source_sha256':H.public_seal(),
        'no_higher_resolution_input':True,'private_state_read':False,'game_actions':0,'chat_requests':0})
    return checks,ref(probe)


def replay(epoch,budget):
    folder=epoch/'popup-recovery';source=H.read(folder/'inventory.json');start=H.public_seal()
    verifier=H.sha(__file__);hybrid=H.sha(HYBRID);assert source['source_sha256']==start
    assert source['verifier_sha256']==verifier and source['hybrid_verifier_sha256']==hybrid
    for key in ('oracle','preserved_failure','preserved_epoch2_archive','baseline_package_seal','derived_inventory'):
        assert H.sha(ROOT/source[key]['path'])==source[key]['sha256']
    stage=folder/('paired-'+str(time.time_ns()));stage.mkdir();present={}
    for path in folder.glob('paired-*/rows/*.json'):
        value=H.read(path)
        if value['source_sha256']==start and value['verifier_sha256']==verifier:present[value['case']]=value
    started=time.perf_counter();completed=0
    for index,case in enumerate(source['cases']):
        if case['id'] in present:continue
        if completed and time.perf_counter()-started>=budget:break
        slug=case['id'].replace(':','-');casepath=stage/'cases'/(slug+'.json');H.write(casepath,case)
        outputs={};workers={}
        for label in (('baseline','current') if index%2==0 else ('current','baseline')):
            destination=stage/'workers'/(slug+'-'+label+'.json');package=epoch/'baseline-source' if label=='baseline' else ROOT
            process=subprocess.run([sys.executable,str(HYBRID),'worker','--package',str(package),
                '--case',str(casepath),'--output',str(destination)],capture_output=True,text=True,encoding='utf-8')
            if process.returncode:
                H.write(stage/('failure-'+str(time.time_ns())+'.json'),{'case':case['id'],'label':label,
                    'exit':process.returncode,'stdout':process.stdout,'stderr':process.stderr})
                raise RuntimeError('Real recovery worker failed; diagnostic preserved')
            outputs[label]=H.read(destination);workers[label]=ref(destination)
        before=outputs['baseline']['frames'][0]['observation'];after=outputs['current']['frames'][0]['observation']
        differences=H.differences(H.strict(before),H.strict(after),'/frames/0')
        route=outputs['current']['frames'][0]['performance'].get('routing',{})
        route_valid=(after['page']=='run_roster' and route.get('strategy')=='visual_region_ocr'
            and route.get('candidates')==['run_owned_popup'] and route.get('semantic_verified') is True)
        checks=[];probe=None
        if case['id']==RECOVERED:
            checks,probe=restored_oracle(case,before,after,outputs['baseline']['frames'][0],stage,source)
            delta_valid=sorted(d['path'] for d in differences)==['/frames/0/page','/frames/0/run']
            passed=route_valid and delta_valid and bool(checks) and all(c['passed'] for c in checks) and probe is not None
            kind='current_evidence_restoration'
        else:passed=route_valid and not differences;kind='strict_preservation'
        assert start==H.public_seal() and verifier==H.sha(__file__) and hybrid==H.sha(HYBRID)
        value={'case':case['id'],'passed':passed,'validation_kind':kind,'outputs':outputs,
            'strict_semantic_differences':differences,'oracle_checks':checks,'same_frame_probe':probe,
            'route_verified':route_valid,'source_sha256':start,'verifier_sha256':verifier,
            'hybrid_verifier_sha256':hybrid,'case_receipt':ref(casepath),'worker_receipts':workers,
            'all_fact_confidence_geometry_leaves_compared':True,'excluded_keys':['elapsed_ms'],
            'private_state_read':False,'game_actions':0,'chat_requests':0}
        H.write(stage/'rows'/(slug+'.json'),value);completed+=1
        print({'case':case['id'],'passed':passed,'kind':kind,'full_diff_count':len(differences),
            'failed_oracle':[c for c in checks if not c['passed']],'route':route},flush=True)
    H.write(stage/'segment.json',{'completed':completed,'source_sha256':start,'source_stable':start==H.public_seal(),
        'verifier_sha256':verifier,'hybrid_verifier_sha256':hybrid,'seconds':time.perf_counter()-started})


def summary(epoch):
    folder=epoch/'popup-recovery';source=H.read(folder/'inventory.json');current=H.public_seal();verifier=H.sha(__file__);rows={}
    for path in sorted(folder.glob('paired-*/rows/*.json')):
        value=H.read(path)
        if value['source_sha256']==current and value['verifier_sha256']==verifier:rows[value['case']]=(path,value)
    expected={c['id'] for c in source['cases']};assert len(expected)==3
    strict=sum(v['passed'] and v['validation_kind']=='strict_preservation' for _,v in rows.values())
    restored=sum(v['passed'] and v['validation_kind']=='current_evidence_restoration' for _,v in rows.values())
    probes=[v['same_frame_probe'] for _,v in rows.values() if v['same_frame_probe'] is not None]
    receipt={'passed':set(rows)==expected and strict==2 and restored==1,
        'source_sha256':current,'verifier_sha256':verifier,'hybrid_verifier_sha256':H.sha(HYBRID),
        'strict_equal_cases':strict,'restored_cases':restored,'formal_case_count_unchanged':23,
        'expected_cases':sorted(expected),'missing_cases':sorted(expected-set(rows)),
        'failed_cases':[name for name,(_,value) in rows.items() if not value['passed']],
        'replay_receipts':{p.relative_to(ROOT).as_posix():H.sha(p) for p,_ in rows.values()},
        'inventory':ref(folder/'inventory.json'),'oracle':source['oracle'],
        'same_frame_probe':probes[0] if len(probes)==1 else None,
        'baseline_package_seal':source['baseline_package_seal'],'preserved_failure':source['preserved_failure'],
        'preserved_epoch2_archive':source['preserved_epoch2_archive'],
        'all_fact_confidence_geometry_leaves_compared':True,'excluded_keys':['elapsed_ms'],
        'limits':['Three derived inputs, not independent captures.',
            'Myrtle half changes unknown to current run_roster; its complete diff and field oracle are retained.',
            'No run/page or confidence/box keys are excluded; this recovery is separate from the formal 23 strict cases.'],
        'private_state_read':False,'game_actions':0,'chat_requests':0}
    destination=folder/('summary-'+str(time.time_ns())+'.json');H.write(destination,receipt)
    print({'receipt':str(destination),'passed':receipt['passed'],'strict_equal_cases':strict,'restored_cases':restored,
        'missing':receipt['missing_cases'],'failed':receipt['failed_cases']},flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=('prepare','replay','summary'))
    parser.add_argument('--epoch',required=True);parser.add_argument('--budget-seconds',type=float,default=45)
    args=parser.parse_args();epoch=Path(args.epoch).resolve()
    if args.mode=='prepare':prepare(epoch)
    elif args.mode=='replay':replay(epoch,args.budget_seconds)
    else:summary(epoch)
