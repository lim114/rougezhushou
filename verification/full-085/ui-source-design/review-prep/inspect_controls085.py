"""Read public bytes/AST/JSON only. No application import, API/Qt/Wine call."""
from pathlib import Path
from datetime import datetime, timezone
import ast, hashlib, json, re, subprocess

R = Path('/workspace/rougezhushou')
O = Path('/workspace/.continuation/ui-085-draft/review-prep')
B = Path('/workspace/.compat/wine-ui-smoke-080.py')
EXPECTED = 'c58ff7ac462e7a9aa457e4b59471a162cbf5c6daf58192f6b5a852901fcdcc98'

def sha(data): return hashlib.sha256(data).hexdigest()
def load(p): return json.loads(p.read_bytes())
def write(name, data): (O/name).write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')

def evidence(path):
    data = path.read_bytes()
    rel = str(path.relative_to(R)) if path.is_relative_to(R) else None
    info = {'source_path':str(path), 'sha256':sha(data), 'bytes':len(data)}
    if rel:
        proc = subprocess.run(['git','show','HEAD:'+rel],cwd=R,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        info['head_git_blob_sha256'] = sha(proc.stdout) if proc.returncode == 0 else None
        info['matches_HEAD_git_blob'] = proc.returncode == 0 and proc.stdout == data
    return info

runner_data = B.read_bytes()
assert sha(runner_data) == EXPECTED
ast.parse(runner_data)
(O/'actual080-wine-ui-smoke.py').write_bytes(runner_data)
files = [R/'rouge'/n for n in ('app.py','operator_options.py','operator_engine.py','reporting.py','relics.py','catalog.py')]
files += [R/'rouge/data'/n for n in ('catalog.json','relic-mechanics.json')]
files += [R/'.cache/p2-s1-binding'/n for n in ('character_table.json','skill_table.json')]
source_records = {str(p.relative_to(R)):evidence(p) for p in files}
for p in files[:6]:
    ast.parse(p.read_bytes())
    (O/('source-'+p.name)).write_bytes(p.read_bytes())

cat = load(R/'rouge/data/catalog.json')
mech = load(R/'rouge/data/relic-mechanics.json')
char = load(R/'.cache/p2-s1-binding/character_table.json')['char_298_susuro']
skills = load(R/'.cache/p2-s1-binding/skill_table.json')
opts_tree = ast.parse((R/'rouge/operator_options.py').read_bytes())
opts = ast.literal_eval(next(node.value for node in opts_tree.body if isinstance(node, ast.Assign) and any(isinstance(t,ast.Name) and t.id=='OPTIONS' for t in node.targets)))
selected = ('rogue_6_relic_legacy_81','rogue_6_relic_legacy_82','rogue_6_relic_legacy_83')
selectors = {
 'susuro_raw_character_talents':char['talents'],
 'susuro_raw_skill_links':char['skills'],
 'susuro_raw_skill_levels':{link['skillId']:skills[link['skillId']]['levels'] for link in char['skills']},
 'susuro_catalog_talents':cat['operators']['char_298_susuro']['talents'],
 'susuro_catalog_modules':cat['operators']['char_298_susuro']['modules'],
 'susuro_OPTIONS':opts['char_298_susuro'],
 'relic_catalog_indices_zero_based':[(i,rid,cat['relics'][rid]['name']) for i,rid in enumerate(cat['relics']) if rid in selected],
 'relic_catalog_records':{rid:cat['relics'][rid] for rid in selected},
 'relic_mechanics_records':{rid:mech['relics'][rid] for rid in selected},
}
write('public-selectors085.json', selectors)
assert selectors['relic_catalog_indices_zero_based'] == [(119,selected[0],'活玫瑰'),(120,selected[1],'苍白花冠'),(121,selected[2],'涌动之餐')]
assert opts['char_298_susuro'] == [('low_cost_healing_target','受疗干员初始费用不超过10',False,1,(1,2)),('casts_used','本场此前深度治疗次数',0,2,(2,))]
assert all(any(bb['key']=='skill_max_trigger_time' and bb['value']==2.0 for bb in level['blackboard']) for level in skills['skchr_susuro_2']['levels'])

report_text=(R/'rouge/reporting.py').read_text(encoding='utf-8')
report_ast=ast.parse(report_text)
formatter=next(n for n in report_ast.body if isinstance(n,ast.FunctionDef) and n.name=='format_report')
phrase=next(n for n in formatter.body if isinstance(n,ast.FunctionDef) and n.name=='phrase')
opaque=next(n for n in ast.walk(phrase) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='sub' and len(n.args)>1 and isinstance(n.args[1],ast.Constant) and n.args[1].value=='未核验配置（原文见技术资料）')
regex=ast.literal_eval(opaque.args[0]); replacement=ast.literal_eval(opaque.args[1])
warnings=['组合 '+group+' 的叠加规则尚未核验，未套用该组合。' for group in ('heal_scale','received_regeneration')]
human=[re.sub(regex,replacement,w) for w in warnings]
assert human[0]==human[1]

receipt=load(Path('/workspace/.compat/wine-ui-080.json'))
assert receipt['passed'] is True and receipt['complete_ui_validation'] is True and len(receipt['checks'])==3063
facts={
 'scope':'Independent read-only preparation for UI085; no imports of application, calculate_damage/prepare/formatter calls, no suites, Qt, Wine, native Windows or game operation. JSON data and AST/source bytes only.',
 'created_utc':datetime.now(timezone.utc).isoformat(),
 'branch':subprocess.check_output(['git','branch','--show-current'],cwd=R,text=True).strip(),
 'root_HEAD_at_read':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),
 'root_changes_at_read':subprocess.check_output(['git','status','--short'],cwd=R,text=True).splitlines(),
 'observed_runtime':{'running':True,'connected':True,'observations_current':True,'network_policy_state':'unknown','new_network_requests':0},
 'actual080_runner':evidence(B),
 'actual080_receipt':{'evidence':evidence(Path('/workspace/.compat/wine-ui-080.json')),'checks':3063,'passed':True,'complete_ui_validation':True,'attribution':'Root historical actual080 execution; reviewer only read receipt.'},
 'old_body_requirement':'All 3063 old actual080 record-producing paths/body/semantics must remain; this reviewer has not inspected an085candidate yet.',
 'sources':source_records,
 '81_relic_list':{
  'creation':'app.py 689 iterates catalog()[relics].items(); QListWidget.addItem appends; no sortItems or setSortingEnabled in MainWindow production source.',
  'manual_mode':'auto_relics defaults True; manual click tests require setChecked(False), real sync_run_relics makes items checkable. Restore original mode/state afterwards.',
  'serialization':'calculate app.py 1024-1025 scans count indices and includes every Checked item once. Hidden filtered items are still scanned.',
  'filter':'filter_relics app.py 1000 changes only item.setHidden(text not in item.text()).',
  'invalid_UI_assumptions':['click order determines relic_ids','search hiding removes selection','duplicate IDs','unlisted unknown ID','arbitrary reverse relic_ids array'],
  'known_visual_order':selectors['relic_catalog_indices_zero_based'],
  'resolution_order':'prepare current relics.py candidates=rules+effects+token_effects, dict.fromkeys of unverified group preserves first occurrence, without changing candidate construction/removal or game stacking.',
  'literal_debug_and_technical_warnings':warnings,
  'default_report_replacement_derived_from_AST':{'pattern':regex,'replacement':replacement,'lines':human,'count':2,'explanation':'format_report deduplicates original warning strings before phrase, so identical translated lines remain twice. This is static derivation, not a formatter call or actual UI result.'},
  'requirements':['Check exact submitted catalog-index ordered ids and matching resolution records.','Check raw structured warnings and record.pending exact first-candidate group order.','Compare whole actual QPlainTextEdit to formatter output with existing NBSP normalization when permitted later.','Technical display can assert heal_scale precedes received_regeneration.','Default display must retain two translated warning lines; do not require raw group names or silently collapse duplicate human lines.','No claim about actual game trigger/order/stacking; all related group exclusions and incomplete flags persist.']
 },
 '82_susuro_controls':{
  'low_cost':{'source':'operator_options.py 8, app.py 667-676, app.py 1035-1037','type':'QCheckBox','default':False,'applicable_skills':[1,2],'serialization':'widget.isChecked() produces bool'},
  'casts_used':{'source':'operator_options.py 8, app.py 671-674, app.py 1035-1037','type':'QSpinBox','range':[0,2],'default':0,'applicable_skills':[2],'serialization':'widget.value() produces int'},
  'casts_used_semantics':{'2':'operator_engine.calculate checks >=2 before plans and raises exact ValueError 深度治疗本场已使用两次，不能再次开启。; app calculates catches and shows exception text, damage_result stays None.','1':'Existing model marks nonrepeat; cannot expect numeric cycle_healing/cycle_seconds for another full reuse.','0':'Existing normal repeat reference when remaining gates permit.'},
  'healing_targets_UI_range_for_susuro':[0,1],
  'raw_skill_evidence':'Original skchr_susuro_2 has skill_max_trigger_time2.0 and same-battle max2 description at all10ranks; no hidden clock or simulation rule is inferred.',
  'raw_talent_evidence':'微创治疗 first E1L1, requiredPotentialRank4 maps to displayed potential5; E2 and current qualified PHY-X source remain original. E0 checked does not invent missing talent.',
  'readonly_cultivation':'elite/trust/potential/module/rank are QLabel or read-only observations; level is a real QSpinBox bounded by phase max. Temporary train helper only injects public in-memory observation and updates real window. Explicit known skill_ranks required; otherwise fallback E0/E1 rank7/E2 rank10 is preview, not real account inheritance.',
  'source_boundaries':['S1 unlocked E0L1; S2 unlocked E1L1.','Public cultivation phase max: E0 45, E1 60, E2 70.','PHY-X uniequip_002_susuro gate E2L40; levels39/40 meaningful, not49/50.','S1 scenario omits inactive casts_used regardless of hidden widget stored value.','Boolean false and true only in actualQt path; stringFalse, stringTrue, null, NaN, dict/list and numeric coercion belong API tests, never passed to Qt as fake types.','82 draft/source not frozen here; no repaired API behavior or final UI085 pass claimed.','No synthetic base_attack control: UI attack is readonly, derive ratios from actual same cultivation and chosen talent, do not hardcode1000-reference totals.','Saving public model state for preview does not verify OCR/current game cost/recipient presence/account unlock or native module attachment.'],
  'suggested_real_boundaries':['S1 E0/E1/E2 boolFalse/True and bothtiming modes.','S2 E1/E2 boolFalse/True with real casts_used0/1/2, check2 exact UI error separately.','Actual integer healing_targets0/1, zero/window/lifetime scope already supported by real controls.','Potential4/5 and module39/40 with stages2/3 only as read-only public observations, selected talent derives factor.','Natural initial/recharge/duration clocks remain same between boolFalse/True where bothsuccessful; casts1 cycleNone remains unknown/unavailable, casts2 is rejected.']
 },
 'pending_sections':[83,84,85],
 'final_status':'Preparation complete only. Await author candidate for static design review; await final root85 freeze for formal source/runner/API receipt verification. No new API/Qt/Wine call.'
}
write('source-control-notes085.json',facts)
write('preparation-diagnostics085.json',{'preparation_read_failures':[
 {'attempt':1,'command_scope':'rg file discovery against planned ui-085-draft before creation','exit_code':2,'cause':'directory did not yet exist; independent actual080/repo matches remained visible','resolution':'created only reviewer-owned external nested review-prep directory; no dependent API/Qt run'},
 {'attempt':2,'command_scope':'rg against mistaken rouge/calc/reporting.py, rouge/calc/engine.py and rouge/calc/relics.py paths','exit_code':2,'cause':'flat rouge package rather than nonexistent calc subpackage','resolution':'read actual rouge/reporting.py, rouge/operator_engine.py, rouge/relics.py; no tests/runtime were launched'}],
 'actual_UI_failures':0,'API_calls':0,'tracked_edits':0,'Windows_executions':0,'native_mechanism_changes':0})
