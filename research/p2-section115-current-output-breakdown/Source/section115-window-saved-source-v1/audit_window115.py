"""Root-only complete Saved readback; no project API/formatter/Qt import."""
import argparse,hashlib,json,math,os,struct,sys,threading,time,traceback
from pathlib import Path
sys.dont_write_bytecode=True
import native_evidence as native
HELPER_SHA='f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a'
WINDOW_SHA='3e62fdb3811c44a746b85872b493b53f5c373933fa9d09c327a6370082034304'
CLOCK_KEYS=('initial_seconds','recharge_seconds','cycle_seconds','duration_seconds','sp_recovery_per_second','mode')
OPERATORS=(('char_002_amiya',1,1,7),('char_1037_amiya3',2,2,10))
def sha(raw):return hashlib.sha256(raw).hexdigest()
def pin(path):
    assert path.is_file() and not path.is_symlink();raw=path.read_bytes()
    return {'path':str(path),'bytes':len(raw),'sha256':sha(raw)}
def same(left,right,label):return native.assert_native_equal(left,right,label)
def sp_fields(result):
    return {'skill':{key:result['estimate']['skill'][key] for key in CLOCK_KEYS},
        'sp_events':{key:value for key,value in result['estimate'].items() if key=='sp_events'},
        'timing_report':next(s for s in result['report']['sections'] if s['id']=='timing')}
GROUPS={'damage':('伤害','伤害'),'healing':('潜在治疗','治疗'),'regeneration':('独立生命回复','生命'),
        'buildup':('潜在损伤积累','损伤积累'),'other':('其他输出字段','')}

LABELS={'physical':'物理伤害','magic':'法术伤害','true':'真实伤害','elemental':'元素伤害',
        'weakness':'择优伤害（物理/法术）','damage_reference':'伤害（原结果未单列类型）',
        'healing':'潜在治疗','regeneration':'独立生命回复','buildup':'潜在损伤积累'}

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

