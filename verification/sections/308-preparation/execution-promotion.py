from pathlib import Path
from hashlib import sha256
import json,subprocess,ast,sys,importlib.util
ROOT=Path(__file__).resolve().parents[1];PREP=ROOT/'verification/sections/308-preparation'
def pin(p):return{'bytes':p.stat().st_size,'sha256':sha256(p.read_bytes()).hexdigest()}
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def copy(src,target):
 target=ROOT/target;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((ROOT/src).read_bytes())
assert pin(ROOT/'rouge/data/fixed-landmark-references.json')['sha256']=='dc43bbbe70eab6f11cc8661c3bfeab994000ea614ea0f8c999a596f5cb2c445a'
h=json.loads((ROOT/'.cache/p3-308-backend/HANDOFF_REVIEW_READY.json').read_bytes())
assert json.loads((ROOT/'verification/sections/308-source-build-attempt1/process.json').read_bytes())['passed']
for name,p in {**h['functional_candidate_files'],**h['existing_test_maintenance']}.items():
 src=ROOT/'.cache/p3-308-backend/candidate'/name;assert pin(src)==p
 if(ROOT/name).exists():copy(name,'verification/sections/308-preparation/before/'+name)
 copy(src.relative_to(ROOT),name)
copy('.cache/p3-308-root-build-attempt1/fixed-landmark-references.json','rouge/data/fixed-landmark-references.json')
copy('.cache/p3-308-root-build-attempt1/build-receipt.json','research/p3-map-direct-ground-308/build-receipt.json')
native='.cache/p3-308-native-window/revision2/verify_direct_map_window_308.py'
assert pin(ROOT/native)['sha256']=='1c441f0f4f012d6cc0ea5bee423a3f81a941e64e3034e447b9208fe9b7969783';copy(native,'scripts/verify_direct_map_window_308.py')
legacy=ROOT/'.cache/p3-308-legacy-native/HANDOFF.json';lh=json.loads(legacy.read_bytes());assert pin(legacy)['sha256']=='6a991469212b3111c4d265f8e228fac8df1a35d027aff02591c1affbffa0bcc6'
for name,p in lh['promotion_files'].items():
 src=legacy.parent/'candidate'/name;assert pin(src)==p;copy(src.relative_to(ROOT),name)