(O/'NOTE.md').write_text('独立只读准备已完成。原080runner固定SHA '+EXPECTED+'，历史真实窗口3063项由root执行，本审查只读回执。\n\n81界面按catalog顺序勾选、隐藏搜索不改序；普通报告两个未知组合原名均匿名为同文，仍保留两行，技术资料才可按原名直接断言顺序。\n\n82真实low_cost_healing_target为bool复选框，casts_used为0–2整数且仅S2；casts2旧门槛拒绝，casts1不允许重复周期。苏苏洛PHY-X门槛是E2L40，培养只读预览不是新增selector，不能把API字符串/null冒充Qt输入。\n\n仅资料与AST/JSON/字节核验；未调用应用API、formatter、prepare、Qt、Wine、游戏。83–85待确定；任何未冻版本不运行预核。两次只读路径准备错误完整保留，不作为产品失败或已测机制。\n',encoding='utf-8')
paths=sorted(p for p in O.rglob('*') if p.is_file() and p.name!='manifest.json')
write('manifest.json',{'format_version':1,'files':[{'source_path':str(p),'archive_path':str(p.relative_to(O)),'bytes':len(p.read_bytes()),'sha256':sha(p.read_bytes())}for p in paths]})
print(json.dumps({'passed_readonly_preparation':True,'source_control_notes_sha256':sha((O/'source-control-notes085.json').read_bytes()),'manifest_sha256':sha((O/'manifest.json').read_bytes()),'files':len(paths),'API_calls':0,'Qt_calls':0,'Wine_calls':0},ensure_ascii=False))
