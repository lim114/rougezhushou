from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,subprocess,difflib,re,runpy,sys
R=Path.cwd();B=R/'verification/sections/443-records';B.mkdir(exist_ok=False)
BASE='31fc275c93befe1f3e44857786f9f1b79f76ec99';title='商店标价自动读取、离店回看与共享图片和对照'
def read(n):return json.loads((R/n).read_bytes())
def write(n,v):(R/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
def pin(n):
 raw=(R/n).read_bytes();return {'receipt':str(n).replace('\\','/'),'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
def save(n,s):
 p=R/n
 if not p.exists():p.write_text(s,'utf8');return
 a=p.read_bytes().decode('utf8').splitlines(keepends=True);b=s.splitlines(keepends=True)
 for x,y,k in difflib.SequenceMatcher(None,[v.rstrip('\r\n')for v in a],[v.rstrip('\r\n')for v in b],autojunk=False).get_matching_blocks():b[y:y+k]=a[x:x+k]
 p.write_bytes(''.join(b).encode('utf8'))
assert subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()==BASE
assert subprocess.check_output(['git','branch','--show-current']).decode().strip()=='codex/p2-development'
checks=read('verification/sections/443-shop-verified/results.json');assert checks['passed']and checks['tests_run']==90 and not checks['failed']and not checks['errors']and not checks['skipped']and not checks['forbidden_external_calls']
assert read('verification/sections/443-shop-verified/process.json')['actual_observed_exit']==0
ids=re.findall(r'^test_\w+ \(([^)]+)\)',(R/'verification/sections/443-shop-verified/stderr.txt').read_text('utf8'),re.M);assert len(ids)==len(set(ids))==90
native_scopes={}
for folder,count in [('443-native-shop-verified',25),('443-native-history-verified',23)]:
 n=read(f'verification/sections/{folder}/window.json');assert n['passed']and n['unique_checks']==count and not n['source_drift']and not any(n['external_operation_attempts'].values())
 assert read(f'verification/sections/{folder}/process.json')['actual_observed_exit']==0
 for name,digest in n['source_sha256_after'].items():assert sha256((R/name).read_bytes()).hexdigest()==digest,name
 write(f'verification/sections/{folder}/root-image-review.json',{'actual_final_PNG_viewed':True,'images':n['screenshots'],'actual_interaction_checks_kept_separate_from_appearance':True,'isolated_state_not_real_game_or_complete_video_parity':True})
 native_scopes[folder]={'receipt':f'verification/sections/{folder}/window.json','unique_checks':count}
public=read('verification/sections/443-public-images-final/results.json');assert public['passed']and len(public['cases'])==7
pairs=read('verification/sections/443-sample-pairs/results.json');assert pairs['passed']and len(pairs['pairs'])==20 and not any(r['new_shop_page']for r in pairs['pairs'])
assert read('verification/sections/443-sample-pairs/process.json')['actual_observed_exit']==0
live=read('verification/sections/443-live-window-final/window.json');assert live['passed']and live['private_six_paths_unchanged']
status=read('.cache/shop-price-443-live-status.json');assert status['toolbar_visible']and status['elapsed_since_launch']>4
write('verification/sections/443-live-window-final/desktop-review.json',{'actual_Windows_mcp_screenshot_region':[1716,1164,2130,1218],'toolbar_actually_viewed':True,'visible_responding_and_Qt_timer_advanced':True,'private_six_paths_unchanged_at_startup':True,'not_a_live_game_accuracy_claim':True})
before=read('.cache/shop-price-443-before.json')['private'];changed=[n for n,v in before.items()if(sha256((R/n).read_bytes()).hexdigest()if(R/n).is_file()else None)!=v]
write('verification/sections/443-records/private-scope.json',{'whole_batch_private_six_unchanged':not changed,'changed_paths_if_any':changed,'change_origin_not_inferred':bool(changed),'startup_six_paths_unchanged':True,'private_contents_hashes_images_or_expected_values_published':False,'private_backup_restore_or_rollback':False})
sources=['rouge/player_acceptance.py','rouge/player_catalog_grid.py','rouge/player_feature_426_acceptance.py','rouge/player_parts.py','rouge/player_shop_hover.py','rouge/player_shop_memory.py','rouge/player_shop_replay.py','rouge/recognition.py','rouge/run_state.py','rouge/view_catalog.py','scripts/verify_full_available.py','tests/test_shop_prices_443.py']
write('verification/sections/443-records/source-review.json',{'base_commit':BASE,'changed_or_new_sources':{n:pin(n)for n in sources},'application_source_files':538,'new_application_modules':0,'REA_scope':'Complete Python source uses direct source/runtime review under REA skill. No new REA invocation or whole-program conclusion.','reuse':'Existing RapidOCR/OpenCV and price-label card binding, current sampling interpreter, RunState, shop history, exact existing44 part images and Qt palette. No dependency/model/new image download.','simplification':'One current grid qualification per identify instead of two; record_shop shared by hover and normal sampler; current/archive reuse one comparison control; parts and shop share exact image loader. Net source lines are not reduced because new price capability is added.','ingress':'Current OCR has its text/geometry boundary; independent saved history admission validates optional nonnegative integer price. No broad new try/catch or generic recovery layer.','new_low_probability_defensive_layer':False,'calculation_models_or_relic_mechanisms_changed':False,'source_links':['https://prts.wiki/w/树海肉鸽','https://doc.qt.io/qtforpython-6/PySide6/QtGui/QPalette.html#PySide6.QtGui.QPalette.text'],'whole_program_or_video_complete':False})
first=read('verification/sections/443-public-images/results.json')
write('verification/sections/443-records/failure-disposition.json',{'original_public_pipeline':'verification/sections/443-public-images/results.json','original_actual_outer_exit_observed':1,'original_cases':len(first['cases']),'original_missed_price_cases':sum(not r['expected_visible_prices_match']for r in first['cases']),'cause':'Current whole-frame detection misses isolated6; smaller12 is below confidence threshold. Kept unknown instead of lowering threshold.','repair':'After exact current card/price-label binding, read only upright white digit area with existing recognizer. Same derived area joins exact pixel cache invalidation. Ambiguous or signed reads are not stripped into prices.','first_native_image_issue':'Existing part image not reached through relic-only loader; current comparison occupied space; hardcoded mint text unreadable on white archive background.','repair_display':'Reuse exact part images, share one collapsed comparison, use Qt text palette for unselected labels.','original_artifacts_kept_unchanged':True})
save('research/shop-price-443/README.md',f'''# 第443节 + {title}

基线{BASE}。目标为原片2:29–2:33离店仍能查商品、2:35–2:57文字优先与图文物品查询，不以局部进展冒称视频全部一致。实际查看原片158/164秒及172秒；158/164是同一演示的不同画面，不是独立对局。

旧判定强制出现购买文字，原片158/164两份当前OCR因此均未识别商店。现在保留旧入口，补由当前余额、刷新、前瞻性投资及至少两处价格组成的明确页面特征；没有固定屏幕坐标。商品仍按精确名称对应本帧自己的价格标签；被遮挡、同名不唯一或数字含糊时不补猜。价格从当次画面读取，不按稀有度/藏品推算折扣、购买或剩余刷新。

主采样读取器复用同次文字输出，不再要求先悬停5秒才能保存商店清单。原hover入口共用shop_snapshot与record_shop，仍保留原新鲜度/本局边界；正常采样沿用RunState.apply的时序资格并只保存一次。商店不变成持有清单，离店不删除历史，只有用户手动新局重置本局。旧记录没有标价时继续未知。

首轮7组完整读取有4组漏价格：整帧检测漏掉单个6，小画面12低于原置信门槛。失败原件保留；不降门槛，只在已经确认商品归属的价格标签下方按当前字号定位白色数字，复用既有识别器直接读这一行，不再次整帧检测/方向分类。含糊或带符号的文字不转成非负价格；该价格区域同时加入精确像素复用核对，名称不变也不能证明旧价格仍有效。原片164可见浪花6、悲伤的红12、老妈的鼓励12；158浪花被遮挡保留未知，两份伪翅下方标价不可见也保持未知。

[PRTS黑流树海资料](https://prts.wiki/w/树海肉鸽)说明商店用源石锭购买商品，仅用于单位/语义核对；这是社区资料，不冒称当前服务器实测。价格和刷新费用、投资余额、公开池频率分别处理，不套用文献刷新规则倒推剩余次数。[Qt QPalette](https://doc.qt.io/qtforpython-6/PySide6/QtGui/QPalette.html#PySide6.QtGui.QPalette.text)用于让浅色历史页的文字跟随实际主题；深色物品页保留绿色标签。

图文回看保留当次标价与准确条目，数量为0与未读分开；前后价格变化单独列出，不叫已买、下架或刷新。长对照默认收起，与历史页复用同一控件，阅读选择/搜索随刷新保持。窗口审阅发现浪花已有零件原图却显示无图，现共享既有44件零件准确图片入口，原298藏品图片保持，没有新下载或改写图像/许可。原重复识别页面、分散保存与历史折叠控制已合并；新增能力使总代码有增加，不称净减或整体提速。

最终90项不同必要检查通过，无失败/错误/跳过。当前商店25项和历史商店23项原生范围分别通过，共同基础检查不累加；两份最终截图逐张查看，6→0为隔离构造测试，不是游戏优惠实测。7组实际完整ScreenReader读取（原图/缩放/留边）匹配人工核对的可见价格；20份既有本机样本没有新shop分类，全部原解释保持，图像/文字/实际数值只留本机。有限派生样本不是全部布局或独立连续游戏准确率，也不证明FPS或全流程性能改善。

实际小窗更新并可见响应，Qt计时器推进，启动六私人路径保持；整批摘要另见private-scope.json，变化如实保留不推定来源、不回滚。726选择器保留既有顺序并追加本节，仅登记核对，不是全量执行；full440仍绑定原冻结源码，下次完整455。全程序、完整视频、其余标价版式/购买状态/刷新次数、同名遗产真实差别及P3/P2/P1仍未完成。未操作游戏、发送聊天或上传私人数据。

[本节回执](../../verification/sections/443.json)。
''')
entry=f'''<!-- player-section-443 -->
## 第443节 + {title}

商店首页不再强制购买文字；正常采样与悬停共用当前名称/价格对应和保存入口。已读标价离店可查、价格单独变化留历史，0与未读分开，旧记录不追填；未读/购买/刷新不混同。复用已有44件零件图片、统一当前/历史折叠对照，并修正浅色历史文字对比度。

90项必要检查通过；25项当前商店与23项历史原生范围分别通过，两个最终原图已看；7组公开图完整读取通过，20本机旧样本原事实保持。原四组漏读、缺图与对比度问题及修复前原件保留，不称独立实机全覆盖或提速。小窗更新可见响应、启动六私人路径保持；回执verification/sections/443.json，全程序/视频及P3/P2/P1未完成，下次完整455。

'''
for n in('WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md'):
 s=(R/n).read_text('utf8')
 if n=='WORK_IN_PROGRESS.md':s=s[s.index('<!-- player-section-442 -->'):]
 save(n,entry+s)
n='PROJECT_PROGRESS.md';s=(R/n).read_text('utf8');s=s.replace('商店未读商品、价格/购买状态与刷新次数','商店其余未读商品和标价版式、购买状态与刷新次数');save(n,s)
for n in('PROGRAM_REVIEW.md','IMPLEMENTATION_STRATEGY.md'):
 s=(R/n).read_text('utf8');save(n,s+'\n[第443节商店文字与标价回顾](research/shop-price-443/README.md)打通正常采样到已读标价历史，合并重复识别/保存/折叠入口，复用既有零件图片并适配浅色文字。其它页面、完整版本/价格版式、实际交易/刷新与全程序/视频仍未完成。\n')
n='PROJECT_REQUIREMENTS.md';s=(R/n).read_text('utf8').replace('当前功能第442节','当前功能第443节',1)
marker='## 界面资源的读取与保留';assert marker in s
s=s.replace(marker,'## 商店信息读取与历史\n\n商品名称和当次标价从当前商店画面对应，不要求先悬停，也不按固定坐标或稀有度推算。离开商店保留已读清单；价格变化与名称变化分开记录，旧记录不补写未来价格。0与未读分开，未读不表示已售罄，标价不证明购买、持有、下架或剩余刷新。被遮挡、同名歧义或数字不明确时只保留已证字段；现有图标按准确条目复用，长对照按需展开。\n\n'+marker,1);save(n,s)
n='VIDEO_PARITY.md';s=(R/n).read_text('utf8');s=s.replace('未读商品、价格、购买/移除、刷新次数和完整库存仍未齐，不能用收藏品持有记录代替。','第443节接入正常采样的商品/标价、离店与旧记录回看及价格独立变化，并共享零件图片与折叠对照；其余商品/标价版式、购买/移除、刷新次数和完整库存仍未齐，不能用持有记录代替。',1)
s=s.replace('希望、生命、护盾、指挥等级等完整读取与可靠性仍待补齐。','441–442已接入六项界面读值和希望上限；其余布局、未读字段和连续可靠性仍待补齐。',1)
save(n,s+'\n[第443节](research/shop-price-443/README.md)按原片158/164的实际商店文字补采样到已读价格历史，当前/历史物品沿用准确图片和选择。仅完成已验价格与阅读路径，不冒称整店、动态交易/刷新、完整实机或视频外观完成。\n')
receipt={'section':443,'kind':'functional_section','title':title,'new_capability':'正常后台采样与悬停共用商店名称/标价读取及保存；离店和历史可查当次标价、价格独立变化，旧记录不追填。共享准确零件图片和折叠对照，改善浅色标签。','limitations':'其它页面/标价形式/遮挡及连续实机准确性、购买/下架/剩余刷新和全店完整性未完成。派生公开画面和旧样本不算独立游戏实测；未声称提速、完整视频或全程序完成。','necessary_validation':pin('verification/sections/443-shop-verified/process.json'),'unit_tests_run':90,'native_windows_scopes':native_scopes,'public_image_pipeline':pin('verification/sections/443-public-images-final/results.json'),'sample_pairs':pin('verification/sections/443-sample-pairs/results.json'),'actual_local_test_window':pin('verification/sections/443-live-window-final/window.json'),'source_review':pin('verification/sections/443-records/source-review.json'),'source_sha256':{n:sha256((R/n).read_bytes()).hexdigest()for n in sources},'full_suite_rerun':False,'old_full440_proves_current_source':False,'goal_active':True,'whole_program_or_video_complete':False,'at_UTC':datetime.now(timezone.utc).isoformat()}
write('verification/sections/443.json',receipt)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==442 and cp['next_section']==443
cp['completed_sections']=443;cp['next_section']=444;cp['sections'].append({'number':443,'completion_ref':'player-section-443','topic':title,'verification':'verification/sections/443.json'})
cp['current_section_save']={'section':443,'verification':'verification/sections/443.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':443,'receipt':'verification/sections/443.json','necessary_checks':90,'native_scopes':{'current_shop':25,'archived_shop':23},'full_validation_rerun':False}
cp['current_batch'].update(completed_sections=443,next_section=444,next_section_started=False,receipt='verification/sections/443.json',scope='Whole-program review and full video parity remain active. Functional443 shop prices/normal sampling/history and shared UI completed in verified scope;444 not started.')
cp['next_action']='继续全程序与视频逐链路回顾，保留商店标价自动读取和历史；推进其余P3页面/商品/节点/条件与紧凑阅读、版本和连续实机覆盖；OCR同步优化，存量三条规则继续整改。其余标价形式、购买状态/剩余刷新、全程序/视频和P3/P2/P1未完成。444未启动，下次完整455。'
if isinstance(cp.get('player_feature_sections'),list):cp['player_feature_sections'].append(443)
assert cp['functional_sections_since_latest_requirement'][-1]==442;cp['functional_sections_since_latest_requirement'].append(443)
save('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n')
idx=runpy.run_path(str(R/'scripts/update_cloud_index.py'));idx['update'](R);assert idx['validate_delivery'](R,cp)['current_section']==443
sys.path.insert(0,str(R/'scripts'));from verify_full_available import maintained_selectors
assert len(maintained_selectors())==726
write('verification/sections/443-records/final-audit.json',{'passed':True,'functional_section':443,'necessary_distinct_tests':90,'native_scopes_separate':[25,23],'ordered_selectors':726,'active_functional_list_includes443':True,'source_review':pin('verification/sections/443-records/source-review.json'),'requirements':pin('PROJECT_REQUIREMENTS.md'),'index':pin('CLOUD_INDEX.json'),'section_receipt':pin('verification/sections/443.json'),'current_full_rerun':False,'goal_active':True,'whole_program_or_video_complete':False})
(B/'record-source.py').write_bytes(Path(__file__).read_bytes())
files={}
for folder in(R/'verification/sections').glob('443-*'):
 if folder.is_dir():files.update({p.relative_to(R).as_posix():{k:v for k,v in pin(p.relative_to(R)).items()if k!='receipt'}for p in folder.rglob('*')if p.is_file()and p.name!='archive-manifest.json'})
files['verification/sections/443.json']={k:v for k,v in pin('verification/sections/443.json').items()if k!='receipt'}
write('verification/sections/443-records/archive-manifest.json',{'kind':'explicit_public_archive_no_private_inputs_or_expected_values','files':files})
print(json.dumps({'passed':True,'section':443,'necessary_distinct_tests':90,'native_scopes_separate':[25,23],'public_archive_files':len(files),'whole_goal_complete':False}))
