"""Root-only Saved readback of 19 actual cases; imports no project runtime."""
import argparse,hashlib,importlib.util,json,math,os,re,sys,threading,traceback
from pathlib import Path
BASE=Path('/workspace/.continuation')
FIXTURE=BASE/'root-section115-public19-inputs-v1.json'
FIXTURE_SHA='e3ca9b48a530489c7e425e54f5fb1577df99f18c647328c308354fbe0cdd38a8'
EXTERNAL=BASE/'section115-accuracy-public-source-v1'
EXTERNAL_SHA='afd29588237b1f087502f1dcec6def2f7454f56b13411ba6deb21daa975da7ea'
CANDIDATES_SHA='ff65b7a7e9c0603bd10794df94a51fa32a75e8773b1965ed46675f7c11885556'
HELPER_SHA='f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a'
PROBE_SHA='b4e574e54d7798d06707ad7f80a2efe268209a5b8e22645f9d976ac86dd7e1d3'
PHASES=('calculate_damage','format_estimate','format_report','format_report_technical')
GROUPS={'damage':('伤害','伤害'),'healing':('潜在治疗','治疗'),'regeneration':('独立生命回复','生命'),
        'buildup':('潜在损伤积累','损伤积累'),'other':('其他输出字段','')}
LABELS={'physical':'物理伤害','magic':'法术伤害','true':'真实伤害','elemental':'元素伤害',
        'weakness':'择优伤害（物理/法术）','damage_reference':'伤害（原结果未单列类型）',
        'healing':'潜在治疗','regeneration':'独立生命回复','buildup':'潜在损伤积累'}
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def pin(path):return {'path':str(path),'bytes':path.stat().st_size,'sha256':sha(path)}
def number_equal(actual,expected):
    assert type(actual) in (int,float) and math.isfinite(actual) and actual==expected

def check_blocks(result,helper):
    """Independently check raw source fields; total is never recomputed."""
    blocks=[block for block in result['report']['sections'] if block['id'].startswith('output_breakdown_')]
    components=result.get('components');legacy='components' not in result
    if legacy:
        components=[]
        if all(key in result for key in ('hits','per_hit','total_damage')):
            components.append({'name':'既有技能伤害字段','damage_type':result.get('damage_type','damage_reference'),
                'hits':result['hits'],'per_hit':result['per_hit'],'total':result['total_damage']})
        if all(key in result for key in ('hits','per_heal','total_healing')):
            components.append({'name':'既有技能治疗字段','damage_type':'healing',
                'hits':result['hits'],'per_hit':result['per_heal'],'total':result['total_healing']})
    expected={key:[] for key in GROUPS}
    for index,component in enumerate(components or []):
        dtype=component.get('damage_type');group=dtype if dtype in ('healing','regeneration','buildup') else 'damage' if dtype in LABELS else 'other'
        title,unit=GROUPS[group];name=component.get('name') or '未命名分项';prefix='component_'+str(index)+'_'
        def row(key,label,value,u=''):expected[group].append({'key':prefix+key,'label':name+' · '+label,'value':value,'unit':u})
        row('type','类型',LABELS.get(dtype,dtype if dtype is not None else None))
        row('count','期望次数/份额' if '期望' in name else '模型次数/份额',component.get('hits'))
        amounts=component.get('event_amounts');finite=isinstance(amounts,list) and bool(amounts) and all(
            type(v) in (int,float) and math.isfinite(v) for v in amounts)
        variable=finite and min(amounts)!=max(amounts)
        row('per_hit','单次量字段（事件量可变）' if variable else '单次量字段',component.get('per_hit'),unit)
        if variable:
            for key,label,value in [('event_mean','已给逐事件量均值',sum(amounts)/len(amounts)),
                    ('event_min','已给逐事件量下限',min(amounts)),('event_max','已给逐事件量上限',max(amounts))]:row(key,label,value,unit)
        pending='actual_total' in component and component['actual_total'] is None
        row('total','条件总量参考' if pending else '分项模型总量',component.get('total'),unit)
        if 'actual_total' in component:row('actual_total','实际总量字段',component['actual_total'],unit)
    keys=[key for key in GROUPS if expected[key]]
    assert [block['id'] for block in blocks]==['output_breakdown_'+key for key in keys]
    for key,block in zip(keys,blocks):
        assert block['title']=='当前情景输出分项 · '+GROUPS[key][0]
        helper.assert_native_equal(block['metrics'],expected[key],'complete added metric fields/order/types')
        notes='\n'.join(block['notes'])
        for phrase in ('不是完整施放或本轮周期','不证明实际攻击次数','不用单次量乘次数重算','不再相加'):assert phrase in notes
        if legacy:assert '不生成事件、额外目标次数或类型' in notes
        if key=='damage' and result.get('total_damage') is None:assert '整体伤害仍未知' in notes
        if key=='healing':
            assert '潜在治疗不等于有效受疗' in notes
            if result.get('total_healing') is None:assert '整体治疗仍未知' in notes
        if key=='regeneration':assert '独立生命回复不并入伤害或直接治疗' in notes
        if key=='buildup':assert '损伤积累不是敌人生命伤害' in notes
    return blocks

