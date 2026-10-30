from pathlib import Path
from hashlib import sha256
import json,re,subprocess,sys,shutil,difflib,runpy,time
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];B=R/'verification/maintenance/node-card-review-20261031'
def read(n):return json.loads((R/n).read_bytes())
def pin(n):
 p=R/n;raw=p.read_bytes();return {'path':p.relative_to(R).as_posix(),'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
def write(n,v):(R/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
def text(n,value):
 p=R/n;old=p.read_bytes().decode('utf8').splitlines(keepends=True);new=value.splitlines(keepends=True);out=list(new)
 for a,b,num in difflib.SequenceMatcher(None,[s.rstrip('\r\n')for s in old],[s.rstrip('\r\n')for s in new],autojunk=False).get_matching_blocks():
  for i in range(num):out[b+i]=old[a+i]
 p.write_bytes(''.join(out).encode('utf8'))
prefix=B.relative_to(R).as_posix()+'/'
intermediate=B/'intermediate-before-cache-guards';intermediate.mkdir(exist_ok=False)
for name in ('summary.json','review-source.json','tests-reconciled.json','image-review.json'):
 shutil.copyfile(B/name,intermediate/name)
source=read(prefix+'review-source.json');changed=[r['path']for r in source['changed_source']]
source['changed_source']=[pin(n)for n in changed]
source.pop('fetch_parser_and_validation_AST_unchanged')
source['fetch_and_parser_AST_unchanged']=True
source['validation_change']='Only explicit top-level and metadata dictionary guards; unchanged valid-schema rules. Reject null/non-object cache/update before startup or replacement.'
write(prefix+'review-source.json',source)
sets=[]
for folder,num in [('tests',132),('tests-final',10),('tests-boundary',17),('tests-final-boundary',17)]:
 result=read(prefix+folder+'/results.json');assert result['passed']and result['tests_run']==num and not result['forbidden_external_calls']
 assert read(prefix+folder+'/process.json')['actual_observed_exit']==0
 ids=set(re.findall(r'^test_\w+ \(([^)]+)\)',(B/folder/'stderr.txt').read_text('utf8'),re.M));assert len(ids)==num
 sets.append(ids)
assert all(s<=sets[0]for s in sets[1:])
write(prefix+'tests-reconciled.json',{'unique_available_passed':132,'initial_passed':132,'initial_ids':sorted(sets[0]),'final_focused_passed':17,'final_ids':sorted(sets[-1]),'final_rechecked_subset_of_initial':True,'other_115_reused':True,
 'final_change_scope':'Top-level and metadata non-object cache/update rejection, including null, list, boolean, number and string. Final 17 related checks and 60 native checks rerun; other unchanged related scopes reused, not 166 unique tests.',
 'failures_remaining':0,'unavailable_in_selected_scope':0})
comparison=read(prefix+'before-after-final.json');assert comparison['all_public_rows_exactly_equal']and comparison['full_domain_results_equal']
for n,v in comparison['source'].items():assert v['current_sha256']==pin(n)['sha256']
native=read(prefix+'native-final-boundary/window.json');assert native['passed']and native['unique_checks']==60 and not any(native['external_operation_attempts'].values())
assert read(prefix+'native-final-boundary/process.json')['actual_observed_exit']==0
assert all(native['source_sha256_after'][n]==pin(n)['sha256']for n in changed)
shots=[]
for p in sorted((B/'native-final-boundary').glob('*.png')):
 old=B/'native-current'/p.name;assert p.read_bytes()==old.read_bytes()
 shots.append({'image':pin(p.relative_to(R)),'exact_whole_bytes_equal_to':pin(old.relative_to(R)),'review_method':'reuse prior actual per-image review through exact whole-byte equality','diagnostic_not_visibility_proof':p.name=='node-hover.png'})
assert len(shots)==7
old=read(prefix+'image-review.json');old['final_images']=shots;old['final_valid_data_visuals_unchanged_by_cache_guards']=True;write(prefix+'image-review.json',old)
live=read(prefix+'live-window-complete/window.json');assert live['passed']and live['private_six_paths_unchanged']
assert all(live['source_sha256_after'][n]==pin(n)['sha256']for n in changed)
import ctypes,win32gui,win32process
for w in live['owned_windows']:assert win32gui.IsWindowVisible(w['hwnd'])and win32process.GetWindowThreadProcessId(w['hwnd'])[1]==w['pid']and not ctypes.windll.user32.IsHungAppWindow(w['hwnd'])
a=read('.cache/runtime-node-source-complete-live-status.json');time.sleep(2.2);b=read('.cache/runtime-node-source-complete-live-status.json');assert b['toolbar_visible']and b['elapsed_since_launch']>a['elapsed_since_launch']
write(prefix+'live-window-complete/desktop-review.json',{'reviewer':'/root','actual_windows_mcp_snapshot_called':True,'actual_image_viewed':True,'region':[1716,1164,2130,1218],'Qt_timer_advanced':True,'owned_window_visible_and_responding':True,'private_six_paths_unchanged_during_startup':True,'private_contents_or_hashes_published':False,'game_operated':False,'chat_sent':False})
summary=read(prefix+'summary.json');summary.update(source_review=pin(prefix+'review-source.json'),related_receipt=pin(prefix+'tests-reconciled.json'),native_receipt=pin(prefix+'native-final-boundary/window.json'),comparison=pin(prefix+'before-after-final.json'),image_review=pin(prefix+'image-review.json'),runtime=pin(prefix+'live-window-complete/desktop-review.json'))
summary['final_cache_boundary_rechecked']=True;summary['final_related_subset_passed']=17
summary['comparison_tool_fixture_correction']={'observed_tool_chunk':'102d7f','exit':1,'cause':'Comparison helper addressed second Assign AST node as If; corrected statement index, no product failure.','corrected_comparison':'before-after-final.json'}
write(prefix+'summary.json',summary)
note='收尾继续发现并修正JSON空值及错误元数据类型导致启动异常或覆盖旧统计的边界；最终17项相关检查及原生60项在最终源码重跑通过，其余115项源码未变范围复用，不累计重叠。此前中间回执保留，最终回执绑定最终源码；原有获取/解析不变，合法数据规则不变，仅加入对象类型核对。'
for n in('WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md'):
 t=(R/n).read_text('utf8');needle='<!-- node-card-review-20261031:end -->';assert t.count(needle)==1;t=t.replace(needle,note+'\n'+needle);text(n,t)
n='research/node-card-review-20261031/README.md';t=(R/n).read_text('utf8');t+='\n## 最终缓存边界复核\n\n'+note+'\n\n最终606查询与15组目录对照仍一致，详见 `before-after-final.json`。首次最终比较脚本把AST赋值语句误当条件语句，已修正比较脚本；不是产品失败。正常更新最终实际测试窗时六处私人路径保持，未恢复旧局。\n';text(n,t)
cp=read('DEVELOPMENT_CHECKPOINT.json');cp['current_maintenance_save']['status']='partial_program_review_shared_public_source_history_and_cache_boundaries_checked'
text('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n')
m=runpy.run_path(str(R/'scripts/update_cloud_index.py'));m['update'](R);assert m['validate_delivery'](R,cp)['current_section']==440
(B/'finalize-source.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({'passed':True,'unique_related':132,'final_subset':17,'native':60,'goal_complete':False}))
