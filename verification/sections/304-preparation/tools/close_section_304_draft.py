"""Root-only closeout draft. No tests, Qt, Git, game or private-state reads.
Dry-run prepares staged bytes; --apply rechecks every input and uses the existing
index updater. Inputs are public actual receipts, not invented success flags.
"""
import argparse
from copy import deepcopy
from datetime import datetime, timezone, timedelta
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'.cache/p3-304-closeout'
TITLE='命运所指五项选择的标记、节点变化、暂离再访与固定决战资料'
CAPABILITY=('好奇心与死、窥视箱中共五项完整资料选择分别解释50源石锭标记、未具名收藏品、'
'同节点转为混沌源阶理论、变化后无法离开及仅对作战节点生效的效果例外、暂离后再访和决战。'
'取得至少一个沙盘后的第五层3个命运所指与双沙盘自动标记分开；默认未选，手选只读，'
'两个相关选择可手动打开既有固定作战。来源或范围失效清旧资料，同范围刷新保留阅读。')
LIMITS=('固定社区版本及原参数不等于当前服务器；两条同文保护证据原选项仍保留歧义，'
'实际选择、50锭支付、领取、节点身份/标记/转换/再访及完整入口脚本未知；'
'不改本局或计算，不提供路线推荐；25场景/57选项、10附注和17条typed奖励统计不因本节减少。')
DOCS=('PROJECT_COMPLETED.md','WORK_IN_PROGRESS.md','AGENTS.md','PROJECT_REQUIREMENTS.md',
      'PROJECT_PROGRESS.md','DEVELOPMENT_CHECKPOINT.json','CLOUD_INDEX.json','CLOUD_HANDOFF.md')
CHOICES={('community_group_030','community_group_030:scene:0','community_group_030:scene:0:choice:0'),
('community_group_030','community_group_030:scene:0','community_group_030:scene:0:choice:1'),
('community_group_031','community_group_031:scene:0','community_group_031:scene:0:choice:0'),
('community_group_031','community_group_031:scene:0','community_group_031:scene:0:choice:1'),
('community_group_031','community_group_031:scene:2','community_group_031:scene:2:choice:0')}

def need(value,message):
    if not value:raise ValueError(message)
def digest(raw):return sha256(raw).hexdigest()
def public(name):
    q=Path(name);q=q if q.is_absolute() else ROOT/q
    need(q.resolve().is_relative_to(ROOT.resolve()),'Input outside project: '+str(name))
    need(q.is_file(),'Missing input: '+str(name));return q

def read(name):return json.loads(public(name).read_text(encoding='utf8'))
def relative(name):return public(name).relative_to(ROOT).as_posix()
def pin(name):
    q=public(name);b=q.read_bytes();return {'file':q.relative_to(ROOT).as_posix(),'sha256':digest(b),'bytes':len(b)}
