"""732 strict outputs; bounded S1 event/unknown-field transformations only."""
import copy,hashlib,json,subprocess,sys,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def canonical(row):return json.dumps(row,sort_keys=True,ensure_ascii=False,separators=(',',':'))
def snapshot():
    files=[*(ROOT/'rouge').rglob('*.py'),*(ROOT/'rouge/data').rglob('*.json'),
        *[p for folder in ('page-features','visual-anchors')
          for p in (ROOT/'rouge/data'/folder).iterdir() if p.is_file()],
        Path(__file__),ROOT/'scripts/verify_calculation_replay_056.py',ROOT/'NUMERIC_REPLAY_0.69_VERIFICATION.json']
    return {p.relative_to(ROOT).as_posix():sha(p) for p in sorted(set(files))}


def transform(old,new):
    expected=copy.deepcopy(old);a=expected['result'];b=new['result']
    # All base, relic, total/per-hit, neural and other damage values remain
    # strict. Only the sourced event placement/count type and unproved timing
    # fields change. No whole-result exemption.
    a['components'][0]['hits']=2
    a['components'][0]['times_seconds']=[.5,.9]
    skill=a['estimate']['skill']
    skill['hit_counts']['暗夜回声']=2
    skill['initial_seconds']=0.0
    for key in ('duration_seconds','recharge_seconds','cycle_seconds','phase_damage','phase_healing',
                'cycle_damage','cycle_healing','cycle_dps','cycle_hps'):
        skill[key]=None
    a['estimate']['complete']=False
    a['estimate']['notes']=b['estimate']['notes']
    assert any('解除阻回尚未闭合' in n for n in a['estimate']['notes'])
    assert not any('周期神经损伤连续结算技能与充能期' in n for n in a['estimate']['notes'])
    stream=b['timing']['streams'];assert len(stream)==1
    stream=stream[0]
    assert stream['start_frames']==[0] and stream['release_frames']==stream['impact_frames']==[15,27]
    assert stream['times_seconds']==stream['emitted_times_seconds']==[.5,.9]
    assert stream['windup_frames']==15 and stream['recovery_frames'] is None
    assert stream['interval_frames']==48 and stream['exact_binding'] is False
    ref=stream['multi_melee_reference']
    assert ref['animation_scale']==1.0 and ref['raw_interval_seconds']==1.6 and ref['relative_wait_frames']==12
    assert not any(ref[k] for k in ('first_damage_phase_verified','cast_end_verified',
        'sp_unblock_phase_verified','normal_resume_verified','current_hotfix_equivalence_proven'))
    a['timing']['streams']=b['timing']['streams']
    a['timing']['notes']=b['timing']['notes']
    assert any('float32等待取最近偶数帧' in n for n in a['timing']['notes'])
    if old['scenario']['timing_mode']=='frames':
        a['timing']['recharge_streams']=[]
        a['timing']['cycle_seconds']=None
        a['timing']['unplaced_components']=['潜在神经损伤积累（不是生命伤害）']
    sections=a['report']['sections'];current=b['report']['sections']
    timing=next(s for s in sections if s['id']=='timing')
    timing['metrics'][0]['value']=0.0
    for row in timing['metrics'][1:]:
        row['value']=None;row['reason']='实际结束、阻回与普攻恢复的观察相位尚未确认'
    damage=next(s for s in sections if s['id']=='damage')
    damage['metrics']=[m for m in damage['metrics'] if m['key']!='active_dps']
    for row in damage['metrics']:
        if row['key']=='cycle_dps':row['value']=None
    if old['scenario']['timing_mode']=='frames':
        index=next(i for i,s in enumerate(sections) if s['id']=='execution')
        execution=next(s for s in current if s['id']=='execution')
        assert {m['key']:m['value'] for m in execution['metrics']}=={
            'fps':30,'interval':1.6,'interval_frames':48,'windup':15,
            'recovery':None,'first_release':.5,'first_impact':.5}
        sections[index]=execution
    block=next(s for s in current if s['id']=='multi_melee')
    assert {m['key']:m['value'] for m in block['metrics']}=={
        'raw_interval':1.6,'animation_scale':1.0,'relative_wait':12,'relative_wait_seconds':.4}
    assert len(block['notes'])==4 and '局外参考' in block['notes'][0]
    sections.insert(1,block)
    return expected


