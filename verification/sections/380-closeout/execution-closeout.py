from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone,timedelta
import json,runpy,subprocess,shutil
ROOT=Path(__file__).resolve().parents[1]


def _verified_full380():
    from pathlib import Path as _Path
    from hashlib import sha256 as _sha256
    import json as _json
    import subprocess as _subprocess
    def _read(name):
        path=ROOT/name
        assert path.is_file()and not path.is_symlink()and path.resolve().is_relative_to(ROOT.resolve()),name
        return _json.loads(path.read_bytes())
    def _sha(name):return _sha256((ROOT/name).read_bytes()).hexdigest()
    f=_read('verification/full-380/summary.json')
    assert f['after_section']==380 and f['available_checks_passed']is True and f['scope_not_reduced']is True
    assert f['actual_root_controller_exit']==0 and f['single_available_scope_execution_all_green']is True
    assert f['current_worktree_validation_authority']is True and f['source_drift']==[]
    assert f['complete_repository_validation']is False and all(f[k]is False for k in('P3_complete','P2_complete','P1_complete'))
    assert f['native_windows_game_chat_verified']is False and f['historical_original_Windows_verified']is False
    freeze=f['source_freeze'];assert freeze.startswith('verification/full-380/source-freeze-attempt')and freeze.endswith('.json')
    assert _sha(freeze)==f['source_freeze_sha256']
    d=_read(freeze)
    assert d['section']==380 and d['root_declared']is True and d['parent_commit']==f['tested_worktree_parent_commit']
    assert d['actual_validation_attempt']==f['actual_validation_attempt']and type(d['actual_validation_attempt'])is int and d['actual_validation_attempt']>=1
    assert len(d['selectors'])==len(set(d['selectors']))==f['maintained_selectors']
    assert len(d['p3_scripts'])==f['native_supplements']and f['actual_required_components']==5+len(d['p3_scripts'])
    assert all(any(int(mode.split('_')[1])==n for mode in d['p3_scripts'])for n in range(286,381))
    for mode in('p3_304','p3_305'):assert d['p3_script_options'][mode]['explicit_current_source_freeze']is True
    assert d['p3_script_options']['p3_312']['visible_ms']==120000
    maps={}
    for group in('source_sha256','legacy_native_source_sha256','supplemental_public_inputs_sha256'):
        for name,pin in d[group].items():
            if name in maps:assert maps[name]==pin,name
            maps[name]=pin
    for name,pin in maps.items():
        path=ROOT/name
        assert path.is_file()and not path.is_symlink()and path.resolve().is_relative_to(ROOT.resolve())and _sha(name)==pin,name

    _expected_canonical = [{'mode': 'p3_369', 'canonical_script': 'scripts/verify_current_boss_documents_window_369.py', 'local_path': '.cache/game-data/levels/enemydata/enemy_database.json', 'public_path': 'verification/full-380/explicit-public-build-inputs/f8dd03997d0e3eae65cc4b77bcb6b5ef198488504f738defc31cad5e13c3680c.json', 'sha256': 'f8dd03997d0e3eae65cc4b77bcb6b5ef198488504f738defc31cad5e13c3680c', 'bytes': 15022043, 'origin_manifests': [{'path': 'research/p3-boss-phase-309/source-manifest.json', 'sha256': 'ae8448916f2b8355e0d946f95d4e6748fcaa2a74838e9949794e7485b18b036d', 'bytes': 4332, 'json_pointer': '/build_authority_files/.cache~1game-data~1levels~1enemydata~1enemy_database.json'}, {'path': 'research/p3-boss-cycle-310/source-manifest.json', 'sha256': 'cddc4465769edd6e74a231838ea325a895562665bee5e2283f6c20880b1e8052', 'bytes': 6015, 'json_pointer': '/build_authority_files/.cache~1game-data~1levels~1enemydata~1enemy_database.json'}, {'path': 'research/p3-boss-hunt-311/source-manifest.json', 'sha256': 'dc1024855751338d2b4b536c53c83e8cd56e75f548b12296dfa34d3b12335321', 'bytes': 5912, 'json_pointer': '/build_authority_files/.cache~1game-data~1levels~1enemydata~1enemy_database.json'}]}, {'mode': 'p3_369', 'canonical_script': 'scripts/verify_current_boss_documents_window_369.py', 'local_path': '.cache/game-data/levels/obt/roguelike/ro6/level_rogue6_b-4-b.json', 'public_path': 'research/p3-auxiliary-mechanisms/level_rogue6_b-4-b.json', 'sha256': 'fc2f7ae7371829259bd445a45704d79f30f84094f8eedbfa74b026fe075c51ea', 'bytes': 202372, 'origin_manifests': [{'path': 'research/p3-boss-hunt-311/source-manifest.json', 'sha256': 'dc1024855751338d2b4b536c53c83e8cd56e75f548b12296dfa34d3b12335321', 'bytes': 5912, 'json_pointer': '/build_authority_files/.cache~1game-data~1levels~1obt~1roguelike~1ro6~1level_rogue6_b-4-b.json'}]}, {'mode': 'p3_369', 'canonical_script': 'scripts/verify_current_boss_documents_window_369.py', 'local_path': '.cache/game-data/levels/obt/roguelike/ro6/level_rogue6_b-4.json', 'public_path': 'verification/full-380/explicit-public-build-inputs/1161795429a9dd4f36b6fcf4e6cf5b6300e2bcce6f04a860e9f7b31e6619d292.json', 'sha256': '1161795429a9dd4f36b6fcf4e6cf5b6300e2bcce6f04a860e9f7b31e6619d292', 'bytes': 207445, 'origin_manifests': [{'path': 'research/p3-boss-hunt-311/source-manifest.json', 'sha256': 'dc1024855751338d2b4b536c53c83e8cd56e75f548b12296dfa34d3b12335321', 'bytes': 5912, 'json_pointer': '/build_authority_files/.cache~1game-data~1levels~1obt~1roguelike~1ro6~1level_rogue6_b-4.json'}]}, {'mode': 'p3_369', 'canonical_script': 'scripts/verify_current_boss_documents_window_369.py', 'local_path': '.cache/game-data/levels/obt/roguelike/ro6/level_rogue6_b-5.json', 'public_path': 'verification/full-380/explicit-public-build-inputs/aec26f5d1146281bdc50b73d0c88ce99c37c07c3bd6361ed2af8980ce53c1faf.json', 'sha256': 'aec26f5d1146281bdc50b73d0c88ce99c37c07c3bd6361ed2af8980ce53c1faf', 'bytes': 205518, 'origin_manifests': [{'path': 'research/p3-boss-cycle-310/source-manifest.json', 'sha256': 'cddc4465769edd6e74a231838ea325a895562665bee5e2283f6c20880b1e8052', 'bytes': 6015, 'json_pointer': '/build_authority_files/.cache~1game-data~1levels~1obt~1roguelike~1ro6~1level_rogue6_b-5.json'}]}, {'mode': 'p3_369', 'canonical_script': 'scripts/verify_current_boss_documents_window_369.py', 'local_path': '.cache/game-data/levels/obt/roguelike/ro6/level_rogue6_b-6.json', 'public_path': 'research/p3-spawn-candidates-299/levels/57db7782a27808e0187f1fbaf41c3886a85e7687d40dc451281846d4297efad9.json', 'sha256': '57db7782a27808e0187f1fbaf41c3886a85e7687d40dc451281846d4297efad9', 'bytes': 165191, 'origin_manifests': [{'path': 'research/p3-boss-phase-309/source-manifest.json', 'sha256': 'ae8448916f2b8355e0d946f95d4e6748fcaa2a74838e9949794e7485b18b036d', 'bytes': 4332, 'json_pointer': '/build_authority_files/.cache~1game-data~1levels~1obt~1roguelike~1ro6~1level_rogue6_b-6.json'}]}]
    assert d.get('canonical_local_public_input_bindings') == _expected_canonical
    _canonical_names = {row['local_path'] for row in _expected_canonical}
    assert {(mode,name) for mode,names in d['p3_script_selected_paths'].items() for name in names if name.startswith('.cache/')} == {('p3_369',name) for name in _canonical_names}
    assert d.get('canonical_local_public_input_sha256') == {row['local_path']:row['sha256'] for row in _expected_canonical}
    for row in _expected_canonical:
        assert row['mode']=='p3_369' and row['canonical_script']=='scripts/verify_current_boss_documents_window_369.py'
        for origin in row['origin_manifests']:
            authority=ROOT/origin['path']
            assert authority.is_file()and not authority.is_symlink()and authority.resolve().is_relative_to(ROOT.resolve())
            assert _sha(origin['path'])==origin['sha256']and authority.stat().st_size==origin['bytes']
            assert _read(origin['path'])['build_authority_files'][row['local_path']]=={'sha256':row['sha256'],'bytes':row['bytes']}
            assert origin['json_pointer']=='/build_authority_files/'+row['local_path'].replace('~','~0').replace('/','~1')
        _raws=[]
        for name in(row['local_path'],row['public_path']):
            path=ROOT/name
            assert path.is_file()and not path.is_symlink()and path.resolve().is_relative_to(ROOT.resolve())
            for parent in path.parents:
                if parent==ROOT:break
                assert not parent.is_symlink()
            raw=path.read_bytes();assert len(raw)==row['bytes']and _sha256(raw).hexdigest()==row['sha256']
            _raws.append(raw)
        assert _raws[0]==_raws[1]
        assert d['supplemental_public_inputs_sha256'][row['public_path']]==row['sha256']
    manifest='verification/full-380/execution-attempt'+str(d['actual_validation_attempt'])+'/archive-manifest.json'
    assert f['archive_manifests_sha256'][manifest]==_sha(manifest)
    archive=_read(manifest)
    assert archive['section']==380 and archive['actual_validation_attempt']==d['actual_validation_attempt']
    assert archive['actual_root_controller_exit']==0 and archive['source_freeze_sha256']==f['source_freeze_sha256']
    assert archive['activation_sha256']==f['activation_sha256']and archive['required_component_positions']==f['actual_required_components']
    assert archive['all_executed_retained_Popen_and_assigned_jobs_terminal']is True
    assert archive['all_original_ordered_components_retained']is True and archive['automated_available_scope_passed']is True
    visual=f['root_PNG_visual_review'];assert visual['file']=='verification/full-380/root-visual-review.json'
    assert _sha(visual['file'])==visual['sha256']and visual['all_reviewed']is True
    pixels=_read(visual['file'])
    assert pixels['section']==380 and pixels['actual_validation_attempt']==d['actual_validation_attempt']
    assert pixels['source_freeze_sha256']==f['source_freeze_sha256']and pixels['archive_manifest_sha256']==_sha(manifest)
    assert pixels['all_reviewed']is True and pixels['pending_actual_view_rows']==0 and pixels['blocking_visual_issues']==[]
    assert visual['image_count']==pixels['image_count']==len(pixels['images'])
    _subprocess.run(['git','merge-base','--is-ancestor',d['parent_commit'],'HEAD'],cwd=ROOT,check=True,stdout=_subprocess.PIPE,stderr=_subprocess.PIPE)
    return f


