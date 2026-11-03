"""Independent fixed-byte static design verification; no app/API/Qt/Wine import."""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import ast, hashlib, json, subprocess

R=Path('/workspace/rougezhushou'); A=Path('/workspace/.continuation/ui-085-draft'); O=A/'review-design'
RUNNER_SHA='fcbd4225094d813bb5f68d52242c53753f98297d01f544b8b146de8d44c3d271'
BASE_SHA='c58ff7ac462e7a9aa457e4b59471a162cbf5c6daf58192f6b5a852901fcdcc98'
PREP_SHA='9469c36950c96d80422041b63fb917d43c39349b3072137961f3acdc3f901f58'
def sha(b):return hashlib.sha256(b).hexdigest()
def save_json(name,data):
 p=O/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def copy(src,name):
 b=src.read_bytes();dest=O/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(b);assert dest.read_bytes()==b
 return {'source_path':str(src),'snapshot_path':str(dest),'bytes':len(b),'sha256':sha(b)}
# Never modify completed preparation artifacts.
assert sha((A/'review-prep/manifest.json').read_bytes())==PREP_SHA
prep=json.loads((A/'review-prep/manifest.json').read_bytes())
for row in prep['files']:
 b=Path(row['source_path']).read_bytes();assert sha(b)==row['sha256']and len(b)==row['bytes']

runner=(A/'wine-ui-smoke-085.py').read_bytes();base=Path('/workspace/.compat/wine-ui-smoke-080.py').read_bytes()
assert sha(runner)==RUNNER_SHA and sha(base)==BASE_SHA
ast.parse(runner);ast.parse(base)
snapshots={name:copy(A/name,'candidate/'+name)for name in ('wine-ui-smoke-085.py','cases085.py','public_contracts.py','supplemental-checks.py.fragment','build_runner.py','runner-static-review.json','source-control-design.json')}
snapshots['actual080']=copy(Path('/workspace/.compat/wine-ui-smoke-080.py'),'actual080.py')
for source in sorted((A/'preparation081-explicit-mechanist-charge').iterdir()):
 if source.is_file():copy(source,'original-charge-implicit-candidate/'+source.name)

text=runner.decode();old=base.decode();helpers=(A/'public_contracts.py').read_text()+'\n'+(A/'cases085.py').read_text()
fragment=(A/'supplemental-checks.py.fragment').read_text()
entry="if __name__ == '__main__' and True:\n    raise RuntimeError('UI085 final source/schema are pending; no Qt execution is permitted')\n\n"
assert text.startswith(entry)
assert text.count(fragment+'\n')==1 and text.count(helpers+'\n\n')==1
restored=text[len(entry):].replace(fragment+'\n','',1).replace(helpers+'\n\n','',1)
for name in ('wine-ui-report-difference-080.json','wine-window-080.png','wine-ui-080.json','wine-ui-failure-080.png','wine-sown-tile-control-080.png','wine-movement-reference-080.png','wine-medical-trait-080.png'):
 restored=restored.replace(name.replace('-080','-085'),name)
for key in ('preserved_old_checks','preserved_full_060_checks','preserved_full_065_checks','preserved_full_070_checks','preserved_full_075_checks'):
 line=next(line for line in old.splitlines()if line.strip().startswith(f"receipt['{key}']=len(checks)"))
 assert restored.count(line+'-(group085_end-group085_start)')==1
 restored=restored.replace(line+'-(group085_end-group085_start)',line,1)