def main():
    old=read(ROOT/'NUMERIC_REPLAY_0.69_VERIFICATION.json')
    assert old['passed'] and old['cases']==732
    path=ROOT/old['current_output'];assert sha(path)==old['current_output_sha256']
    rows=read(path);assert len(rows)==732
    directory=ROOT/'.cache/numeric-replay-070'/str(time.time_ns());directory.mkdir(parents=True)
    inputs=directory/'inputs.json';inputs.write_text(json.dumps([r['scenario'] for r in rows]),encoding='utf-8')
    before=snapshot();after=directory/'after.json';worker=directory/'worker.json'
    with (directory/'worker.log').open('x',encoding='utf-8') as log:
        subprocess.run([sys.executable,str(ROOT/'scripts/verify_calculation_replay_056.py'),'_worker',
            '--package',str(ROOT),'--inputs',str(inputs),'--output',str(after),'--receipt',str(worker)],
            cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=60)
    current=read(after);expected=copy.deepcopy(rows);allow=[]
    for i,(a,b) in enumerate(zip(rows,current,strict=True)):
        if a['scenario'].get('operator')=='char_1042_phatm2' and a['scenario'].get('skill')==1:
            expected[i]=transform(a,b)
            allow.append({'case_index':i,'scope':'two_event_resource_reference_and_unverified_timing_only',
                'single_cast_and_window_damage_must_remain_exact':True,'reference_release_frames':[15,27],
                'native_lifecycle_fields_expected':None,'initial_sp_already_ready_seconds':0})
    differences=[i for i,(a,b) in enumerate(zip(rows,current)) if canonical(a)!=canonical(b)]
    unexpected=[i for i,(a,b) in enumerate(zip(expected,current)) if canonical(a)!=canonical(b)]
    final=snapshot();drift=[n for n in sorted(set(before)|set(final)) if before.get(n)!=final.get(n)]
    details={'cases_before':len(rows),'cases_after':len(current),'changed_case_indices':differences,
        'unexpected_case_indices':unexpected,'allowances':allow,'source_drift':drift}
    (directory/'comparison.json').write_text(json.dumps(details,ensure_ascii=False,indent=2),encoding='utf-8')
    proof=read(worker)
    assert proof['passed'] and proof['source_stable_during_calculation']
    assert len(current)==732 and len(allow)==8 and not unexpected and not drift,details
    assert differences==[a['case_index'] for a in allow]
    receipt={'version':'0.70.0','passed':True,'verified_at':time.time(),'cases':732,
        'exact_structured_unchanged':724,'single_cast_and_window_damage_unchanged':732,
        'expected_timing_cases':8,'unexpected_changes':[],'allowances':allow,
        'baseline_output':path.relative_to(ROOT).as_posix(),'baseline_sha256':sha(path),'baseline_version':'0.69.0',
        'current_output':after.relative_to(ROOT).as_posix(),'current_output_sha256':sha(after),
        'worker_receipt':worker.relative_to(ROOT).as_posix(),'worker_receipt_sha256':sha(worker),
        'source_sha256':proof['source_sha256'],'source_stable':True,
        'full_formal_source_sha256':before,'full_formal_source_sha256_after':final,
        'source_drift':drift,'runner_sealed':True,'private_state_used':False,'game_actions':0,'chat_requests':0}
    with (ROOT/'NUMERIC_REPLAY_0.70_VERIFICATION.json').open('x',encoding='utf-8') as stream:
        json.dump(receipt,stream,ensure_ascii=False,indent=2)
    print(json.dumps({'passed':True,'exact_structured_unchanged':724,'expected_timing_cases':8,'source_drift':drift}))


if __name__=='__main__':main()