def jbytes(data):return (json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def front(text,title,body):return '## '+title+'\n\n'+body+'\n\n'+text

def source_guard(record):
    before=record['source_sha256_before'];after=record['source_sha256_after']
    need(type(before)is dict and before and before==after,'Actual source before/after differ')
    for name,h in before.items():need(pin(name)['sha256']==h,'Current source differs: '+name)
    return before

def prepare(a):
    n=read(a.necessary);proc=read(a.window_process);w=read(a.window);main=read(a.main_review);visual=read(a.png_review)
    need(n['section']==304 and n['passed']is True and type(n['exit_code'])is int and n['exit_code']==0,'Necessary actual result not passed/0')
    need(type(n['methods_ran'])is int and n['methods_ran']>0 and n['full_validation_rerun']is False,'Invalid necessary count/scope')
    ns=source_guard(n)
    need(proc['section']==304 and proc['status']=='completed' and type(proc['exit_code'])is int and proc['exit_code']==0
         and type(proc['child_primary_exit'])is int and proc['child_primary_exit']==0 and proc['window_receipt_passed']is True
         and proc['timed_out']is False and proc['owned_job_no_live_execution_verified']is True,'Native process actual result not completed/0/clean')
    ps=source_guard(proc);need(proc['source_before_after_unchanged']is True,'Native controller source changed')
    need(proc['window_receipt_sha256']==pin(a.window)['sha256'],'Controller not bound to exact native receipt')
    need(w['section']==304 and w['passed']is True and w['failure']is None and w['qpa']=='windows'
         and type(w['qt_exit_code'])is int and w['qt_exit_code']==0 and w['verification_window_closed']is True,'Native receipt not actual passed Windows/0')
    ws=source_guard(w);need(all(ns[k]==h for k,h in ws.items()if k in ns),'Necessary/native shared source mismatch')
    need(all(ps[k]==h for k,h in ws.items()if k in ps),'Controller/native source mismatch')
    need(type(w['unique_checks'])is int and w['unique_checks']>0 and len(w['checks'])==len(set(w['checks']))==w['unique_checks'],'Native unique-check ledger inconsistent')
    rows=w['actual_choice_readings'];actual={(x['event_id'],x['scene_key'],x['choice_key'])for x in rows}
    need(len(rows)==5 and actual==CHOICES,'Five exact complete choice tuples not read')
    expected_ids={key:ids for key,ids in zip(sorted(CHOICES), [('choice_ro6_end1_1',),('choice_ro6_end1_2',),('choice_ro6_end2_1','choice_ro6_end2_4'),('choice_ro6_end2_2',),('choice_ro6_end2_3',)])}
    need(all(tuple(x['original_choice_ids'])==expected_ids[(x['event_id'],x['scene_key'],x['choice_key'])] for x in rows),'Native original-choice candidates changed')
    need(all(x['reference_id']==x['choice_key'] and x['all_actual_fields_unknown']is True and x['run_state_updated']is False for x in rows),'Native semantic boundary violated')
    need(w['private_state_read_copied_or_restored']is False and w['game_operated']is False and w['game_captures']==0
         and w['chat_sent']is False and w['chat_attempted']is False,'Native external/private boundary violated')
    need(w['actual_node_marker_transformation_revisit_or_inventory_verified']is False,'Native wrongly claims real game verification')
    need(main['section']==304 and main['passed']is True and type(main['actual_exit'])is int and main['actual_exit']==0
         and main['window_visible_and_responsive']is True and main['private_state_five_paths_unchanged']is True,'Root original-window/private5 review incomplete')
    if 'original_receipt' in main:need(pin(main['original_receipt'])['sha256']==main['original_receipt_sha256'],'Root main review original receipt changed')
    need(visual['section']==304 and visual['reviewer']=='root' and visual['all_reviewed']is True,'Root visual review incomplete')
    shots=w['screenshots'];need(len(shots)==w['screenshot_count'] and len(shots)>=5,'Native screenshots incomplete')
    reviewed={x['sha256']:x for x in visual['images']if x.get('reviewed')is True}
    for shot in shots:
        h=shot['sha256'];need(h in reviewed,'Native PNG not root reviewed: '+shot['name'])
        need(pin(reviewed[h]['file'])['sha256']==h,'Reviewed PNG actual bytes changed')
    cp=read('DEVELOPMENT_CHECKPOINT.json');need(cp['completed_sections']==303 and cp['next_section']==304,'Checkpoint not at original303')
    need(cp['policy']['wrap_up_below_usage_percent']==5,'Current usage5 rule changed')
    need(cp['last_verified_cloud_save']['section']==303,'Previous actual publication must stay303')
    need(pin(cp['last_verified_cloud_save']['proof'])['sha256']==cp['last_verified_cloud_save']['proof_sha256'],'303 proof bytes changed')
    need(cp['last_full_validation']['receipt']=='verification/full-290/summary.json','Last full must remain290')
    need(cp['next_full_validation_after']==cp['policy']['next_full_validation_after']==cp['current_batch_commit_policy']['next_full_validation_after']==305,'305 cadence mismatch')
    need(re.fullmatch('[0-9a-f]{40}',a.prior_commit),'Use root actual prior HEAD40')
    guards={x:pin(x)for x in DOCS}
    inputs={x:pin(x)for x in (a.necessary,a.window_process,a.window,a.main_review,a.png_review,*a.failed_process)}
    failed=[]
    for name in a.failed_process:
        f=read(name);need(f['section']==304 and f['exit_code']!=0,'Declared failure history is not a failed304 receipt');failed.append(pin(name))
    now=datetime.now(timezone(timedelta(hours=8))).isoformat()
    details=f'{CAPABILITY}\n\n实际{n["methods_ran"]}必要检查、原生{w["unique_checks"]}个唯一检查通过；{len(shots)}张实际PNG由根代理查看。原项目窗口更新可见响应、私人5路径未变。{LIMITS} '
    details+='来源及实际回执verification/sections/304.json；290完整范围沿用原来源，本节未跑全量；后续305且到期全量305，无数字终点。当前为本地验收完成、普通推送尚待核对。'
    receipt={'section':304,'kind':'functional_section','title':TITLE,'at_Beijing':now,'branch':'codex/p2-development','prior_commit':a.prior_commit,
      'remaining_item':'P3节点事件与动态节点状态文献规则','new_capability':CAPABILITY,'files':sorted(set(ns)|set(ws)),
      'source_sha256':ns,'validated_source_sha256':ws,'necessary_validation':{'receipt':relative(a.necessary),**pin(a.necessary),'actual_exit':n['exit_code'],'methods_run':n['methods_ran'],'source_unchanged':True},
      'native_windows_validation':{'process':pin(a.window_process),'receipt':pin(a.window),'actual_Qt_exit':w['qt_exit_code'],'unique_checks':w['unique_checks'],
       'actual_assertion_executions':w['successful_assertion_executions_including_repeated_guards'],'five_exact_choice_readings':rows,'screenshots':shots,'root_visual_review':pin(a.png_review),'original_project_window':pin(a.main_review)},
      'necessary_attempt_history':[], 'native_attempt_history':failed,'original_entry_gaps_unchanged':[25,57],'unparsed_notes_unchanged':10,'typed_named_grant_count_unchanged':17,
      'actual_server_generation_or_inventory_verified':False,'full_validation':{'receipt':'verification/full-290/summary.json',**pin('verification/full-290/summary.json'),'after_section':290,'full_suite_rerun':False,'next_periodic_section':305,'scope_not_reduced':True,'new304_source_full_validation_claimed':False},
      'limits':[LIMITS],'next_section':305,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'P3_complete':False,'P2_complete':False}
    staged={'verification/sections/304.json':jbytes(receipt)}
    text={name:public(name).read_text(encoding='utf8')for name in DOCS if name.endswith('.md')}
    for name in ('PROJECT_COMPLETED.md','WORK_IN_PROGRESS.md'):
        staged[name]=front(text[name],'功能第304节 · '+TITLE,now+'。'+details).encode('utf8')
    for name in ('AGENTS.md','PROJECT_REQUIREMENTS.md'):
        staged[name]=front(text[name],'当前续接 · 第304节已完成功能与必要/原生验收',details).encode('utf8')
    progress=text['PROJECT_PROGRESS.md'];old='同步完成标志、住民/迷雾、行动力与加工品的节点状态规则'
    new='同步完成标志、住民/迷雾、行动力与加工品的节点状态规则，以及已解释的命运所指文献规则在真实本局中的标记、转换与再访状态'
    need(progress.count(old)==1,'Todo exact remaining fragment missing/ambiguous');staged['PROJECT_PROGRESS.md']=progress.replace(old,new,1).encode('utf8')
    cp=deepcopy(cp)
    for key in ('current_section_validation','latest_section_environment','cloud_publication_closeout','active_section'):
        if key in cp:cp['historical_before304_'+key]=cp.pop(key)
    cp['completed_sections']=304;cp['next_section']=305;cp['batch_status']='P3_SECTION304_LOCAL_ACCEPTED_PUBLICATION_PENDING'
    cp['sections'].append({'number':304,'completion_ref':'p3-section-304','topic':TITLE,'verification':'verification/sections/304.json'})
    cp['last_verified_cloud_save']['scope']='previous_functional_section'
    cp['current_section_save']={'section':304,'verification':'verification/sections/304.json','scope':'current_functional_section','binding':'enclosing_commit','commit_reference':'commit containing304 actual sources/acceptance/requirements/index; ordinary publication pending'}
    cp['current_section_validation']={'section':304,'receipt':'verification/sections/304.json','necessary_methods_passed':n['methods_ran'],'native_isolated_window_checks':w['unique_checks'],'full_suite_rerun':False,'last_full_receipt':'verification/full-290/summary.json','full_source_is_historical290':True}
    cp['latest_section_environment']={'section':304,'receipt':'verification/sections/304.json','native_windows':f'{n["methods_ran"]} necessary; {w["unique_checks"]} unique native; root PNG review and original window/private5 unchanged','native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-290/summary.json'}
    cp['current_batch'].update(status=cp['batch_status'],next_section=305,next_section_started=False,receipt='verification/sections/304.json')
    cp['functional_sections_since_latest_requirement'].append(304)
    staged['DEVELOPMENT_CHECKPOINT.json']=jbytes(cp)
    index=read('CLOUD_INDEX.json');index.update(completed_sections=304,next_section=305,batch_status=cp['batch_status'],sections=cp['sections'])
    index['requirements']['sha256']=digest(staged['PROJECT_REQUIREMENTS.md']);staged['CLOUD_INDEX.json']=jbytes(index)
    handoff=text['CLOUD_HANDOFF.md'];a0=handoff.index('<!-- live-cloud-index:start -->');b0=handoff.index('<!-- live-cloud-index:end -->')+len('<!-- live-cloud-index:end -->')
    banner='<!-- live-cloud-index:start -->\n# 当前云端续接索引 · 第304节\n\n'+details+'\n\n当前源码/验收随 enclosing commit 保存；303远端发布证明作为previous保留；304普通推送与实际远端核对未完成。P3 → P2 → P1，识别最后；下次定期全量305，原290全量不重写。\n<!-- live-cloud-index:end -->'
    staged['CLOUD_HANDOFF.md']=(handoff[:a0]+banner+handoff[b0:]).encode('utf8')
    for name,raw in staged.items():q=OUT/'staged'/name;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(raw)
    plan={'section':304,'kind':'root_only_actual_acceptance_closeout_draft','guarded_live_inputs':{**guards,**inputs},'staged_outputs':{k:{'sha256':digest(v),'bytes':len(v)}for k,v in staged.items()},'ordinary_push_or_remote_verified':False,'index_final_regeneration_required_on_apply':True}
    (OUT/'plan.json').write_bytes(jbytes(plan));print(json.dumps({'ready_draft':True,'necessary':n['methods_ran'],'native':w['unique_checks'],'outputs':len(staged),'apply':a.apply},ensure_ascii=False))
    if a.apply:
        for name,p in plan['guarded_live_inputs'].items():need(pin(name)==p,'Input changed before apply: '+name)
        before={name:(ROOT/name).read_bytes()if(ROOT/name).exists()else None for name in staged}
        try:
            for name,raw in staged.items():(ROOT/name).write_bytes(raw)
            spec=importlib.util.spec_from_file_location('existing_index_updater',ROOT/'scripts/update_cloud_index.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.update(ROOT)
        except BaseException:
            for name,raw in before.items():
                if raw is None:(ROOT/name).unlink(missing_ok=True)
                else:(ROOT/name).write_bytes(raw)
            raise
        (OUT/'apply-receipt.json').write_bytes(jbytes({'section':304,'applied':True,'outputs':{name:pin(name)for name in staged},'tests_Qt_Git_private_reads':False,'cloud_publication_verified':False}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--necessary',required=True);p.add_argument('--window-process',required=True);p.add_argument('--window',required=True)
    p.add_argument('--main-review',required=True);p.add_argument('--png-review',required=True);p.add_argument('--prior-commit',required=True)
    p.add_argument('--failed-process',action='append',default=[]);p.add_argument('--apply',action='store_true');prepare(p.parse_args())