def read(n):return json.loads((ROOT/n).read_bytes())
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+chr(10)).encode('utf8')
def sha(n):return sha256((ROOT/n).read_bytes()).hexdigest()
def pin(n):return{'receipt':n,'sha256':sha(n)}
def doc(n,s):
 p=ROOT/n;style='\r\n'if b'\r\n'in p.read_bytes()else'\n';p.write_bytes(s.replace('\r\n','\n').replace('\n',style).encode('utf8'))
parent='afab40c3bb4ea8b95118e8cbe34aa07204c1c615';assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==parent
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
title='“物欲拮抗者” · 指令、屏障与斯第奇'
change='物欲遮天普通、紧急及dlc1四份准确配置新增物欲拮抗者完整指令与形态阅读。默认精确level0的80秒屏障准备，另一数据库级别40秒原文仅作独立参考；3333原参数不强行等同9999文献屏障值。轰炸最多目标与干扰最少目标、各自20/35秒初冷、31秒后续准备、4.17秒选点延迟、5秒效果间隔与结束条件分别说明；保留无目标时落自身格、斯第奇重生及波次释放条件，不猜固定站位。父刷新、来源丢失、恢复手选和地图所有权按现有模式处理。'
limits='当前四份普通或紧急配置均准确引用数据库级别0；级别1完整原文保留在技术详情，不借其40秒刷新冒充本关。 屏障值、技能准备、延迟、命中、地块覆盖及实际波次释放分别保留条件；不读取战斗、不标实际站位、不推断完整时钟。 只作局外资料查阅，不操作游戏、发送聊天或改变本局；P3/P2/P1仍未完成，识别最后。'
validation='本节实际必要检查30项、原生窗口唯一检查52项通过；到期完整可用范围已在第380节真实源码上重新执行并封口，627个完整有序选择器、95份P3原生范围及全部100个声明位置保持，实际根退出0。当前完整回执verification/full-380/summary.json，实际attempt2；离线6759项中6680项通过、73项历史或声明跳过，0失败0错误，16条不可用记录按6个父项单独保留。原30实遇符号链接WinError1314仍未通过，独立29保持分开；缺私样本、旧系统及实机游戏/聊天不计通过，不冒称完整工程或P3/P2/P1完成。全量首轮3600秒超时原件保存；只将该离线整轮预算改为5400秒后完整范围重跑，不能称性能提升。后处理旧格式误拒及新精确兼容封存的原件、独立审核和实际退出另见verification/full-380/postprocessing-schema-repair/closure.json。610条实际图片路径保持，239张新独立原图由四名真实审阅者逐张查看，其余仅按整字节和原审阅方式复用；图片不替代交互证明。下次395仅在用户明确恢复后适用，本批380完整发布核对后暂停，不启动381。原功能验收来源继续保留：本机30项必要检查和52项原生窗口唯一检查通过，真实退出与当前源码摘要一致。主代理逐张实际查看7张最终图，外观不替代交互证明；七类真实外部操作均零，隔离临时状态不作为本局或游戏验证。原项目测试窗正常更新可见响应，正常关闭启动区间私人五路径仅摘要核对保持，不复制或发布内容。新选择器追加且既有次序保持。365全量保留为历史来源，本轮实际完整回执另见下文。当前要求/索引实际验证，未变25索引测试复用；缺权限、私样本、实机游戏/聊天不冒称通过。按授权继续至380，完整当前小节和最终发布后暂停。4份准确关卡引用及8份分级完整原卡分别核对；80秒与40秒不混用，3333参数不充当9999屏障值或本局结果。首击、延迟、准备与选点范围分别说明；没有本局实测，不给实际时钟或位置。'
f=_verified_full380()
validation+=' 本节到期完整可用范围已按真正第380节来源重新验收，实际根退出0，全部'+str(f['actual_required_components'])+'个声明位置终止，'+str(f['native_supplements'])+'份P3原生范围保留；原52状态/4283完整核对与862断言、原30及独立29仍分开核验。完整回执verification/full-380/summary.json；图片外观审阅不替代交互。原30的符号链接权限结果按本轮真实原件记录，未取得范围仍未通过。365仅历史，不作为当前380来源；下一周期395仅待用户恢复后适用。'

