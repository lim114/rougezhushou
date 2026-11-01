from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,runpy,difflib,sys,ctypes
R=Path.cwd();B=R/'verification/maintenance/player-copy-20261102'
sys.path[:0]=[str(R),str(R/'.cache/305-window-tooldeps')]
def read(p):return json.loads((R/p).read_bytes())
def pin(p):
 raw=(R/p).read_bytes();return {'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
def write(p,x):(R/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf8')
def save(p,s):
 p=R/p;old=p.read_bytes().decode('utf8').splitlines(keepends=True)if p.exists()else[];new=s.splitlines(keepends=True)
 for x,y,k in difflib.SequenceMatcher(None,[v.rstrip('\r\n')for v in old],[v.rstrip('\r\n')for v in new],autojunk=False).get_matching_blocks():new[y:y+k]=old[x:x+k]
 p.write_bytes(''.join(new).encode('utf8'))
u=read(B/'final/results.json');proc=read(B/'final/process.json')
assert u['passed']and u['tests_run']==55 and not(u['failed']or u['errors']or u['skipped']or u['forbidden_external_calls'])and proc['actual_observed_exit']==0 and proc['tested_source_unchanged']
for p,h in read(B/'final/source-before.json').items():assert pin(p)['sha256']==h,p
private=read('.cache/viewport459-private-before.json');assert all((sha256((R/p).read_bytes()).hexdigest()if(R/p).is_file()else None)==h for p,h in private.items())
import win32gui,win32process
status=read('.cache/readable459-live-status.json');hwnd=status['native_host'];assert status['toolbar_visible']and status['main_reference_visible']and win32gui.IsWindowVisible(hwnd)and not ctypes.windll.user32.IsHungAppWindow(hwnd)
live=read(B/'live-window/window.json');assert live['private_six_paths_unchanged'];live.update(desktop_visual_review_pending=False,desktop_visual_review={'tool':'Windows-mcp Screenshot','observed':'Updated native map and compact toolbar visible and responsive.','private_screenshot_published':False});write(B/'live-window/window.json',live)
sources=['rouge/player_game_map.py','rouge/player_inventory.py','rouge/player_map_hover.py','rouge/player_recent_scene.py','rouge/player_shop_memory.py','tests/test_shop_prices_443.py']
write(B/'source-review.json',{'section':459,'kind':'implementation_maintenance','changed_or_new_sources':{p:pin(p)for p in sources},'review':'Copy-only simplification on inventory, stored shop reads, recent event excerpts, node hover and game-map annotation. Replace repetitive negative caveats with source/status labels. Keep game conditions, data qualification, read-vs-held attribution, history/source actions and price comparisons. Existing tests keep record immutability, deduplication, selected earlier price, held-state and source behavior checks.','new_logic_or_dependency':False,'functional_section_added':False})
write(B/'issues.json',{'original_failed_receipt':'related/results.json','failed_assertions':2,'reason':'Two tests asserted the old explanatory sentences verbatim.','correction':'Check the selected-record wording; retain6-to0 price output and add direct checks for empty added/unread lists and a single price change.','final_receipt':'final/results.json','original_failure_retained':True})
examples=[{'before':'持有清单未核对完整，未列出不代表没有','after':'持有清单待核对'},{'before':'已读商品X件 · 不代表持有或当前仍在售','after':'已读商品X件'},{'before':'资料候选不等于本局实际出现；发生概率未核验','after':'候选资料 · 点击在地图侧栏阅读'},{'before':'展开来源范围与尚未核验的条件','after':'资料说明'}]
write(B/'summary.json',{'section':459,'kind':'implementation_maintenance','title':'精简常用页面说明','passed':True,'functional_section_added':False,'examples':examples,'necessary_validation':'final/results.json','tests_run':55,'original_failure':'related/results.json','source_review':'source-review.json','actual_local_test_window':'live-window/window.json','private_six_unchanged':True,'full_suite_rerun':False,'at_UTC':datetime.now(timezone.utc).isoformat()})
entry='## 界面维护：精简常用页面说明\n\n藏品清单、商店记录、事件预览和地图悬停改用简短状态与来源标签，保留领取条件及操作入口。55项定向检查通过，测试窗口已更新。[记录](verification/maintenance/player-copy-20261102/summary.json)。\n\n'
for p in ['WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md']:save(p,entry+(R/p).read_bytes().decode('utf8'))
save('PROJECT_REQUIREMENTS.md',(R/'PROJECT_REQUIREMENTS.md').read_bytes().decode('utf8')+'\n玩家页面与汇报使用简短的结果、条件和操作说明，重复的否定解释改为状态或来源标签；具体游戏条件保留，技术核验过程放在资料说明中。\n')
save('PROGRAM_REVIEW.md',(R/'PROGRAM_REVIEW.md').read_bytes().decode('utf8')+'\n[常用页面说明维护](verification/maintenance/player-copy-20261102/summary.json)：精简藏品、商店、事件及地图提示；55项定向检查通过。两个旧文案断言已随新显示更新，原始失败保留，数值与记录归属检查继续保留。\n')
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==459 and cp['next_section']==460
cp['player_copy_maintenance_20261102']={'kind':'implementation_maintenance','title':'精简常用页面说明','receipt':'verification/maintenance/player-copy-20261102/summary.json','binding':'enclosing_commit','functional_section_added':False,'necessary_tests':55,'status':'listed_scope_passed'}
cp['next_action']='继续精简其余玩家页面说明，完成深层资料与公开档案整合、笔记排版及视频细节；按已测开销定位本局信息解析中的重复文字处理。'
save('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n')
idx=runpy.run_path(str(R/'scripts/update_cloud_index.py'));idx['update'](R);idx['validate_delivery'](R,cp)
(B/'record-source.py').write_bytes(Path(__file__).read_bytes())
write(B/'final-audit.json',{'passed':True,'section':459,'kind':'implementation_maintenance','necessary_distinct_tests':55,'goal_active':True,'full_checks_cancelled':True,'private_six_unchanged':True,'requirements':pin('PROJECT_REQUIREMENTS.md'),'index':pin('CLOUD_INDEX.json')})
files={p.relative_to(R).as_posix():pin(p)for p in B.rglob('*')if p.is_file()and p.name!='archive-manifest.json'};write(B/'archive-manifest.json',{'kind':'explicit_public_player_copy_maintenance','files':files})
print(json.dumps({'maintenance':'concise_player_copy','passed':True,'tests':55,'section_unchanged':459,'public_files':len(files)}))