for src,dest in [('.cache/p3-308-backend/HANDOFF_REVIEW_READY.json','backend-handoff-original.json'),('.cache/p3-308-backend/historical303-maintenance-proof.json','historical303-maintenance-proof.json'),('.cache/p3-308-backend/historical303-explicit107.diff','historical303-explicit107.diff'),('.cache/p3-308-backend/builder-semantic-review.json','builder-semantic-review.json'),('.cache/p3-308-backend/builder303-to308-semantic.diff','builder303-to308-semantic.diff'),('.cache/p3-308-backend/static-correction/correction.json','static-correction.json'),('.cache/p3-308-backend/static-correction/original-incorrect-png-magic.py','before/static-incorrect-PNG-draft.py'),('.cache/p3-308-backend/preparation-tool-error-summary.json','backend-preparation-tool-error.json'),('.cache/p3-308-native-window/revision2/READY.json','native-handoff-original.json'),('.cache/p3-308-native-window/revision2/static-source-alignment.json','native-static-source-alignment.json'),('.cache/p3-308-legacy-native/HANDOFF.json','legacy-native-handoff-original.json')]:copy(src,'verification/sections/308-preparation/'+dest)
for label,src in [('A','.cache/p3-308-reader-A/freeze_reader_a_original.py'),('B','.cache/freeze308_reader_b.py')]:copy(src,'verification/sections/308-preparation/execution-reader-'+label+'.py')
# Append one maintained module without rewriting existing CRLF bytes.
p=ROOT/'scripts/verify_full_available.py';raw=p.read_bytes();sys.path.insert(0,str(ROOT/'scripts'))
spec=importlib.util.spec_from_file_location('before_registry308',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);before=m.maintained_selectors();assert len(before)==474
line=b"ADDITIONAL_MODULES += ('tests.test_direct_landmark_308',)\r\n";anchor=b"ADDITIONAL_MODULES += ('tests.test_choice_annotations_307'";where=raw.index(b'\n',raw.index(anchor))+1
p.write_bytes(raw[:where]+line+raw[where:]);spec=importlib.util.spec_from_file_location('after_registry308',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);after=m.maintained_selectors();assert len(after)==475 and after[:474]==before
(PREP/'maintained-registration.json').write_bytes(enc({'section':308,'before_count':474,'after_count':475,'original_ordered_prefix_unchanged':True,'appended':after[474:],'source_sha256':pin(p)['sha256'],'full_rerun':False,'next_full':320,'actual_exit':0,'current_native_full_scope_variants':['scripts/verify_direct_map_window_303_full308.py','scripts/verify_direct_map_window_294_full308.py','scripts/verify_direct_map_window_308.py'],'original_native_scripts_preserved':True}))
text='''# 第308节 · 两张新固定原图的逐格参考

一步之遥、彼处水如酒的两张既有公开原图，按普通/紧急四个明确关卡身份核对。
两个隔离代理上下文分别目视同一原图和完整逻辑格，首次完整67格在比较前冻结；
它们不是两位真人、不是游戏采样，也不证明绝对位置精度。两份原始JSON结构不同，
不重序列化/改坐标；A的observed_pixel与B的pixel分别留原字段指针和完整来源。

完整67格逐项比较，16格一致（一步之遥5、彼处水如酒11），51格不可读或分歧。
只有双方均非空且原像素欧氏距离不超过4才保留A首次读数；不平均、不修点、不拟合、
不插值、不外推、不重读以求通过。所有拒绝及其原读数、原因均留在build-receipt。

旧107格的完整12图21关记录保留，新总量14图25关123格。原12图24关整面投影字节不改；
81关59图的完整校准缺口仍在，不因有部分点就视为整图完成。高台、出生脚点、随机偏移、
反向定位、整段路线与实际敌人位置均未由本节证明。只做手动固定资料阅读，不操作游戏。

source-manifest绑定原PNG/Git blob、完整原level/grid、完整请求、A/B原件及READY、旧直接/规则数据。
缓存路径只是原读者输入身份，source-records明确映射到公开文件，重建不依赖cache或私人文件。
构建默认只读；--output-dir仅允许新独立候选目录，拒runtime/source包/普通仓库目录和覆盖已有输出。

原303 builder严格拒绝新追加数据的合同保留。旧303测试明确在公开exact107临时夹具重放，
真实CLI也显式传该夹具；新308测试另核真实当前解析和旧guard对新current仍拒绝。
未来完整原生验收保留303/294原脚本，并提供full308当前变体，全部原流程保留且加107完整保留守卫。
源码/静态审查与构建不是产品验收；真实必要/原生及原项目窗口结果以verification/sections/308.json为准。
'''
(ROOT/'research/p3-map-direct-ground-308/README.md').write_bytes(text.encode('utf8'))
record={'section':308,'kind':'root_reviewed_public_promotion_not_acceptance','data_pin':pin(ROOT/'rouge/data/fixed-landmark-references.json'),'build_receipt_pin':pin(ROOT/'research/p3-map-direct-ground-308/build-receipt.json'),'native_pin':pin(ROOT/'scripts/verify_direct_map_window_308.py'),'code_and_303_test_candidate_pins':{**h['functional_candidate_files'],**h['existing_test_maintenance']},'private_or_game_or_chat_operations':False}
(PREP/'promotion.json').write_bytes(enc(record));(PREP/'execution-promotion.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({'section':308,'data_promoted':True,'acceptance_not_yet_executed':True,'maintained_selectors':len(after)},ensure_ascii=False))
