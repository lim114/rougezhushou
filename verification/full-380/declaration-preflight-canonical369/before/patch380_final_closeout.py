"""Adapt generated380 cache closeout only after a real complete380 summary exists.

No test, window, index, document, source, Git commit/push or pause is performed by
this adapter. The generated closeout later rechecks the actual full proof before
writing public records; metadata pause follows a genuine functional publication.
"""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import argparse,ast,json,re
R=Path(__file__).resolve().parents[1]

GUARD='''
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

'''

def require(value,message):
    if not value:raise ValueError(message)
def change_one(text,old,new):
    require(text.count(old)==1,'Expected exactly one generated380 anchor: '+repr(old));return text.replace(old,new)
def insert_guard(text):
    require('def _verified_full380('not in text,'Never apply380 adapter twice')
    nodes=[node for node in ast.parse(text).body if isinstance(node,ast.Assign)
           and any(isinstance(t,ast.Name)and t.id=='ROOT'for t in node.targets)]
    require(len(nodes)==1,'Generated unique root binding required')
    # Several existing wrappers keep OUT on the same physical ROOT line.
    # Insert after that whole line; never leave a leading semicolon behind.
    lines=text.splitlines(keepends=True);lines[nodes[0].end_lineno:nodes[0].end_lineno]=['\n'+GUARD+'\n']
    return ''.join(lines)