added="        receipt['preserved_full_080_checks']=len(checks)-(group085_end-group085_start)\n        assert receipt['preserved_full_080_checks']==3063,receipt['preserved_full_080_checks']\n"
assert restored.count(added)==1;restored=restored.replace(added,'',1)
assert restored.encode()==base
assert "receipt['sections83_85_final_checks_pending']=True"in fragment
# Execute only the pure local case-data generator AST. This is not a public
# calculation/formatter call; function contains literals, loops and add only.
tree=ast.parse((A/'cases085.py').read_bytes())
assert not any(isinstance(n,(ast.Import,ast.ImportFrom))for n in ast.walk(tree))
namespace={};exec(compile(tree,'pure-case-design085','exec'),namespace)
cases=namespace['cases085']();counts=dict(Counter(case['section']for case in cases))
assert counts=={81:136,82:216}
cat=json.loads((R/'rouge/data/catalog.json').read_bytes());order=list(cat['relics'])
anchors=set();anchor_pairs=0
for case in cases:
 s=case['input'];profile=cat['operators'][s['operator']]
 assert 1<=s['level']<=profile['phases'][s['elite']]['max_level']
 assert profile['skills'][s['skill']-1]['unlock_elite']<=s['elite']
 assert s['elite']==2 or s['skill_rank']<=7
 assert type(s['healing_targets'])is int and s['healing_targets']in (0,1)
 assert sorted(s['relic_ids'],key=order.index)==s['relic_ids']and len(set(s['relic_ids']))==len(s['relic_ids'])
 if s['operator']=='mechanist':assert type(s['charge_count'])is int and s['charge_count']==0
 if case['section']==82:
  assert type(s['low_cost_healing_target'])is bool
  if s['skill']==2:assert type(s['casts_used'])is int and s['casts_used']in (0,1)
  else:assert 'casts_used'not in s
  anchor=json.dumps({k:v for k,v in s.items()if k!='low_cost_healing_target'},sort_keys=True)
  if not s['low_cost_healing_target']:anchors.add(anchor)
  else:assert anchor in anchors;anchor_pairs+=1
assert anchor_pairs==108
# Verify every required estimate.skill key against its real production Dict AST.
engine=(R/'rouge/operator_engine.py').read_bytes();e=ast.parse(engine)
estimate=next(n.value for n in ast.walk(e)if isinstance(n,ast.Assign)and isinstance(n.value,ast.Dict)and any(isinstance(t,ast.Subscript)and isinstance(t.value,ast.Name)and t.value.id=='result'and isinstance(t.slice,ast.Constant)and t.slice.value=='estimate'for t in n.targets))
skill=next(value for key,value in zip(estimate.keys,estimate.values)if isinstance(key,ast.Constant)and key.value=='skill')
actual_keys={key.value for key in skill.keys if isinstance(key,ast.Constant)}
required={'mode','initial_seconds','recharge_seconds','cycle_seconds','duration_seconds','sp_recovery_per_second','hit_counts','total_healing','phase_healing','window_healing','window_hps','cycle_healing','cycle_hps'}
assert required<=actual_keys
source_records={name:copy(R/'rouge'/name,'production/'+name)for name in ('app.py','catalog.py','damage.py','operator_options.py','operator_engine.py','reporting.py','relics.py','timing.py')}
for row in snapshots.values():assert sha(Path(row['source_path']).read_bytes())==row['sha256']
assert sha((A/'wine-ui-smoke-085.py').read_bytes())==RUNNER_SHA
assert sha((A/'review-prep/manifest.json').read_bytes())==PREP_SHA
save_json('design-review085.json',{
 'scope':'Independent fixed-byte static review of pending81/82 UI085 design; application/API/formatter/Qt/Wine executions=0. Pure local case-data generator enumerated352 planned rows, not352 calculation passes.',
 'passed_static_design_review':True,'created_utc':datetime.now(timezone.utc).isoformat(),'candidate_sha256':RUNNER_SHA,'base_actual080_sha256':BASE_SHA,
 'old_actual080_3063_complete_body_reconstructed_exactly':True,'case_design_count_by_section':counts,'new_planned_rows':len(cases),'planned_total_including_old':3063+len(cases),
 'false_before_true_anchor_pairs':108,'candidate_snapshot_hashes':snapshots,'production_source_snapshots':source_records,
 'production_estimate_skill_keys_required':sorted(required),'production_estimate_skill_keys_present':sorted(actual_keys),
 'root_HEAD_at_read':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),
 'findings':[
  {'id':'81-list-order','status':'static_pass','evidence':'QListWidget appends catalog items; calculate scans real item indexes and filter only hides. All136 design rows preserve exact catalog selected-ID order, no unknown/duplicate/reverse synthetic Qt items.'},
  {'id':'81-presentation','status':'static_pass','evidence':'Default report deduplicates original warnings before anonymous phrase, so two distinct unknown groups render two identical lines; technical retains original exact groups. Contract checks both and preserved exclusions/statuses.'},
  {'id':'81-explicit-charge','status':'static_pass','evidence':'Original080 charge_count last explicit write0 at line1205, so initialcandidate was state-dependent rather than a confirmed failure. Revised81 mechanist S3 case supplies explicit0 to genuine QSpinBox0..100 and checks real int producer; oldcandidate/reason preserved.'},
  {'id':'82-field-contract','status':'static_pass','evidence':'All13 helper estimate.skill keys exist in actual production dictionary. Susuro plans regular healing and use actual selected 微创治疗 coefficient; no hardcoded base_attack or mechanism factor.'},
  {'id':'82-null-cycle','status':'static_pass','evidence':'Existing casts_used1 marks nonrepeat and cycle=None, derived cycle_healing/cycle_hps=None; helper preserves None before arithmetic and explicitly asserts cycleSeconds/healingNone.'},
  {'id':'82-friendly-scope','status':'static_pass','evidence':'Both modes build friendly regular AttackTimeline children and retain target_scope_notes; annotate_result appends these in continuous too. Empty enemy inputs do not assert healing0; helper asks existing friendly clock unknown. Only friend0 or window0 is mathematical exclusion.'},
  {'id':'82-real-producers','status':'static_pass','evidence':'Checkbox onlybool F/T; casts actualint0/1, range0..2 declared but2 error not claimednewactualtest. S1 hidden casts omitted. readonly elite/module/rank public observation, actual level control; E0S2 excluded, PHY-X39/40 gate, potential5 exact source.'},
  {'id':'old-body-and-guard','status':'static_pass','evidence':'Independent removal of exact new helpers/fragment/prefix/counter wrappers/output renames reconstructs every base080 byte. True entry rejection precedes imports/Qt. Pending83–85True remains hardassert later.'}
 ],
 'limitations':['No calculate_damage/prepare/format_report call, test suite, Qt/Wine/nativeWindows/gameexecution.','Section82 original/draft formal source remains pending; this checks current production schema and existing bool paths only, not repaired APIstrings.','Section83–85 absent; runner remains blocked before import.','Final root85 fixed source compatibility and saved public API results still require independent formal review.','Readonly public observation injection never proves actual account/OCR/recipient/clock/native stacking.'],
 'ready_for_API_or_actual_UI_execution':False,'prep15_artifacts_unchanged':True})
