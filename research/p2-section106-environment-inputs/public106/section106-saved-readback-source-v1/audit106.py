"""Root-only pure Saved106 readback; no project/API/Qt/test execution.

Runtime bindings are supplied only after actual Gold/candidate/raw/visual exist.
Readback cannot manufacture missing per-UI-step pre/post evidence in d407.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
import time
import traceback

from native_evidence import assert_native_equal, read_record, source_map

HELPER='f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a'
RUNNER='d4076884a45a8044778a6d358e1a4e54921edde7f6baeb545a3a4c35ed65d520'
ORIGINAL='c09e542f3d1cee720c31daa638663a133bd1894268eb7bb20abc062ccfb92b25'
TRANSPORT='028063cf676eee596c07046fd009b18cf48b2bc71ed2665ac12fc477988e9624'
ORIGINAL_MANIFEST='2e8f3e9b74a84cb9d4ef7cee49df8bc8510c6b2bc3e09afd74b94d6af32ce217'
TEST='6cd75f91e466daa6b231a6e318b44795f596a2b8d292c0fd6939329117521a8e'
CORE='a75d9497ce34f68de787e3ba99704741f2c873c2c5fa9b5de01e6620b1f00f89'
HEALTHY=('healthy-mode-missing-source-missing','healthy-mode-normal',
         'healthy-modeDifficulty-zero','healthy-both-normal-fifteen',
         'healthy-source-empty','healthy-source-whitespace','healthy-source-text',
         'healthy-target-zero','healthy-target-one')
MODES=('bad-mode-month-team','bad-modeDifficulty-month-team','bad-mode-conflicting',
       'bad-mode-null','bad-mode-list')
GRADES={'bad-grade-bool':True,'bad-grade-float':2.0,'bad-grade-text':'2','bad-grade-list':[2]}
SOURCES={'bad-source-null':None,'bad-source-list':[],'bad-source-number':1,
         'bad-source-map':{},'bad-source-bool':False}
BOOLS={'enemy-level-zero-bool','enemy-level-one-bool'}
TEMP=b'public106-unmodified-original-temporary\n'
MODE_ERROR='当前保密等级数值计算仅支持NORMAL模式，其他模式不能套用常规难度修正。'
GRADE_ERROR='本局保密等级需要0–15的整数。'
IDENTITY_ERROR='目标敌人身份/等级必须与关卡引用唯一匹配。'


def sha(raw):return hashlib.sha256(raw).hexdigest()


def same(actual,expected,label):assert_native_equal(actual,expected,label)


def bound_bytes(pin):
    assert type(pin) is dict and type(pin['path']) is str
    assert type(pin['bytes']) is int and pin['bytes']>=0
    assert type(pin['sha256']) is str and len(pin['sha256'])==64
    path=Path(pin['path']);assert not path.is_symlink()
    raw=path.read_bytes();assert len(raw)==pin['bytes'] and sha(raw)==pin['sha256'],str(path)
    return raw


def json_bytes(raw):
    assert type(raw) is bytes
    return json.loads(raw.decode('utf-8'))


def no_file(value):same(value,{'exists':False,'bytes':None},'Absent actual disk entry')


def main():
    parser=argparse.ArgumentParser()
    for name in ('root','bindings','bindings-sha256','out'):parser.add_argument('--'+name,required=True)
    args=parser.parse_args();root=Path(args.root).resolve();out=Path(args.out).resolve()
    assert not out.exists() and out.parent.is_dir() and out!=root and root not in out.parents
    packet=Path(__file__).resolve().parent;assert packet!=root and root not in packet.parents
    assert sha((packet/'native_evidence.py').read_bytes())==HELPER
    binding_path=Path(args.bindings);binding_raw=binding_path.read_bytes()
    assert not binding_path.is_symlink() and sha(binding_raw)==args.bindings_sha256
    bindings=json_bytes(binding_raw)
    assert bindings['kind']=='ROOT_ACTUAL106_SAVED_ARTIFACT_BINDINGS_V1' and bindings['actual_runtime_ready'] is True
    active={'dataset':'bindings','case':None,'record':None};started=time.perf_counter()
    report={'kind':'ROOT_ACTUAL_106_PURE_SAVED_READBACK','passed':False,'workflow_complete':False,
            'audit_Source_sha256':sha(Path(__file__).read_bytes()),'bindings_sha256':sha(binding_raw),
            'native_helper_sha256':HELPER,'decoded_records':[],'original_pure_checks':[],
            'calculator_caller_checks':[],'snapshot_checks':[],'restart_checks':[],
            'healthy_Gold_points':[],'direct_API_checks':[],'PNG_checks':[],
            'project_API_formatter_numeric_Qt_tests_Wine_Git_executed':False,
            'saved_inputs_written':False,'native_windows_verified':False,
            'natural_OCR_producer_verified':False,
            'window_per_UI_step_prepost_saved_verified':False,
            'individual_formatter_prepost_saved_verified':False,
            'cross_separate_freeze_live_alias_verified':False,
            'window_pure_scope':'Calculator caller before/after and saved snapshot raw JSON/.tmp views. Per-UI/formatter state-disk assertions remain frozen runner runtime attestations; missing pre/post records cannot be recreated.',
            'original_pure_scope':'All original284 complete combined (args,state,disks) native before/after records.',
            'restart_scope':'Actual saved JSON graph and direct RunState reload; no live alias or second MainWindow reopen claim.'}
    current=None;additional=None;source_bindings={}
    try:
        assert sha(bound_bytes(bindings['runner']))==RUNNER
        assert sha(bound_bytes(bindings['transport']))==TRANSPORT
        transport=json_bytes(bound_bytes(bindings['transport']))
        assert sha(bound_bytes(bindings['original_manifest']))==ORIGINAL_MANIFEST
        manifest=json_bytes(bound_bytes(bindings['original_manifest']))
        assert bound_bytes(bindings['original_primary'])==b'0\n'
        raw=bound_bytes(bindings['original_receipt']);assert sha(raw)==ORIGINAL
        original=json_bytes(raw);original_dir=Path(bindings['original_receipt']['path']).resolve().parent
        assert original['observation_only'] is True and original['product_pass'] is False
        assert original['observation_complete'] is True and original['source_and_CORE_unchanged'] is True
        assert original['source_before']==original['source_after'] and len(original['source_before'])==748
        assert original['CORE_before']==original['CORE_after']==CORE
        assert original['actual_public_consumer_calls']==284 and original['actual_native_records']==350
        old_guard=json_bytes(bound_bytes(bindings['gold_guard']))
        guard=json_bytes(bound_bytes(bindings['candidate_guard']))
        old=old_guard['source_sha256'];current=guard['source_sha256'];additional=guard['source_additional_sha256']
        assert old==original['source_before'] and len(old)==748 and len(current)==749
        assert additional==old_guard['source_additional_sha256']=={'CORE_0.70_VERIFICATION.json':CORE}
        assert set(current)-set(old)=={'tests/test_environment_input_106.py'} and not set(old)-set(current)
        assert current['tests/test_environment_input_106.py']==TEST
        assert {name for name in old if old[name]!=current[name]}=={entry['path'] for entry in transport['changes']}|{'scripts/verify_cloud.py'}
        for entry in transport['changes']:
            assert old[entry['path']]==entry['before_source_sha256'] and current[entry['path']]==entry['after_source_sha256']
        report['source_before']=source_map(root);assert report['source_before']==current
        report['source_additional_before']={name:sha((root/name).read_bytes()) for name in additional}
        assert report['source_additional_before']==additional
        original_values={};original_meta={}
        native_dir=original_dir/'native';assert not native_dir.is_symlink()
        assert {p.name for p in native_dir.iterdir()}=={m['path'] for m in original['native_records']}
        original_kinds=Counter()
        for sequence,meta in enumerate(original['native_records'],1):
            active.update(dataset='original',case=meta['case'],record=meta['path'])
            assert meta['path']=='%06d.pickle.gz'%sequence
            value=read_record(native_dir,meta);original_values[meta['path']]=value;original_meta[meta['path']]=meta
            original_kinds[meta['kind']]+=1
            if meta['kind']=='pure-public-consumer':
                same(value['after'],value['before'],'Original full combined caller/state/disk/tmp native conservation')
                report['original_pure_checks'].append({'case':meta['case'],'phase':meta['phase'],'record':meta['path'],
                    'combined_graph_types_floatbits_order_alias_verified':True})
            elif meta['kind']=='authorized-apply-save-phase':
                same(value['caller_after'],value['caller_before'],'Original fresh observation complete caller')
                assert value['result'] is True and value['error'] is None
                persisted=json_bytes(value['disks_after']['run']['bytes'])
                same(value['state_after'],persisted,'Original legal saved state versus actual persisted JSON graph')
            elif meta['kind']=='real-RunState-restart':
                same(value['restarted'],value['persisted_JSON'],'Original actual reload complete persisted JSON graph')
                same(json_bytes(value['disks']['run']['bytes']),value['persisted_JSON'],'Original reload still has actual saved bytes')
            else:assert meta['kind']=='accepted-loader'
            report['decoded_records'].append({'dataset':'original',**meta,'safe_native_hash_decode_verified':True})
        assert original_kinds=={'pure-public-consumer':284,'accepted-loader':22,
                               'authorized-apply-save-phase':22,'real-RunState-restart':22}
        for call in original['calls']:
            assert original_meta[call['native']['path']]==call['native']
            value=original_values[call['native']['path']]
            assert (value['error'] is None) is call['returned']
            if value['error'] is not None:
                assert value['error']['type']==call['error']['type'] and value['error']['message']==call['error']['message']
        datasets={}
        for phase in ('gold','candidate'):
            active.update(dataset=phase,case=None,record=None)
            raw_primary=bound_bytes(bindings[phase+'_primary']);assert raw_primary==b'0\n'
            raw_receipt=bound_bytes(bindings[phase+'_receipt']);receipt=json_bytes(raw_receipt)
            directory=Path(bindings[phase+'_receipt']['path']).resolve().parent
            assert directory!=root and root not in directory.parents
            expected=old if phase=='gold' else current
            assert receipt['kind']=='ROOT_ACTUAL_106_REAL_MAINWINDOW' and receipt['phase']==phase
            assert receipt['passed'] is True and receipt['workflow_complete'] is True and receipt['runner_sha256']==RUNNER
            assert receipt['source_guard_sha256']==bindings[phase+'_guard']['sha256']
            assert receipt['original_receipt_sha256']==ORIGINAL
            assert receipt['original_raw_exit_sha256']==bindings['original_primary']['sha256']
            assert receipt['source_before']==receipt['source_after']==expected and receipt['source_drift']==[]
            assert receipt['source_additional_before']==receipt['source_additional_after']==additional
            assert receipt['Qt_errors']==[] and receipt['deadline_seconds']==450 and 0<receipt['elapsed_seconds']<450
            for name in ('native_windows_verified','private_state_access','game_chat_sampling_executed','natural_OCR_producer_verified'):
                assert receipt[name] is False
            identities=list(HEALTHY) if phase=='gold' else list(HEALTHY+MODES+tuple(GRADES)+tuple(SOURCES))
            assert [row['id'] for row in receipt['rows']]==identities
            assert [row['id'] for row in receipt['direct_API']]==[row['id'] for row in manifest['direct_cases']]
            if phase=='candidate':assert receipt['actual_gold_receipt_sha256']==bindings['gold_receipt']['sha256']
            values={};metadata={};latest={};predecessor={};kinds=Counter()
            record_dir=directory/'records';assert not record_dir.is_symlink()
            assert {p.name for p in record_dir.iterdir()}=={m['path'] for m in receipt['records']}
            for sequence,meta in enumerate(receipt['records'],1):
                active.update(case=meta['case'],record=meta['path'])
                assert meta['path']=='%06d.pickle.gz'%sequence and meta['path'] not in values
                assert meta['case'] in identities or meta['case'] in {row['id'] for row in manifest['direct_cases']}
                value=read_record(record_dir,meta)
                for name in ('kind','case','phase'):assert value[name]==meta[name]
                values[meta['path']]=value;metadata[meta['path']]=meta;kinds[meta['kind']]+=1
                if meta['kind'] in ('actual_calculate_result','actual_calculate_exception'):
                    same(value['after'],value['before'],'All actual window/direct calculator callers conserved')
                    assert type(value['before']) is dict and list(value['before'])==['args','kwargs']
                    latest[meta['case']]=meta['path']
                    report['calculator_caller_checks'].append({'dataset':phase,'case':meta['case'],'record':meta['path'],
                        'complete_retained_caller_graph_verified':True})
                elif meta['kind'] in ('actual_direct_API_contract','actual_initial_window_snapshot',
                                     'actual_observation_window_snapshot','actual_unconfirmed_manual_preset_snapshot'):
                    assert meta['case'] in latest;predecessor[meta['path']]=latest[meta['case']]
                else:assert meta['kind']=='actual_close_RunState_reload'
                report['decoded_records'].append({'dataset':phase,**meta,'safe_native_hash_decode_verified':True})
            assert kinds['actual_direct_API_contract']==11
            assert kinds['actual_initial_window_snapshot']==kinds['actual_observation_window_snapshot']==kinds['actual_close_RunState_reload']==len(identities)
            assert kinds['actual_unconfirmed_manual_preset_snapshot']==(0 if phase=='gold' else len(MODES)+len(GRADES))
            assert sum(kinds.values())==len(receipt['records'])
            datasets[phase]={'receipt':receipt,'directory':directory,'values':values,'metadata':metadata,
                             'predecessor':predecessor,'identities':identities,'kinds':dict(kinds)}
        for phase,data in datasets.items():
            for direct_row in data['receipt']['direct_API']:
                identity=direct_row['id'];active.update(dataset=phase,case=identity)
                record=direct_row['record'];assert record==data['metadata'][record['path']]
                value=data['values'][record['path']];actual=data['values'][data['predecessor'][record['path']]]
                assert value['kind']=='actual_direct_API_contract'
                same(actual['before'],{'args':(value['caller'],),'kwargs':{}},'Direct recorded entire caller reaches actual API')
                if value['error'] is not None:
                    assert actual['kind']=='actual_calculate_exception'
                    for field in ('type','message'):
                        assert actual['error'][field]==value['error'][field]==direct_row['numeric_error'][field]
                else:
                    assert actual['kind']=='actual_calculate_result' and direct_row['numeric_error'] is None
                old_call=next(c for c in original['calls'] if c['case']==identity and c['phase']=='direct_calculate_damage')
                old_value=original_values[old_call['native']['path']]
                same(((value['caller'],),None,None),old_value['before'],'Direct original full graph caller identity including old float')
                changed=phase=='candidate' and identity in BOOLS
                if changed:
                    assert direct_row['numeric_returned'] is False and value['result'] is None
                    assert value['error']['type']=='ValueError' and value['error']['message']==IDENTITY_ERROR
                    assert actual['kind']=='actual_calculate_exception' and old_call['returned'] is True
                    assert direct_row['old_complete_result_equal'] is False
                elif old_call['returned']:
                    assert direct_row['numeric_returned'] is True and value['error'] is None
                    same(value['result'],actual['result'],'Direct saved result equals actual original callee return graph')
                    same(value['result'],old_value['result'],'Direct complete original result with type/order/floatbits/alias')
                    assert direct_row['old_complete_result_equal'] is True
                else:
                    assert direct_row['numeric_returned'] is False and value['result'] is None
                    assert value['error']['type']==old_value['error']['type'] and value['error']['message']==old_value['error']['message']
                target=value['caller']['target_enemy']
                if type(target) is dict and target:
                    old_preview=next(c for c in original['calls'] if c['case']==identity and c['phase']=='direct_enemy_preview')
                    previous=original_values[old_preview['native']['path']]
                    same(((target['stage_id'],target['enemy_id'],target['level'],value['caller']['run_config']),None,None),
                         previous['before'],'Preview original caller full typed graph')
                    if old_preview['returned']:
                        assert value['preview_error'] is None
                        same(value['preview'],previous['result'],'Complete original integer preview retained')
                    else:
                        assert value['preview'] is None
                        assert value['preview_error']['type']==previous['error']['type'] and value['preview_error']['message']==previous['error']['message']
                report['direct_API_checks'].append({'dataset':phase,'case':identity,'record':record['path'],
                                                   'bool_new_error_verified':changed,'old_complete_result_equal':direct_row['old_complete_result_equal']})
            for row in data['receipt']['rows']:
                identity=row['id'];active.update(dataset=phase,case=identity)
                assert row['constructor_returned'] is True and row['apply_result'] is True
                before=data['values'][row['before']['path']];after=data['values'][row['after']['path']]
                restart=data['values'][row['restart']['path']]
                for key,kind in (('before','actual_initial_window_snapshot'),('after','actual_observation_window_snapshot'),('restart','actual_close_RunState_reload')):
                    assert row[key]==data['metadata'][row[key]['path']]
                    assert data['values'][row[key]['path']]['case']==identity and data['values'][row[key]['path']]['kind']==kind
                snapshots=[(row['before'],before),(row['after'],after)]
                if identity in MODES or identity in GRADES:
                    manuals=[m for m in data['metadata'].values() if m['case']==identity and m['kind']=='actual_unconfirmed_manual_preset_snapshot']
                    assert len(manuals)==1;snapshots.append((manuals[0],data['values'][manuals[0]['path']]))
                for meta,snapshot in snapshots:
                    active['record']=meta['path'];view=snapshot['view']
                    calculation=data['values'][data['predecessor'][meta['path']]]
                    caller=calculation['before']['args'][0]
                    assert caller['operator']=='mechanist' and caller['skill']==3
                    same(caller['run_config'],snapshot['durable']['run']['config'],'Full raw config retained in actual numeric argument')
                    raw_difficulty=snapshot['durable']['run']['config']['difficulty']
                    pending=meta['kind']!='actual_observation_window_snapshot' and (identity in MODES or identity in GRADES)
                    if pending:
                        expected_error=MODE_ERROR if identity in MODES else GRADE_ERROR
                        assert calculation['kind']=='actual_calculate_exception' and calculation['error']['type']=='ValueError'
                        assert calculation['error']['message']==expected_error and view['damage_result'] is None
                        assert view['three_texts']=={'pending':expected_error} and view['displayed_damage']==expected_error
                        assert view['difficulty_UI']['enabled'] is True and '尚未满足当前常规模式资格' in view['difficulty_UI']['tooltip']
                        assert 'difficulty' not in view['reuse']['confirmed'] and '保密等级未确认' in view['summary']
                        if meta['kind']=='actual_unconfirmed_manual_preset_snapshot':assert view['difficulty_UI']['preset']==15
                    else:
                        assert calculation['kind']=='actual_calculate_result' and type(view['damage_result']) is dict
                        same(view['damage_result']['scenario'],caller,'Full actual saved scenario equals original API caller')
                        same(view['damage_result']['result'],calculation['result'],'Full saved numeric returned graph including all aliases')
                        texts=view['three_texts'];assert list(texts)==['estimate','default','technical']
                        assert all(type(text) is str and text for text in texts.values()) and texts['estimate']==texts['default']
                        assert view['displayed_damage']==texts['default'].replace(chr(160),' ')
                        assert view['difficulty_UI']=={'enabled':False,'tooltip':'自动读取本局保密等级；切换页面后保留最近确认值。','preset':raw_difficulty['value']}
                        assert 'difficulty' in view['reuse']['confirmed']
                        if identity in SOURCES and meta['kind']=='actual_initial_window_snapshot':
                            same(raw_difficulty['source'],SOURCES[identity],'Raw unknown source type/value kept')
                            result=view['damage_result']['result']
                            same(result['run_resolution']['difficulty']['source'],SOURCES[identity],'Raw numeric provenance is not washed')
                            section=next(s for s in result['report']['sections'] if s['id']=='run_environment')
                            assert section['notes'][0]=='本局保密等级：2；来源：未确认（来源字段不是文本）'
                    report['snapshot_checks'].append({'dataset':phase,'case':identity,'record':meta['path'],
                        'numeric_original_record':data['predecessor'][meta['path']], 'pending_original_error':pending,
                        'text_sha256':{name:sha(text.encode('utf-8')) for name,text in view['three_texts'].items()},
                        'state_disk_joint_per_step_evidence_present':False})
                raw_run=json_bytes(before['disks']['run']['bytes'])
                for name,value in raw_run.items():
                    if name!='notice':same(before['durable']['run'][name],value,'Initial raw JSON field retained at saved pure view')
                same(before['disks']['run_tmp'],{'exists':True,'bytes':TEMP},'Original temporary sentinel preserved at initial pure view')
                no_file(before['disks']['account_tmp']);no_file(after['disks']['account_tmp']);no_file(after['disks']['run_tmp'])
                if identity in GRADES:same(before['durable']['run']['config']['difficulty']['value'],GRADES[identity],'Bad cached grade exact raw type remains')
                same(after['disks']['account'],before['disks']['account'],'Run-only recovery keeps exact original account bytes')
                same(after['durable']['account'],before['durable']['account'],'Run-only recovery keeps original account memory graph')
                same(after['durable']['run']['operators'],before['durable']['run']['operators'],'Environment recovery keeps all raw operator records')
                assert after['durable']['run']['config']['difficulty']=={'value':2,'source':'public106-fresh-normal-label','captured_at':1001.0}
                same(restart['live_state_before_close'],after['durable']['run'],'Saved close retains entire live run graph')
                same(restart['observation_caller_before'],restart['observation_caller_after'],'Fresh observation actual caller retained through close/reload')
                same(restart['observation_caller_after'],({'operators':[],'config':{'difficulty':{'value':2,'source':'public106-fresh-normal-label'}}},1001.0),
                     'Legal explicit fresh observation and float capture time')
                same(restart['disks'],after['disks'],'Actual close/direct reload retains full current file/tmp phase')
                persisted=json_bytes(after['disks']['run']['bytes'])
                same(restart['persisted_json'],persisted,'Saved restart oracle is actual serialized bytes')
                same(restart['state'],persisted,'Actual direct RunState reload restores complete JSON graph')
                same(restart['reuse'],after['view']['reuse'],'Actual direct reload retains full eligibility context/reuse')
                report['restart_checks'].append({'dataset':phase,'case':identity,'record':row['restart']['path'],
                    'actual_close_direct_RunState_JSON_graph_verified':True,'live_cross_JSON_alias_claimed':False})
        gold_rows={r['id']:r for r in datasets['gold']['receipt']['rows']}
        for row in datasets['candidate']['receipt']['rows']:
            if row['id'] not in gold_rows:continue
            assert row['complete_healthy_initial_and_after_native_and_three_texts_equal'] is True
            for point in ('before','after'):
                old_value=datasets['gold']['values'][gold_rows[row['id']][point]['path']]
                new_value=datasets['candidate']['values'][row[point]['path']]
                same({n:new_value[n] for n in ('view','durable','disks')},{n:old_value[n] for n in ('view','durable','disks')},
                     'All complete healthy native Gold snapshots and three full texts')
                report['healthy_Gold_points'].append({'case':row['id'],'point':point,'complete_native_Gold_equal':True})
        visual=json_bytes(bound_bytes(bindings['visual']))
        assert visual['passed'] is True and visual['workflow_complete'] is True
        assert visual['native_windows_game_chat_verified'] is False
        pngs=datasets['candidate']['receipt']['pngs'];assert len(pngs)==len(visual['pngs'])==4
        assert datasets['gold']['receipt']['pngs']==[]
        expected_pngs={'healthy-normal-environment.png':('healthy-mode-normal','initial-actual-view',0),
                       'mode-unconfirmed-original-retained.png':('bad-mode-month-team','initial-actual-view',0),
                       'legal-new-normal-observation-recovered.png':('bad-mode-month-team','actual-fresh-observation-save',1),
                       'source-unconfirmed-calculate-retained.png':('bad-source-null','initial-actual-view',1)}
        assert {p['file'] for p in pngs}==set(expected_pngs)
        for png,viewed in zip(pngs,visual['pngs']):
            assert (png['case'],png['phase'],png['tab_index'])==expected_pngs[png['file']]
            assert {name:viewed[name] for name in png}==png and viewed['actually_viewed'] is True
            assert type(viewed['visual_observation']) is str and viewed['visual_observation']
            path=datasets['candidate']['directory']/png['file'];assert Path(png['file']).name==png['file'] and not path.is_symlink()
            raw=path.read_bytes();assert len(raw)==png['bytes'] and sha(raw)==png['sha256'] and raw.startswith(b'\x89PNG\r\n\x1a\n')
            report['PNG_checks'].append({**png,'actual_Root_visual_ledger_bound':True})
        report.update(passed=True,workflow_complete=True,
                      decoded_record_count=len(report['decoded_records']),
                      original_combined_pure_records_checked=len(report['original_pure_checks']),
                      actual_calculator_caller_records_checked=len(report['calculator_caller_checks']),
                      saved_snapshots_checked=len(report['snapshot_checks']),
                      direct_API_contracts_checked=len(report['direct_API_checks']),
                      healthy_Gold_points_checked=len(report['healthy_Gold_points']),
                      actual_close_direct_RunState_records_checked=len(report['restart_checks']),
                      phase_record_counts={phase:len(data['receipt']['records']) for phase,data in datasets.items()},
                      phase_record_kinds={phase:data['kinds'] for phase,data in datasets.items()})
    except BaseException as error:
        report['failure']={'active':dict(active),'type':type(error).__name__,'message':str(error),
                           'traceback':''.join(traceback.format_exception(type(error),error,error.__traceback__))}
    finally:
        report['bindings']=bindings
        if current is not None:
            report['source_after']=source_map(root)
            report['source_drift']=[name for name in set(current)|set(report['source_after']) if current.get(name)!=report['source_after'].get(name)]
            report['source_additional_after']={name:sha((root/name).read_bytes()) for name in additional}
            if report['source_drift'] or report['source_additional_after']!=additional:report.update(passed=False,workflow_complete=False)
        report['elapsed_seconds']=time.perf_counter()-started
        with out.open('x',encoding='utf-8') as stream:stream.write(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'passed':report['passed'],'decoded_records':len(report['decoded_records']),
                      'saved_snapshots':len(report['snapshot_checks']),'healthy_Gold_points':len(report['healthy_Gold_points'])}))
    return 0 if report['passed'] else 1


if __name__=='__main__':sys.exit(main())