def proof_bindings_expr():
    return "{'receipt':'verification/full-380/summary.json','sha256':sha('verification/full-380/summary.json'),'source_freeze':f['source_freeze'],'source_freeze_sha256':f['source_freeze_sha256'],'archive_manifests_sha256':f['archive_manifests_sha256'],'root_PNG_visual_review':f['root_PNG_visual_review'],'actual_validation_attempt':f['actual_validation_attempt']}"

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--apply',action='store_true');args=parser.parse_args()
    # Execute only this read-only proof guard, not a candidate pipeline or tests.
    api={'ROOT':R};exec(compile(GUARD,'<actual full380 proof only>','exec'),api);full=api['_verified_full380']()
    require(full['after_section']==380,'Actual380 proof required; never substitute365')
    names=('close380.py','finalize380.py','publish380.py','metadata380.py','open_test_window_380.py')
    inputs={name:(R/'.cache'/name).read_text('utf8')for name in names};outputs={}
    for name,source in inputs.items():
        text=insert_guard(source)
        text=text.replace('verification/full-365/summary.json','verification/full-380/summary.json')
        if name=='close380.py':
            text=text.replace("'full_suite_rerun':False","'full_suite_rerun':True")
            text=text.replace("'last_full_receipt_is_historical_for_this_changed_source':True","'last_full_receipt_is_historical_for_this_changed_source':False")
            text=text.replace("'last_full_receipt_is_historical_for_current_changes':True","'last_full_receipt_is_historical_for_current_changes':False")
            text=text.replace("'historical_for_current_changed_source':True","'historical_for_current_changed_source':False")
            text=text.replace("'current_worktree_validation_authority':not True","'current_worktree_validation_authority':True")
            text=text.replace("'section':365,'receipt':'verification/full-380/summary.json'","'section':380,'receipt':'verification/full-380/summary.json'")
            text=text.replace("'after_section':365,'receipt':'verification/full-380/summary.json'","'after_section':380,'receipt':'verification/full-380/summary.json'")
            text=text.replace("'next_periodic_full_section':380","'next_periodic_full_section':395")
            text=text.replace("cp['next_full_validation_after']=380","cp['next_full_validation_after']=395")
            text=text.replace("cp[key]['next_full_validation_after']=380","cp[key]['next_full_validation_after']=395")
            text=text.replace("cp['current_batch']['next_full_validation_after']=380","cp['current_batch']['next_full_validation_after']=395")
            text=text.replace("cp['current_section_validation']['full_suite_rerun']=not True","cp['current_section_validation']['full_suite_rerun']=True")
            text=text.replace("cp['latest_section_environment']['current_section_full_rerun']=not True","cp['latest_section_environment']['current_section_full_rerun']=True")
            text=change_one(text,"f=read('verification/full-380/summary.json');assert f['available_checks_passed']and f['scope_not_reduced']","f=_verified_full380()")
            match=re.search(r'^validation=.*$',text,re.M);require(match is not None,'Generated validation prose required')
            addition="\nf=_verified_full380()\nvalidation+=' 本节到期完整可用范围已按真正第380节来源重新验收，实际根退出0，全部'+str(f['actual_required_components'])+'个声明位置终止，'+str(f['native_supplements'])+'份P3原生范围保留；原52状态/4283完整核对与862断言、原30及独立29仍分开核验。完整回执verification/full-380/summary.json；图片外观审阅不替代交互。原30的符号链接权限结果按本轮真实原件记录，未取得范围仍未通过。365仅历史，不作为当前380来源；下一周期395仅待用户恢复后适用。'\n"
            text=text[:match.end()]+addition+text[match.end():]
            line="(ROOT/'verification/sections/380.json').write_bytes(enc(r))"
            binding="f=_verified_full380();r['current_complete_available_full_validation']="+proof_bindings_expr()+"\n"
            audit="a.update(full380_historical_for_this_changed_source=False,current_full_is_historical_for_section=False,final_full_source_freeze=f['source_freeze'],current_full_receipt='verification/full-380/summary.json',current_full_summary_sha256=sha('verification/full-380/summary.json'),actual_full_validation_attempt=f['actual_validation_attempt'])\n(ROOT/'verification/sections/380-source-audit.json').write_bytes(enc(a));r['source_audit']=pin('verification/sections/380-source-audit.json')\n"
            text=change_one(text,line,binding+audit+line)
            anchor="(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))"
            extra="cp['current_available_full_validation']['public_complete_proof']="+proof_bindings_expr()+"\ncp['last_full_validation']['public_complete_proof']=cp['current_available_full_validation']['public_complete_proof']\ncp['current_section_validation']['last_full_receipt_is_historical_for_current_changes']=False\ncp['latest_section_environment']['last_full_receipt_is_historical_for_current_changes']=False\ncp['latest_section_environment']['current_section_full_rerun']=True\n"
            text=change_one(text,anchor,extra+anchor)
            text=text.replace('继续P3；381从实际剩余节点/事件条件、掉落和固定地图缺口接续，未启动。','第380节为本批最后一节；普通推送及真实远端核对后暂停，不启动381。')
            text=text.replace('普通推送核对后381接续P3实际剩余缺口，未启动。下次380。','普通推送及真实远端核对后本批暂停，不启动381；下一周期395仅在用户恢复后适用。')
            text=text.replace('只跑本机必要检查；下一全量380','本节已完成到期完整可用范围；下一全量395仅待用户恢复')
        elif name=='finalize380.py':
            text=text.replace("'full_validation_rerun':False","'full_validation_rerun':True")
            anchor='allowed.extend(p.relative_to(ROOT).as_posix()for p in'
            require(text.count(anchor)==1,'Generated380 explicit allowlist required')
            text=text.replace(anchor,"allowed.append('verification/full-380')\n"+anchor)
            marker="module=runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))"
            require(text.count(marker)==1,'Existing index actual validation must remain')
            text=text.replace(marker,"f=_verified_full380()\n"+marker)
        elif name=='publish380.py':
            text=text.replace("r['full_suite_rerun']is False","r['full_suite_rerun']is True")
            text=text.replace("'full_validation_rerun':False","'full_validation_rerun':True")
            text=text.replace("'last_full_is_historical_for_current_changes':True","'last_full_is_historical_for_current_changes':False")
            anchor="assert cp['policy']['new_functional_sections_paused']is False and cp['policy']['stop_after_section']==380"
            text=change_one(text,anchor,"assert cp['policy']['new_functional_sections_paused']is (phase=='metadata') and cp['policy']['stop_after_section']==380\nf=_verified_full380()\nassert r['current_complete_available_full_validation']['sha256']==sha('verification/full-380/summary.json')")
        elif name=='metadata380.py':
            anchor="assert cp['policy']['new_functional_sections_paused']is False and cp['policy']['stop_after_section']==380"
            extra="\nf=_verified_full380()\ncp['policy'].update(new_functional_sections_paused=True,development_paused_by_latest_user_request=True,paused_after_completed_section=380,current_user_batch_completed=True)\ncp['batch_status']='P3_SECTION380_PUBLISHED_PAUSED'\ncp['current_batch'].update(status=cp['batch_status'],batch_closed=True,paused_after_section=380,next_section=381,next_section_started=False)\n"
            text=change_one(text,anchor,anchor+extra)
            text=re.sub(r"^cp\['next_action'\]=.*$","cp['next_action']='第380节功能、到期完整可用范围及当前要求/索引已普通推送核对；按用户要求本批暂停，不启动381。P3/P2/P1仍未完成；下一周期395仅待用户明确恢复后适用。'",text,flags=re.M)
            text=text.replace("'development_paused':False","'development_paused':True")
            text=text.replace('后续381尚未启动；按本次授权继续至380并完整收尾后暂停，下一定期全量380。','本批已在380完整收尾并暂停，不启动381；下一周期395仅待用户恢复后适用。')
        elif name=='open_test_window_380.py':
            text=text.replace("'full_validation_this_changed_source_rerun':False","'full_validation_this_changed_source_rerun':True")
            text=text.replace("'historical_full_receipt':'verification/full-380/summary.json'","'current_full_receipt':'verification/full-380/summary.json'")
            # The real wrapper has import path setup before ROOT. Only the
            # source guard definition is inserted there; verify after ROOT and
            # that definition, before reading state or touching normal windows.
            text=change_one(text,GUARD,GUARD+'\n_verified_full380()\n')
        ast.parse(text);outputs[name]=text
    for name,text in outputs.items():
        require('verification/full-365/summary.json'not in text,'Obsolete current365 pointer in generated380 '+name)
    report={'kind':'CACHE380_FINAL_FULL_PUBLICATION_AND_PAUSE_ADAPTATION','at_utc':datetime.now(timezone.utc).isoformat(),
        'actual_full380_summary_sha256':sha256((R/'verification/full-380/summary.json').read_bytes()).hexdigest(),
        'actual_freeze':full['source_freeze'],'actual_archive_manifests':full['archive_manifests_sha256'],
        'actual_root_visual':full['root_PNG_visual_review'],'cache_only':True,'formal_tree_modified':False,'tests_or_windows_started':False,
        'pause_executed':False,'no381_started':True,'applied':args.apply,
        'before':{n:sha256(t.encode()).hexdigest()for n,t in inputs.items()},'after':{n:sha256(t.encode()).hexdigest()for n,t in outputs.items()},
        'index_validation_and_ordinary_remote_verification_preserved':True,'next_full_only_after_resume':395}
    if args.apply:
        backup=R/'.cache/full380-before-final-closeout-adaptation';backup.mkdir(exist_ok=False)
        for name,text in inputs.items():(backup/name).write_text(text,encoding='utf8',newline='\n')
        for name,text in outputs.items():(R/'.cache'/name).write_text(text,encoding='utf8',newline='\n')
        (R/'.cache/full380-final-closeout-adaptation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