save_json('preparation-diagnostics085.json',{'read_only_preparation_errors':[
 {'exit_code':2,'scope':'file discovery','cause':'Guessed public_contracts085.py and fragment085.txt filenames absent; actualfiles public_contracts.py and supplemental-checks.py.fragment read next.','API_or_dependent_runs':0},
 {'exit_code':2,'scope':'source rg','cause':'Guessed rouge/input_conditions.py absent; actual damage.py and operator_engine.py read.','API_or_dependent_runs':0}],
 'static_product_findings_failed':0,'application_API_calls':0,'Qt_Wine_calls':0,'revised_candidate_reason':'Explicit charge0 real producer avoids hidden old-state dependence; no observed runtime/productfailure.'})
(O/'NOTE.md').write_text('81–82当前pending设计固定SHA '+RUNNER_SHA+'，独立静态审通过。完整逆向逐字节恢复实际080旧3063项正文；352新设计行81=136/82=216，108个false先于true配对，计数不代表计算通过。\n\n13个estimate.skill契约字段均有实际生产AST证据；None周期、真实bool/int和隐藏非活跃键、空敌方保留友方时钟未知的说明链均正确。初稿mechanist依赖旧控件残留0的边界已用真实显式charge0及int断言完善，原稿理由保留，没有伪报API/Qt失败。\n\n82来源formal与83–85仍待完成；入口True保护在import前，因此绝不能执行本pendingrunner。此审查没有应用API、formatter、Qt、Wine或游戏调用。旧review-prep15附件未改动，新的两次只读错误路径诊断独立保留。\n',encoding='utf-8')
paths=sorted(p for p in O.rglob('*')if p.is_file()and p.name!='manifest.json')
save_json('manifest.json',{'format_version':1,'files':[{'source_path':str(p),'archive_path':p.relative_to(O).as_posix(),'bytes':len(p.read_bytes()),'sha256':sha(p.read_bytes())}for p in paths]})
for row in json.loads((O/'manifest.json').read_bytes())['files']:
 b=Path(row['source_path']).read_bytes();assert sha(b)==row['sha256']and len(b)==row['bytes']
print(json.dumps({'passed_static_design':True,'candidate_sha256':RUNNER_SHA,'review_sha256':sha((O/'design-review085.json').read_bytes()),'manifest_sha256':sha((O/'manifest.json').read_bytes()),'files':len(paths),'old3063_preserved':True,'new_planned_rows':len(cases),'API_calls':0,'Qt_Wine_calls':0},ensure_ascii=False))