def main():
    parser=argparse.ArgumentParser()
    for key in ('root','guard','window','window-exit','runner','out'):parser.add_argument('--'+key,required=True)
    args=parser.parse_args();root=Path(args.root).resolve();out=Path(args.out).resolve();folder=Path(args.window).resolve()
    guard_path=Path(args.guard).resolve();runner=Path(args.runner).resolve();exit_path=Path(args.window_exit).resolve()
    assert not out.exists() and root not in out.parents and out!=folder and root!=out
    assert pin(Path(__file__).with_name('native_evidence.py'))['sha256']==HELPER_SHA
    assert pin(runner)['sha256']==WINDOW_SHA and exit_path.read_bytes()==b'0\n'
    guard_raw=guard_path.read_bytes();guard=json.loads(guard_raw);expected=guard['source_sha256'];extra=guard['source_additional_sha256']
    assert guard['section']==115 and native.source_map(root)==expected and set(extra)=={'CORE_0.70_VERIFICATION.json'}
    assert {name:sha((root/name).read_bytes()) for name in extra}==extra
    input_path=folder/'receipt.json';receipt_raw=input_path.read_bytes();window=json.loads(receipt_raw)
    assert window['kind']=='ROOT_ACTUAL_115_REAL_MAINWINDOW' and window['phase']=='candidate'
    assert window['passed'] is True and window['workflow_complete'] is True and not window.get('failure')
    assert window['Qt_errors']==[] and window['source_drift']==[]
    assert window['runner_sha256']==WINDOW_SHA and window['native_helper_sha256']==HELPER_SHA
    assert window['source_guard_sha256']==sha(guard_raw) and window['source_count']==len(expected)
    assert window['source_before']==window['source_after']==expected
    assert window['source_additional_before']==window['source_additional_after']==extra
    assert window['actual_windows']==1 and len(window['rows'])==4 and len(window['pairs'])==2 and len(window['pngs'])==2
    assert window['private_state_access'] is False and window['native_windows_verified'] is False
    assert window['game_chat_sampling_executed'] is False and window['deadline_seconds']==450
    assert 0<=window['elapsed_seconds']<450
    out.mkdir();(out/'native-verified').mkdir();started=time.perf_counter();done=threading.Event()
    def timeout():
        if not done.wait(120):(out/'timeout.json').write_text('{"passed":false,"deadline_seconds":120}\n');os._exit(124)
    threading.Thread(target=timeout,daemon=True).start()
    proof={'kind':'ROOT_ACTUAL115_FULL_SPECIALIZED_WINDOW_SAVED_AUDIT','passed':False,'workflow_complete':False,
        'workflow_checks_passed':False,'source_drift':[],'guard':pin(guard_path),'window_receipt':pin(input_path),
        'window_runner':pin(runner),'window_exit':pin(exit_path),'auditor':pin(Path(__file__).resolve()),
        'native_helper_sha256':HELPER_SHA,'source_before':expected,'source_additional_before':extra,
        'no_project_API_formatter_Qt_Wine_reexecution':True,'private_state_access':False,
        'native_windows_verified':False,'PNG_pixels_viewed_by_this_auditor':False,
        'formatter_scope':'Whole three-formatter group purity; not individually isolated-call purity.',
        'technical_checkbox_render_text_independently_saved':False,
        'technical_checkbox_render_scope':'Original bound runner asserted full technical display; Saved step independently proves result/state purity, not an unsaved intermediate displayed string.',
        'scope':'Complete current four-state/three-text native ledger; independent derived SP pairs; no old GUI Gold, game formula, or native Windows claim.',
        'full_native_records_retained':[],'snapshots':[],'pairs':[],'PNGs':[],'numeric_exceptions_preserved':[]}
    try:
        metadata=window['records'];names=[ref['path'] for ref in metadata]
        assert names==[f'{i:06d}.pickle.gz' for i in range(1,len(names)+1)] and len(names)==len(set(names))
        assert not (folder/'records').is_symlink() and {p.name for p in (folder/'records').iterdir()}==set(names)
        ledger={ref['path']:ref for ref in metadata};decoded={};positions={name:i for i,name in enumerate(names)}
        for ref in metadata:
            value=native.read_record(folder/'records',ref)
            for key in ('kind','case','phase'):same(value[key],ref[key],'complete saved metadata '+key)
            decoded[ref['path']]=value
            raw=(folder/'records'/ref['path']).read_bytes();target=out/'native-verified'/ref['path']
            with target.open('xb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
            assert target.read_bytes()==raw;proof['full_native_records_retained'].append(ref)
        def get(ref,kind):
            name=ref['path'];same(ref,ledger[name],'complete record reference metadata')
            value=decoded[name];assert value['kind']==kind;return value
        initial=get(window['initial'],'actual_public_fixture_loaded');joint=initial['value']
        same(initial['run_bytes'],joint['disks']['run.json'],'initial complete run bytes')
        same(initial['account_bytes'],joint['disks']['account.json'],'initial complete account bytes')
        same(json.loads(initial['account_bytes']),joint['account'],'loaded original public account')
        assert joint['run']['id']=='public115-window' and joint['run']['crew_count']==2
        assert set(joint['run']['operators'])=={values[0] for values in OPERATORS}
        assert joint['run']['relics']=={} and joint['run']['public_opaque']['nullable'] is None
        same(joint['run']['public_opaque']['signed_zero'],-0.0,'original opaque negative zero')
        kinds={};numeric=[]
        for name in names:
            value=decoded[name];kind=value['kind'];kinds[kind]=kinds.get(kind,0)+1
            if kind in ('actual_calculate_result','actual_calculate_exception'):
                numeric.append(value);same(value['after'],value['before'],'whole numeric caller/context purity')
                if 'joint' in value['before']:same(value['before']['joint'],joint,'numeric whole public state')
                if kind=='actual_calculate_exception':proof['numeric_exceptions_preserved'].append(ledger[name])
            elif kind=='actual_UI_step':
                same(value['after']['joint'],value['before']['joint'],'every UI-step joint purity')
                same(value['before']['joint'],joint,'every UI-step initial whole public state')
                if value['label'] in ('actual technical checkbox','restore actual ordinary report checkbox'):
                    same(value['after'],value['before'],'actual report checkbox complete result/state purity')
            elif kind=='actual_three_formatter_group':same(value['after'],value['before'],'complete three-formatter group purity')
            else:assert kind in ('actual_public_fixture_loaded','actual_window_snapshot','actual_PNG_complete_current_breakdown','actual_close_RunState_reload')
        assert len(numeric)==window['actual_numeric_calls']
        assert kinds.get('actual_public_fixture_loaded')==1 and kinds.get('actual_window_snapshot')==4
        assert kinds.get('actual_three_formatter_group')==4 and kinds.get('actual_PNG_complete_current_breakdown')==2 and kinds.get('actual_close_RunState_reload')==1
        wanted=[(op+'-window'+str(seconds),op,skill,elite,rank,seconds) for op,skill,elite,rank in OPERATORS for seconds in (2,10)]
        assert [(r['id'],r['operator'],r['window_seconds']) for r in window['rows']]==[(i,o,s) for i,o,_,_,_,s in wanted]
        assert [name for name in names if decoded[name]['kind']=='actual_window_snapshot']==[r['snapshot']['path'] for r in window['rows']]
        snapshots=[];sections=[]
        for row,(identity,op,skill,elite,rank,seconds) in zip(window['rows'],wanted):
            saved=get(row['snapshot'],'actual_window_snapshot');snapshot=saved['value'];numeric=get(row['numeric'],'actual_calculate_result')
            assert saved['case']==numeric['case']==identity and saved['phase']==numeric['phase']=='explicit_snapshot'
            index=positions[row['snapshot']['path']];assert index>=5 and names[index-5]==row['numeric']['path']
            step,group,technical,ordinary=[decoded[names[index-offset]] for offset in (4,3,2,1)]
            assert step['kind']=='actual_UI_step' and step['label']=='MainWindow.calculate'
            assert group['kind']=='actual_three_formatter_group' and group['case']==identity
            assert technical['label']=='actual technical checkbox' and ordinary['label']=='restore actual ordinary report checkbox'
            caller=snapshot['caller'];result=snapshot['damage_result']['result']
            assert len(numeric['before']['args'])==1 and numeric['before']['kwargs']=={}
            same(caller,numeric['before']['args'][0],'complete actual numeric caller')
            same(snapshot['damage_result']['scenario'],caller,'complete UI scenario caller')
            same(result,numeric['result'],'full actual return/UI result')
            assert caller['operator']==op and caller['skill']==skill and caller['timing_mode']=='frames'
            assert (caller['elite'],caller['level'],caller['skill_rank'],caller['trust'],caller['potential'])==(elite,1,rank,0,1)
            assert caller['module_id'] is None and caller['module_level']==0 and caller['relic_ids']==[]
            assert caller['enemy_defense']==0 and caller['enemy_resistance']==0 and caller['continuous_attacks'] is True and caller['healing_targets']==1
            assert caller['window_seconds']==seconds and 'base_attack' not in caller and 'target_enemy' not in caller
            same(caller['timing'],{'windup_frames':0,'recovery_frames':0},'full manual timing reference')
            blocks=check_blocks(result,native);block_map={block['id']:block for block in blocks}
            same(saved['breakdown'],block_map,'full saved new breakdown sections')
            assert row['breakdown_ids']==list(block_map)
            if op=='char_002_amiya':assert set(block_map)=={'output_breakdown_damage'} and result['total_damage']>0
            else:
                assert set(block_map)=={'output_breakdown_damage','output_breakdown_healing','output_breakdown_regeneration'}
                assert result['total_damage'] is None and result['total_healing'] is None
                assert result['amiya_phase_reference']['actual_skill_end_seconds'] is None
                regen=next(c for c in result['components'] if c['damage_type']=='regeneration');assert regen['actual_total'] is None and regen['per_hit']>0
            same(group['before'],{'damage_result':snapshot['damage_result'],'joint':snapshot['state_and_disks']},'whole actual three formatter input')
            same(snapshot['texts'],group['texts'],'all three complete saved strings')
            assert tuple(snapshot['texts'])==('estimate','default','technical') and all(type(t) is str and t for t in snapshot['texts'].values())
            assert snapshot['texts']['estimate']==snapshot['texts']['default']
            assert snapshot['displayed_damage']==snapshot['texts']['default'].replace(chr(160),' ')
            assert '【技术资料】' in snapshot['texts']['technical']
            for text in snapshot['texts'].values():
                for block in blocks:assert '【'+block['title']+'】' in text
            same(technical['before'],{'joint':group['after']['joint'],'damage_result':group['after']['damage_result']},
                'technical checkbox follows complete group with original UI-step dict key order')
            same(ordinary['before'],technical['after'],'ordinary checkbox follows unchanged technical result')
            same(snapshot['state_and_disks'],joint,'every snapshot complete original account/run/all disks')
            snapshots.append(snapshot);sections.append(block_map)
            proof['snapshots'].append({'id':identity,'numeric':row['numeric'],'snapshot':row['snapshot'],
                'formatter_record':ledger[names[index-3]],'technical_checkbox_record':ledger[names[index-2]],
                'ordinary_checkbox_record':ledger[names[index-1]],'full_breakdown_sections':block_map,
                'complete_caller_result_text_state_retained_in_native':True})
        for pair,values,offset in zip(window['pairs'],OPERATORS,(0,2)):
            op=values[0];short,long=snapshots[offset:offset+2]
            assert pair['operator']==op and pair['current_component_fields_checked'] is True and pair['state_account_disks_preserved'] is True
            same(pair['short_snapshot'],window['rows'][offset]['snapshot'],'complete short reference')
            same(pair['long_snapshot'],window['rows'][offset+1]['snapshot'],'complete long reference')
            normalized=native.freeze(long['caller']);normalized['window_seconds']=short['caller']['window_seconds']
            same(normalized,short['caller'],'complete same caller except actual window')
            same(short['state_and_disks'],long['state_and_disks'],'paired full account/run/all disks')
            short_sp=sp_fields(short['damage_result']['result']);long_sp=sp_fields(long['damage_result']['result'])
            same(short_sp,long_sp,'independent derived full SPclock/events/timing-report pair')
            proof['pairs'].append({'operator':op,'short_snapshot':pair['short_snapshot'],'long_snapshot':pair['long_snapshot'],
                'complete_SP_fields':short_sp,'full_SPclock_events_timing_report_equal':True})
        close=get(window['close_reload'],'actual_close_RunState_reload')
        same(close['live_before'],joint,'real close whole original state')
        same(close['restart_state'],joint['run'],'direct whole original accepted RunState reload')
        same(close['account_restart_records'],joint['account'],'direct whole original AccountCache reload')
        same(close['disks_after'],joint['disks'],'close and both reload complete disk purity')
        same(close['persisted_json'],json.loads(initial['run_bytes']),'complete original persisted JSON')
        for png,offset,key in zip(window['pngs'],(1,3),('output_breakdown_damage','output_breakdown_regeneration')):
            snapshot=snapshots[offset];identity=wanted[offset][0];assert png['path']==identity+'.png' and Path(png['path']).name==png['path']
            path=folder/png['path'];raw=path.read_bytes();assert not path.is_symlink() and len(raw)==png['bytes'] and sha(raw)==png['sha256']
            assert raw[:8]==b'\x89PNG\r\n\x1a\n' and raw[12:16]==b'IHDR';width,height=struct.unpack('>II',raw[16:24]);assert width>0 and height>0
            visual=get(png['visual'],'actual_PNG_complete_current_breakdown');assert visual['case']==identity and visual['section']==key
            block=sections[offset][key];assert visual['title']=='【'+block['title']+'】'
            same(visual['displayed_text'],snapshot['displayed_damage'],'complete PNG-bound displayed text')
            visible=visual['visible_blocks'];assert visible and len(visible)<20 and visible[0]==visual['title']
            assert block['metrics'][-1]['label']+'：' in visible[-1] and len(visible)==len(block['metrics'])+1
            for metric,line in zip(block['metrics'],visible[1:]):assert line.startswith(metric['label']+'：')
            document=visual['displayed_text'].split('\n');assert any(document[i:i+len(visible)]==visible for i in range(len(document)))
            assert len(visual['cursor_rects'])==len(visible)*2
            vx,vy,vw,vh=visual['viewport_rect'];assert vw>0 and vh>0
            for x,y,w,h in visual['cursor_rects']:assert w>0 and h>0 and vx<=x and vy<=y and x+w<=vx+vw and y+h<=vy+vh
            with (out/png['path']).open('xb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
            assert (out/png['path']).read_bytes()==raw
            proof['PNGs'].append({'input_metadata':png,'complete_visual_metadata':visual,'width':width,'height':height,'byte_exact_copy':True})
        with (out/'original-window-receipt.json').open('xb') as stream:stream.write(receipt_raw);stream.flush();os.fsync(stream.fileno())
        assert (out/'original-window-receipt.json').read_bytes()==receipt_raw
        with (out/'original-window-exit-code').open('xb') as stream:stream.write(exit_path.read_bytes());stream.flush();os.fsync(stream.fileno())
        proof.update(passed=True,workflow_complete=True,workflow_checks_passed=True,
            actual_native_records_decoded=len(names),actual_numeric_calls=len(numeric),actual_complete_states=4,
            actual_complete_formatter_groups=4,actual_complete_formatter_strings=12,actual_independent_SP_pairs=2,
            actual_full_close_RunState_AccountCache_reload=1,actual_PNG_hash_viewport_gates=2,record_kinds=kinds,
            close_reload_metadata=window['close_reload'])
    except BaseException as error:proof['failure']={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
    finally:
        after=native.source_map(root);proof['source_after']=after;proof['source_additional_after']={name:sha((root/name).read_bytes()) for name in extra}
        proof['source_drift']=[name for name in set(expected)|set(after) if expected.get(name)!=after.get(name)]
        if proof['source_drift'] or proof['source_additional_after']!=extra or guard_path.read_bytes()!=guard_raw or input_path.read_bytes()!=receipt_raw:proof.update(passed=False,workflow_complete=False,workflow_checks_passed=False)
        proof['elapsed_seconds']=time.perf_counter()-started
        with (out/'receipt.json').open('x',encoding='utf-8') as stream:stream.write(json.dumps(proof,ensure_ascii=False,indent=2)+'\n');stream.flush();os.fsync(stream.fileno())
        done.set()
    print(json.dumps({'passed':proof['passed'],'decoded':proof.get('actual_native_records_decoded',0),'SP_pairs':len(proof['pairs'])}))
    return 0 if proof['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