nname='verification/sections/380-necessary-attempt1/process.json';wname='verification/sections/380-native-attempt1/actual/window.json';pname='verification/sections/380-native-attempt1/process.json'
n,w,p=map(read,(nname,wname,pname));m=read('verification/sections/380-main-window.json');a=read('verification/sections/380-source-audit.json');v=read('verification/sections/380-root-visual.json')
assert n['passed']and n['methods_ran']==30 and w['passed']and w['qpa']=='windows'and w['qt_exit_code']==0 and w['unique_checks']==52 and w['verification_window_closed']
assert len(w['same_identity_refresh_observations'])==2 and len(w['screenshots'])==7 and len(w['actual_readings'])==16 and all(x==0 for x in w['external_operation_attempts'].values())
assert p['passed']and p['window_receipt_sha256']==sha(wname)
for result in(n,w):
 assert result['source_sha256_before']==result['source_sha256_after']
 for name,h in result['source_sha256_after'].items():assert sha(name)==h,name
assert v['passed']and len(v['final_screenshot_reviews'])==7 and a['ordered_previous625_preserved']and len(a['current_selectors'])==627
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section380-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':380,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(nname),'methods_run':n['methods_ran'],'actual_exit':0},'native_windows_validation':{**pin(wname),'process':pin(pname),'unique_checks':w['unique_checks'],'actual_Qt_exit':0,'real_nonzero_refresh_states':2,'actual_MainWindow_entry_and_close_exercised':True,'all_seven_real_external_operations_zero':True},'root_visual_review':pin('verification/sections/380-root-visual.json'),'source_audit':pin('verification/sections/380-source-audit.json'),'original_project_window':pin('verification/sections/380-main-window.json'),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'full_suite_rerun':True,'last_full_receipt':'verification/full-380/summary.json','last_full_receipt_is_historical_for_this_changed_source':False,'last_full_validation_sha256':sha('verification/full-380/summary.json'),'next_periodic_full_section':395,'P3_complete':False,'P2_complete':False,'P1_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'execution_environment':'local_original_windows_project_venv','local_source_parity_required_for_cloud_publication':True}
f=_verified_full380();r['current_complete_available_full_validation']={'receipt':'verification/full-380/summary.json','sha256':sha('verification/full-380/summary.json'),'source_freeze':f['source_freeze'],'source_freeze_sha256':f['source_freeze_sha256'],'archive_manifests_sha256':f['archive_manifests_sha256'],'root_PNG_visual_review':f['root_PNG_visual_review'],'actual_validation_attempt':f['actual_validation_attempt']}
a.update(full380_historical_for_this_changed_source=False,current_full_is_historical_for_section=False,final_full_source_freeze=f['source_freeze'],current_full_receipt='verification/full-380/summary.json',current_full_summary_sha256=sha('verification/full-380/summary.json'),actual_full_validation_attempt=f['actual_validation_attempt'])
(ROOT/'verification/sections/380-source-audit.json').write_bytes(enc(a));r['source_audit']=pin('verification/sections/380-source-audit.json')
(ROOT/'verification/sections/380.json').write_bytes(enc(r));details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
old_wip=(ROOT/'WORK_IN_PROGRESS.md').read_bytes();(ROOT/'WORK_IN_PROGRESS.md').write_bytes(('## 第380节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述380为准。\n\n').replace('\n','\r\n').encode()+old_wip)
doc('PROJECT_COMPLETED.md','## 第380节 + '+title+'\n\n'+now+'。'+details+'\n\n'+(ROOT/'PROJECT_COMPLETED.md').read_text('utf8'))
s=(ROOT/'AGENTS.md').read_text('utf8');end=s.index('\n## 项目级最高优先要求');note='下一到期完整检查须给304/305两份full320验证脚本显式传入--source-freeze及当轮根声明冻结文件；默认320仅供历史绑定。350原失败与组合复验见verification/full-350/summary.json。312补充窗口采用既有120秒默认，304/305显式传入当轮source-freeze。'
doc('AGENTS.md','## 当前续接 · 第380节 + '+title+'\n\n'+details+'\n\n第380节为本批最后一节；普通推送及真实远端核对后暂停，不启动381。资料条件对照不替代本局实际状态、生成、生效或结算。通用页面不恢复独立版本栏目。用户当前授权继续至380，完整收尾后暂停。本节已完成到期完整可用范围；下一全量395仅待用户恢复，严格低于15%才开始当前完整小节收尾。\n\n'+note+'\n'+s[end:])
s=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');doc('PROJECT_REQUIREMENTS.md',s[:start]+'<!-- current-delivery:start -->\n## 第380节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:])
s=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8')
doc('PROJECT_PROGRESS.md',s)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==379 and cp['next_section']==380

