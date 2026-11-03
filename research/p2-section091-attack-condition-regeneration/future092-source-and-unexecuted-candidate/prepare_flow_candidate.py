"""Prospective source candidate only. No imports/execution of project/Qt code."""
import ast
import difflib
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
UI91=Path('/workspace/.continuation/p2-continuous-attack-controls-091-ui-candidate')
DEEP91=Path('/workspace/.continuation/p2-section091-deepcolor-regeneration-notes-author')
SOURCE=Path('/workspace/.continuation/p2-window-target-timing-candidate-source')


def sha(raw):return hashlib.sha256(raw).hexdigest()


def put(name,obj):(HERE/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')


ui_mf=(UI91/'ui-author-public-manifest091.json').read_bytes()
deep_mf=(DEEP91/'public-artifacts-manifest-final.json').read_bytes()
source_mf=(SOURCE/'public-source-manifest.json').read_bytes()
assert sha(ui_mf)=='2b286f356a0d10da925f269f6e303c731adfcf9674efc18eef22363e092a7b53'
assert sha(deep_mf)=='cfedb0ab204f413d77fe695c614f6667df92886320abc23d5a6d99c9963ece73'
assert sha(source_mf)=='fa7955a7b6114e4eb47ce2e87afc3c4f1451d832f102c1298fdb29fe40b1add1'
app_path=UI91/'candidate/rouge/app.py'
report_path=DEEP91/'draft-tree/rouge/reporting.py'
app=app_path.read_bytes();report=report_path.read_bytes()
assert sha(app)=='fa27d6eceaf88f8caf1bc4e994641c6d110884ee9fbf673ab7d46a355cc41143'
assert sha(report)=='b71dec77a7cb7ba88da7324982be6f4fd59c02ae8cd91bce44fe92f3546f5d01'
assert any(r['archive_path']=='candidate/rouge/app.py' and r['sha256']==sha(app) and r['bytes']==len(app) for r in json.loads(ui_mf)['files'])
assert any(r['path']=='draft-tree/rouge/reporting.py' and r['sha256']==sha(report) and r['bytes']==len(report) for r in json.loads(deep_mf)['artifacts'])
assert app.count(b'\n')==app.count(b'\r\n') and b'\r\n' not in report
for rel,content in [('rouge/app.py',app),('rouge/reporting.py',report)]:
    dest=HERE/'prospective91-base'/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(content)
put('prospective-base-binding.json',{
    'format_version':1,'status':'PROSPECTIVE_FROZEN91_AUTHOR_BASE_NOT_ACTUAL_ROOT91_COMMIT',
    'actual_source_research_root':'2cbc45f03f99ed4f04b9c7e2612b58542f909168',
    'actual_root91_commit':'PENDING; source transport must verify after root91 validation/commit',
    'sources':[
        {'source_path':str(app_path),'archive_path':'prospective91-base/rouge/app.py','bytes':len(app),'sha256':sha(app),'origin_manifest_sha256':sha(ui_mf)},
        {'source_path':str(report_path),'archive_path':'prospective91-base/rouge/reporting.py','bytes':len(report),'sha256':sha(report),'origin_manifest_sha256':sha(deep_mf)}],
    'source33_manifest':{'path':str(SOURCE/'public-source-manifest.json'),'sha256':sha(source_mf)},
    'source33_immutable':True,'91_author_materials_immutable':True,
    'only_selected_foreign_product_leaf_hashes_verified':'Not a rerun of91 review/API/saved/source matrices or 271whole inventory',
    'no_tracked_or_API_Qt_Wine_tests':True})

window_tip='只改变当前技能模型的观察范围，不把输入秒数当作技能持续时间；实际已计窗口见报告。已计窗口为0秒时不计算窗口平均DPS/HPS，未定位来源与未知回转仍保持原说明。'
timing_tip=('秒数以技能开启为0；初动使用initial_target_windows等独立部署时间轴。此处为测试情景，当前尚未从战斗画面自动跟踪。'
            '动画参考值会自动加载；不要在这里填写培养属性。区间按30Hz模拟帧换算，换算后结束须晚于开始。'
            '关闭逐帧时，常规连续攻击参考不按供靶/移动/中断区间逐帧调度；目标消失声明和友方潜在治疗仍按已有范围处理，未知时钟不补算。')
app_changes=[(
    "        self.window_seconds = number(40,3600,2)\r\n"
    "        self.limit_window = QCheckBox('使用指定输出窗口（秒）')\r\n"
    "        form.addRow(self.limit_window,self.window_seconds)\r\n",
    "        self.window_seconds = number(40,3600,2)\r\n"
    "        self.limit_window = QCheckBox('使用指定观察窗口（秒）')\r\n"
    f"        self.limit_window.setToolTip('{window_tip}')\r\n"
    f"        self.window_seconds.setToolTip('{window_tip}')\r\n"
    "        self.limit_window.toggled.connect(lambda:self.calculate())\r\n"
    "        self.window_seconds.valueChanged.connect(lambda:self.calculate())\r\n"
    "        form.addRow(self.limit_window,self.window_seconds)\r\n"
),(
    "        self.timing_scenario.setToolTip('秒数以技能开启为0；初动使用initial_target_windows等独立部署时间轴。此处为测试情景，当前尚未从战斗画面自动跟踪。动画参考值会自动加载；不要在这里填写培养属性。')\r\n",
    f"        self.timing_scenario.setToolTip('{timing_tip}')\r\n"
)]
report_changes=[(
    "            if skill.get('window_seconds'):\n"
    "                rows.append(metric('window_seconds','伤害观察窗口',skill['window_seconds'],'秒'))\n"
    "                rows.append(metric('window_dps','情景平均伤害参考' if result.get('charge_reference') else '窗口平均 DPS',\n",
    "            if skill.get('window_seconds') is not None:\n"
    "                rows.append(metric('window_seconds','伤害观察窗口',skill['window_seconds'],'秒'))\n"
    "            if skill.get('window_seconds'):\n"
    "                rows.append(metric('window_dps','情景平均伤害参考' if result.get('charge_reference') else '窗口平均 DPS',\n"
),(
    "            rows.append(metric('window_healing','观察窗口治疗',window_healing))\n"
    "            if skill.get('window_seconds'):\n",
    "            rows.append(metric('window_healing','观察窗口治疗',window_healing))\n"
    "            if skill.get('window_seconds') is not None:\n"
    "                rows.append(metric('window_seconds','治疗观察窗口',skill['window_seconds'],'秒'))\n"
    "            if skill.get('window_seconds'):\n"
)]
patch='';proofs=[]
for rel,before,changes in [('rouge/app.py',app,app_changes),('rouge/reporting.py',report,report_changes)]:
    after=before
    for old,new in changes:
        assert after.count(old.encode())==1,(rel,old)
        after=after.replace(old.encode(),new.encode(),1)
    inverse=after
    for old,new in reversed(changes):
        assert inverse.count(new.encode())==1
        inverse=inverse.replace(new.encode(),old.encode(),1)
    assert inverse==before
    old_ast=ast.parse(before.decode());new_ast=ast.parse(after.decode())
    assert ast.dump(ast.parse(inverse.decode()),include_attributes=False)==ast.dump(old_ast,include_attributes=False)
    if rel.endswith('app.py'):
        old_cls=next(n for n in old_ast.body if isinstance(n,ast.ClassDef) and n.name=='MainWindow')
        new_cls=next(n for n in new_ast.body if isinstance(n,ast.ClassDef) and n.name=='MainWindow')
        old_methods={n.name:n for n in old_cls.body if isinstance(n,ast.FunctionDef)}
        new_methods={n.name:n for n in new_cls.body if isinstance(n,ast.FunctionDef)}
        changed=[name for name in old_methods if ast.dump(old_methods[name],include_attributes=False)!=ast.dump(new_methods[name],include_attributes=False)]
        assert changed==['make_damage_tab']
        assert after.count(b'\n')==after.count(b'\r\n')
        assert before.count(b'self.window_seconds.setValue(')==after.count(b'self.window_seconds.setValue(')==0
        assert before.count(b'self.limit_window.setChecked(')==after.count(b'self.limit_window.setChecked(')==0
        assert b"self.continuous_attacks.toggled.connect(lambda:self.calculate())" in after
        unchanged_calculate_AST=True
    else:
        old_functions={n.name:n for n in old_ast.body if isinstance(n,ast.FunctionDef)}
        new_functions={n.name:n for n in new_ast.body if isinstance(n,ast.FunctionDef)}
        changed=[name for name in old_functions if ast.dump(old_functions[name],include_attributes=False)!=ast.dump(new_functions[name],include_attributes=False)]
        assert changed==['build_report']
        assert b'\r\n' not in after
        unchanged_calculate_AST='Not a numerical engine file; existing positive-average arithmetic text kept'
    dest=HERE/'candidate'/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(after)
    patch+=''.join(difflib.unified_diff(before.decode().splitlines(keepends=True),after.decode().splitlines(keepends=True),fromfile='a/'+rel,tofile='b/'+rel))
    proofs.append({'source_path':str(HERE/'prospective91-base'/rel),'candidate_path':str(dest),'old_sha256':sha(before),'new_sha256':sha(after),
                   'old_bytes':len(before),'new_bytes':len(after),'exact_byte_inverse':True,'whole_AST_inverse':True,
                   'only_changed_functions':changed,'unchanged_numerical_calculate':unchanged_calculate_AST,
                   'replacement_blocks':len(changes)})
(HERE/'candidate-flow.patch').write_bytes(patch.encode())
put('candidate-static-proof.json',{'status':'EXTERNAL_PROSPECTIVE_CANDIDATE_SOURCE_AST_PASS_NOT_RUNTIME_OR_FORMAL',
                                 'products':proofs,'patch_sha256':sha(patch.encode()),'patch_bytes':len(patch.encode()),
                                 'report_scope':'New length metric uses existing effective value, including0; same old outer section qualification and strictly-positive denominator guard. Report intentionally changes; numerical/model/unknown/timing fields do not.',
                                 'window_label':'使用指定观察窗口（秒）','window_tooltip':window_tip,'timing_tooltip':timing_tip,
                                 'source33_final_unchanged':True,'91_app_reporting_changes_preserved_by_prospective_base':True,
                                 'guards_and_prepare_engine_unchanged':'No candidate changes to engine/damage/estimate/timing/condition_inputs/prepare/registry',
                                 'API_helper_formatter_tests_Qt_Wine_calls':0,
                                 'pending':'Actualroot91 transport, parent scope/budget, formal review, current checks and actual window validation; no candidate execute now'})
print(json.dumps({'status':'PROSPECTIVE_FLOW_CANDIDATE_SOURCE_PASS','products':proofs,'patch_sha256':sha(patch.encode()),'new_calls':0}))