def load_domain(directory,phase,guard,fixture,helper):
    assert Path(str(directory)+'.exit-code').read_bytes()==b'0\n'
    path=directory/'observations.json';receipt=json.loads(path.read_text())
    assert receipt['kind']=='ROOT_ACTUAL_PUBLIC_API_THREE_FORMATTER_OBSERVATION' and receipt['phase']==phase
    assert receipt['observation_only'] and receipt['product_pass'] is False and receipt['observation_complete']
    assert receipt['consumer_error_count']==0 and receipt['source_and_CORE_unchanged']
    assert receipt['actual_completed_cases']==19 and receipt['actual_public_calls']==76 and receipt['actual_native_records']==95
    rp=Path(receipt['runner']['path']);assert pin(rp)==receipt['runner'] and sha(rp)==PROBE_SHA
    assert receipt['fixture']['sha256']==FIXTURE_SHA and receipt['fixture']['bytes']==FIXTURE.stat().st_size
    gp=Path(receipt['guard']['path']);assert pin(gp)==receipt['guard'];own_guard=json.loads(gp.read_text())
    assert own_guard['section']==115 and own_guard['source_sha256']==receipt['source_before']==receipt['source_after']
    assert own_guard['source_additional_sha256']==receipt['CORE_before']==receipt['CORE_after']==guard['source_additional_sha256']
    if phase=='candidate':assert own_guard==guard
    index=[json.loads(line) for line in (directory/'native/index.jsonl').read_text().splitlines()]
    assert index==receipt['records'] and len(index)==95
    expected_order=[(kind,case['id'],p) for case in fixture['cases'] for kind,p in
        [('actual-public-consumer',p) for p in PHASES]+[('whole-case-caller','caller')]]
    assert [(m['kind'],m['case'],m['phase']) for m in index]==expected_order
    decoded={};consumer_calls=iter(receipt['calls'])
    for meta in index:
        value=helper.read_record(directory/'native',meta);decoded[meta['case'],meta['phase']]=value
        helper.assert_native_equal(value['after'],value['before'],'saved whole caller purity')
        if meta['phase']!='caller':
            call=next(consumer_calls)
            assert call['case']==meta['case'] and call['phase']==meta['phase'] and call['native']==meta
            assert call['caller_unchanged'] and call['error'] is None and value['error'] is None
    assert next(consumer_calls,None) is None
    for case in fixture['cases']:
        identity=case['id'];calculation=decoded[identity,'calculate_damage']
        helper.assert_native_equal(calculation['before'],(case['scenario'],),'complete actual fixture caller')
        helper.assert_native_equal(decoded[identity,'caller']['before'],case['scenario'],'whole-case actual fixture')
        result=calculation['result'];texts={}
        for p in PHASES[1:]:
            saved=decoded[identity,p];helper.assert_native_equal(saved['before'],(result,),'whole formatter input equals actual calculation')
            assert isinstance(saved['result'],str) and saved['result'];texts[p]=saved['result']
        assert texts['format_estimate']==texts['format_report']
        assert '【技术资料】' in texts['format_report_technical']
    return receipt,decoded,pin(path)

