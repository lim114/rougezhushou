"""Static report only; parses source AST but never imports product or test code."""
import ast
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
inputs=json.loads((HERE/'static-inputs.json').read_bytes())
for name,pin in inputs['source_pins'].items():
 raw=(ROOT/name).read_bytes()
 assert sha256(raw).hexdigest()==pin['sha256']and len(raw)==pin['bytes'],name
compares={}
for relative,function in [('rouge/player_node_information.py','_event_lines'),('rouge/event_planning.py','_event_checks')]:
 before=ast.parse((ROOT/'verification/sections/298-preparation/before'/relative).read_text(encoding='utf8'))
 current=ast.parse((ROOT/relative).read_text(encoding='utf8'))
 target=next(node for node in current.body if isinstance(node,ast.FunctionDef)and node.name==function)
 removed=[];kept=[]
 for node in target.body:
  text=ast.unparse(node)
  remove=(function=='_event_lines'and isinstance(node,ast.If)and text.startswith("if context.get('entry_mode') in ('natural', 'content', 'processed_item'):"))
  if function=='_event_checks':
   remove=(isinstance(node,ast.Assign)and any(isinstance(t,ast.Name)and t.id in ('historical','reference')for t in node.targets)
     or isinstance(node,ast.If)and text.startswith("if reference and reference['context_applicable']:"))
  if remove:removed.append({'line':node.lineno,'node':type(node).__name__})
  else:kept.append(node)
 target.body=kept
 assert ast.dump(before,include_attributes=False)==ast.dump(current,include_attributes=False),relative
 compares[relative]={'original_module_AST_unchanged_after_removing_exact_added_reference_statements':True,
  'removed_added_nodes':removed,'source_before_sha256':sha256((ROOT/'verification/sections/298-preparation/before'/relative).read_bytes()).hexdigest()}
report={
 'kind':'SECTION298_INDEPENDENT_STATIC_REVIEW_NOT_TEST_OR_NATIVE_ACCEPTANCE',
 'at_utc':datetime.now(timezone.utc).isoformat(),
 'result':'No blocking defect found in the new six-target restriction/source-binding scope.',
 'scope':{'production_sources':['rouge/event_node_requirements.py','rouge/node_catalog.py','rouge/event_planning.py',
 'rouge/node_catalog_view.py','rouge/player_node_information.py'],
 'source_packet':'research/p3-event-node-requirements-298/source-manifest.json',
 'only_JSON_AST_and_source_read':True,'tests_or_Qt_run':False,'live_or_Git_modified':False},
 'verified_static_findings':[
  {'topic':'完整对象/原件绑定','result':'7个manifest成员SHA/长度全部匹配；6个expected_event与当前原catalog完整对象相等。封存值不是按标题或事件编号后缀匹配。',
   'evidence':'static-inputs.json/manifest_members and six_target_catalog_rows'},
  {'topic':'自然禁区适用范围','result':'模型只在explicit natural、已知1–6主层、非特殊、非历史时给bool；其它上下文保留参考而matches=None。allowed结果的整体资格仍unknown，actual_server_eligible始终None。',
   'source':'rouge/event_node_requirements.py:event_requirements/_context'},
  {'topic':'科技不是未经证明的硬门','result':'科技数据只有known_enabling_path_only/两个hard-negative标志False、actual_account_active=None；没有账号科技状态输入或未点亮排除分支。',
   'source':'rouge/event_node_requirements.py:_valid_schema/event_requirements; player_node_information.py:_event_lines'},
  {'topic':'来源失效','result':'每次fresh读manifest和7成员，缓存对象canonical完整性另核；包失效或实际阅读对象与expected_event不相等时不能沿用禁区。event_planning转未知check，event_candidates不走False排除。',
   'source':'event_node_requirements._verified_packet; node_catalog.natural_event_requirements/event_candidates'},
  {'topic':'已读/历史内容','result':'node_dossier先用observed title内容替代generic rows；已读内容与history_observed_*独立保留。新增excluded_event_candidates只补泛候选，不覆盖observed或passed内容。NodePanel对explicit/history用content，并以reference_context_scope阻止natural禁区。',
   'source':'rouge/node_catalog.py:node_dossier; rouge/node_catalog_view.py:_event_context/_entries'},
  {'topic':'默认资源/玩家输出','result':'default规划上下文是unknown；新check仅context_applicable时append，玩家新增说明块仅explicit natural/content/processed。两模块的其余AST精确保持。静态证据支持默认输出不变，但没有执行190资源/38输出的实际比较。',
   'evidence':'module_AST_boundaries; actual comparison remains root necessary-validation responsibility'},
  {'topic':'玩家用语','result':'新增段先列不会自然出现的具体层数，明确是固定资料、保留完整内容和当前服务器未知；科技说明与账号点亮分开，无概率或路线建议。',
   'source':'rouge/player_node_information.py:_event_lines'}],
 'module_AST_boundaries':compares,
 'resolved_static_observations':[
  {'kind':'new generic keyword API boundary corrected by root before formal execution','source':'rouge/node_catalog.py:event_candidates natural_context',
   'static_counterexample_input':{'node_type':None,'floor':6,'include_indirect':True,'entry_mode':'content','historical':True},
   'original_affected_example':'community_group_000 桑尼的邀请 has old catalog floors[1,2]; the first promoted draft still filtered it before consulting the new model.',
   'correction_verified_statically':'root将natural_context限定natural且非historical，explicit content/history不再套旧floors；旧无kwargs调用默认natural且historicalFalse保持。',
   'qualification':'6个本节目标的old floors全部None，原问题是新泛用kw边界，不是已读/历史UI正文已被实际删除的观察。没有执行这个算例。'},
  {'kind':'avoidable read-only source lookup removed; no measured performance claim','source':'rouge/event_planning.py:_event_checks and node_catalog.py:event_candidates',
   'original_observation':'first draft在defaultunknown仍核新的六目标包，虽然不append新check。',
   'correction_verified_statically':'root的新条件表达式只有natural+knownfloor+非special/非history时调用helper；其他上下文短路None，显式玩家说明仍独立fresh核验。',
   'qualification':'没有进行耗时或卡顿测试，不宣称量化提速。'}],
 'source_guard_interruption':{'first_finalizer_exit':1,'reason':'rouge/node_catalog.py changed by root between initial static inventory and finalization; source guard correctly refused a mixed-source report',
   'first_source_map':'static-inputs-first.json','first_finalizer_source':'finalize-review-first.py',
   'product_test_failure':False,'new_source_reread_before_this_report':True},
 'not_claimed':['未执行新增或旧测试、未运行Qt/窗口。','没有把静态默认分支推理当成190/38实际输出哈希通过。',
 '没有重审原HTML每个DOM字节的语义，复用源包与作者研究原件；技术路径仅审本节六目标。',
 '没有因未见阻断就声明P3/层数15缺口或任何实际服务器资格完成。'],
 'source_pins':inputs['source_pins']}
with(HERE/'review.json').open('xb')as stream:stream.write((json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps({'review_sha256':sha256((HERE/'review.json').read_bytes()).hexdigest(),
 'blocking_defect_found':False,'static_only':True,'tests_Qt_live_Git_operations':False},ensure_ascii=False))