if 380==371:
 cp['historical_before371_batch']={k:cp.get(k) for k in ('batch_start_section','batch_target_section','current_batch','batch_status')}
 cp['batch_start_section']=371;cp['batch_target_section']=380
 cp['current_batch']={'start':371,'end':380,'status':cp['batch_status'],'completed_sections':370,'next_section':371,'next_section_started':False,'batch_closed':False,'target_origin':'direct_user_request_2026-10-26_continue_to380','next_full_validation_after':380}
 cp['policy'].update(development_paused_by_latest_user_request=False,new_functional_sections_paused=False,stop_after_section=380,current_user_batch_target_section=380,batch_target_section=380,current_user_batch_completed=False,latest_user_instruction_receipt='verification/sections/371-preparation/resume-and-scope.json')
 cp['policy'].pop('paused_after_completed_section',None)

for key in('current_section_validation','latest_section_environment','cloud_publication_closeout'):
 if key in cp:cp['historical_before380_'+key]=cp.pop(key)
cp.update(completed_sections=380,latest_functional_section=380,next_section=381,batch_status='P3_SECTION380_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第380节 + '+title+'已本机必要验收；普通推送及真实远端核对后本批暂停，不启动381；下一周期395仅在用户恢复后适用。',full_validation_due=False)
cp['sections'].append({'number':380,'completion_ref':'p3-section-380','topic':title,'verification':'verification/sections/380.json'});cp['functional_sections_since_latest_requirement'].append(380)
cp['current_section_save']={'section':380,'verification':'verification/sections/380.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':380,'receipt':'verification/sections/380.json','methods_run':n['methods_ran'],'native_isolated_window_checks':w['unique_checks'],'real_nonzero_refresh_states':2,'full_suite_rerun':True,'last_full_receipt':'verification/full-380/summary.json','last_full_receipt_is_historical_for_current_changes':False}
cp['latest_section_environment']={'section':380,'receipt':'verification/sections/380.json','native_windows':validation,'native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-380/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=380,next_section=381,next_section_started=False,receipt='verification/sections/380.json',batch_closed=False)
cp['policy'].update(verification_execution_preference='local_project_environment',avoid_duplicate_cloud_tests=True)
u=read('verification/sections/380-usage.json');cp['policy'].update(current_usage_remaining_percent=u['remaining_percent'],current_usage_receipt='verification/sections/380-usage.json',usage_percent_available=True,usage_wrap_up_triggered=u['triggered'])
cp['current_data_versions'].update({'guest_material_manifest': '9d65a3e8a4bfbe18619e0e07d0709b9b0e8ff5b18e8ec369bfbb4341393f542c', 'guest_material_current_server_verified': False, 'guest_material_numeric_model_added': False})

f=_verified_full380()
cp['current_available_full_validation']={
 'section':380,'receipt':'verification/full-380/summary.json','available_scope_passed':True,
 'actual_validation_attempt':f['actual_validation_attempt'],
 'single_available_scope_execution_all_green':f['single_available_scope_execution_all_green'],
 'actual_root_controller_exit':f['actual_root_controller_exit'],
 'validation_composition':f['validation_composition'],
 'source_freeze':f['source_freeze'],'source_freeze_sha256':f['source_freeze_sha256'],
 'native_windows_game_chat_verified':False,
 'historical_for_current_changed_source':False,
 'current_worktree_validation_authority':True}
cp['last_full_validation']={'after_section':380,'receipt':'verification/full-380/summary.json',
 'available_checks_passed':True,'complete_repository_validation':False,'scope_not_reduced':True,
 'source_freeze':f['source_freeze'],'source_freeze_sha256':f['source_freeze_sha256'],
 'historical_for_current_changed_source':False}
cp['next_full_validation_after']=395
for key in ('validation_cadence','policy','current_batch','current_batch_commit_policy'):
 if isinstance(cp.get(key),dict):cp[key]['next_full_validation_after']=395
cp['current_batch']['next_full_validation_after']=395
cp['current_section_validation']['full_suite_rerun']=True
cp['latest_section_environment']['current_section_full_rerun']=True

cp['current_available_full_validation']['public_complete_proof']={'receipt':'verification/full-380/summary.json','sha256':sha('verification/full-380/summary.json'),'source_freeze':f['source_freeze'],'source_freeze_sha256':f['source_freeze_sha256'],'archive_manifests_sha256':f['archive_manifests_sha256'],'root_PNG_visual_review':f['root_PNG_visual_review'],'actual_validation_attempt':f['actual_validation_attempt']}
cp['last_full_validation']['public_complete_proof']=cp['current_available_full_validation']['public_complete_proof']
cp['current_section_validation']['last_full_receipt_is_historical_for_current_changes']=False
cp['latest_section_environment']['last_full_receipt_is_historical_for_current_changes']=False
cp['latest_section_environment']['current_section_full_rerun']=True
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section380-handoff:start -->\n## 第380节 + '+title+'\n\n'+details+'\n<!-- section380-handoff:end -->\n')
out=ROOT/'verification/sections/380-closeout';out.mkdir();shutil.copyfile(ROOT/'.cache/open_test_window_380.py',out/'execution-main-window.py')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':380,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next381_started':False,'at_Beijing':now}))
print(json.dumps({'section':380,'local_accepted':True,'ordinary_publication_pending':True},ensure_ascii=False))