def main():
    parser=argparse.ArgumentParser()
    for key in ('root','guard','original','candidate','out'):parser.add_argument('--'+key,required=True)
    args=parser.parse_args();root=Path(args.root).resolve();out=Path(args.out).resolve();guard_path=Path(args.guard).resolve()
    assert not out.exists() and root not in out.parents and BASE in out.parents
    helper_path=Path(__file__).resolve().parent/'native_evidence.py';assert sha(helper_path)==HELPER_SHA
    sys.dont_write_bytecode=True;spec=importlib.util.spec_from_file_location('root_saved115',helper_path)
    helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    guard_raw=guard_path.read_bytes();guard=json.loads(guard_raw);expected=guard['source_sha256'];extra=guard['source_additional_sha256']
    assert guard['section']==115 and helper.source_map(root)==expected and set(extra)=={'CORE_0.70_VERIFICATION.json'}
    assert all(sha(root/name)==wanted for name,wanted in extra.items())
    assert sha(FIXTURE)==FIXTURE_SHA;fixture=json.loads(FIXTURE.read_text());assert len(fixture['cases'])==19
    assert sha(EXTERNAL/'SOURCE_MANIFEST.json')==EXTERNAL_SHA and sha(EXTERNAL/'accuracy-candidates.json')==CANDIDATES_SHA
    manifest=json.loads((EXTERNAL/'SOURCE_MANIFEST.json').read_text());assert len(manifest['files'])==manifest['count']==66
    for leaf in manifest['files']:
        name=leaf['path'];assert Path(name).name==name;path=EXTERNAL/name
        assert not path.is_symlink() and path.stat().st_size==leaf['bytes'] and sha(path)==leaf['sha256']
    external=json.loads((EXTERNAL/'accuracy-candidates.json').read_text());assert external['currently_supported_core_candidates']==4
    assert external['cases'][4]['apply_ready'] is False and fixture['external_conditional_5th_excluded'] is True
    out.mkdir();done=threading.Event()
    def timeout():
        if not done.wait(120):(out/'timeout.json').write_text('{"passed":false,"deadline_seconds":120}\n');os._exit(124)
    threading.Thread(target=timeout,daemon=True).start()
    proof={'kind':'ROOT_ACTUAL115_SAVED_API_AND_EXTERNAL_ACCURACY','passed':False,'workflow_complete':False,
        'source_drift':[],'project_runtime_executed':False,'guard':pin(guard_path),'runner':pin(Path(__file__).resolve()),
        'fixture':pin(FIXTURE),'external_manifest':pin(EXTERNAL/'SOURCE_MANIFEST.json'),'cases':[],'external_examples':[],
        'native_windows_game_chat_verified':False,'private_state_access':False,
        'scope':'Saved native decoding only. Actual calculation/three formatters are verified from original and candidate receipts, not executed again.',
        'external_scope':'Exact agreement at stated nominal inputs. Wiki approximate encounter/rating and TapTap S1/S2 typo limitations retained; no client or complete-rotation proof.',
        'excluded_fifth':external['cases'][4]}
    try:
        old,od,op=load_domain(Path(args.original).resolve(),'original',guard,fixture,helper)
        new,nd,np=load_domain(Path(args.candidate).resolve(),'candidate',guard,fixture,helper)
        proof['original_receipt']=op;proof['candidate_receipt']=np
        changed={k for k in set(old['source_before'])|set(expected) if old['source_before'].get(k)!=expected.get(k)}
        assert changed=={'rouge/reporting.py','tests/test_current_output_breakdown_115.py','scripts/verify_cloud.py'}
        assert old['source_before'].get('tests/test_current_output_breakdown_115.py') is None
        for case in fixture['cases']:
            identity=case['id'];o=od[identity,'calculate_damage']['result'];n=nd[identity,'calculate_damage']['result']
            assert not any(s['id'].startswith('output_breakdown_') for s in o['report']['sections'])
            blocks=check_blocks(n,helper);stripped=helper.freeze(n)
            stripped['report']['sections'][:]=[s for s in stripped['report']['sections'] if not s['id'].startswith('output_breakdown_')]
            helper.assert_native_equal(stripped,o,'whole original result except explicit new report sections')
            for p in PHASES:
                before=od[identity,p]['before'];after=nd[identity,p]['before']
                if p=='calculate_damage':helper.assert_native_equal(after,before,'original/candidate complete caller')
                else:
                    for text in (od[identity,p]['result'],nd[identity,p]['result']):assert isinstance(text,str) and text
                    for block in blocks:assert '【'+block['title']+'】' in nd[identity,p]['result']
            proof['cases'].append({'id':identity,'whole_result_except_new_sections_equal':True,
                'added_section_ids':[s['id'] for s in blocks],'three_complete_texts_retained':True})
        catalog=json.loads((root/'rouge/data/catalog.json').read_text());amiya=catalog['operators']['char_002_amiya']
        assert amiya['skills'][0]['levels'][6]['values']=={'attack_speed':60.0}
        assert all(frame['interval']==1.6 and frame['attack_speed']==100.0 for frame in amiya['phases'][1]['frames'])
        assert '"wgRevisionId":759599' in (EXTERNAL/'wiki-mechanics.html').read_text()
        ami_html=(EXTERNAL/'wiki-amiya.html').read_text();assert '"wgRevisionId":706848' in ami_html
        rank7=ami_html.split('title="Level 7"',1)[1].split('</tr>',1)[0];assert '+60' in rank7
        assert re.search(r'Attack Interval\s+1\.6 seconds',(EXTERNAL/'wiki-amiya.txt').read_text())
        for source_key in ('wiki_damage_tips','taptap_guide'):
            source=external['sources'][source_key];text=(EXTERNAL/Path(source['text']['path']).name).read_text()
            assert all(quote in text for quote in source.get('quotes',[source.get('quote')]))
        for example in external['cases'][:4]:
            identity='external-'+example['id'];case=next(c for c in fixture['cases'] if c['id']==identity)
            helper.assert_native_equal(case['scenario'],example['candidate_scenario'],'exact original external input mapping')
            results=[od[identity,'calculate_damage']['result'],nd[identity,'calculate_damage']['result']]
            selected=[]
            for result in results:
                caller=case['scenario'];assert caller['relic_ids']==[] and caller['effects']==[] and result['applied_effects']==[]
                assert caller['enemy_defense']==800 and caller['enemy_resistance']==50
                training=result['estimate']['training'];assert training['module_id'] is None and training['module_level']==0
                assert training['elite']==1 and training['level']==1 and training['trust']==0 and training['potential']==1
                for value in (result['attack'],result['estimate']['base_stats']['attack'],result['estimate']['skill']['skill_attack']):number_equal(value,caller['base_attack'])
                if 'per_hit' in example['external_expected']:
                    where=example['candidate_result_selector']['where'];components=[c for c in result['components'] if all(c.get(k)==v for k,v in where.items())]
                    assert len(components)==1;actual={'per_hit':components[0]['per_hit']}
                else:
                    number_equal(result['base_attack_speed'],100);actual={k:result[k] for k in example['external_expected']}
                for key,wanted in example['external_expected'].items():number_equal(actual[key],wanted)
                selected.append(actual)
            source=external['sources'][example['source']]
            proof['external_examples'].append({'id':identity,'expected_from_source':example['external_expected'],
                'original_actual':selected[0],'candidate_actual':selected[1],'input':example['candidate_scenario'],
                'source':source,'qualification':example['source_qualification'],'verification_scope':example['verification_scope'],
                'exact_nominal_value_agreement':True})
        assert len(proof['cases'])==19 and len(proof['external_examples'])==4
        proof.update(passed=True,workflow_complete=True,native_records_decoded=190,actual_calls_verified=152,
            original_cases_verified=19,candidate_cases_verified=19,external_source_leaves_verified=66)
    except BaseException as error:proof['failure']={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
    finally:
        after=helper.source_map(root);proof['source_after']=after
        proof['source_drift']=[k for k in set(expected)|set(after) if expected.get(k)!=after.get(k)]
        if proof['source_drift'] or guard_path.read_bytes()!=guard_raw or any(sha(root/k)!=v for k,v in extra.items()):proof.update(passed=False,workflow_complete=False)
        with (out/'receipt.json').open('x',encoding='utf-8') as stream:
            stream.write(json.dumps(proof,ensure_ascii=False,allow_nan=False,indent=2)+'\n');stream.flush();os.fsync(stream.fileno())
        done.set()
    print(json.dumps({'passed':proof['passed'],'cases':len(proof['cases']),'external':len(proof['external_examples'])}))
    return 0 if proof['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
