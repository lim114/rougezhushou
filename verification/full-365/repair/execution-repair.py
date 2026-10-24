"""Execute only after original365 attempt1 genuinely terminates and is archived."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,subprocess,ast
R=Path(__file__).resolve().parents[1]
def read(name):return json.loads((R/name).read_bytes())
archive=read('verification/full-365/execution-attempt1/archive-manifest.json')
assert archive['all_executed_retained_Popen_and_assigned_jobs_terminal'] is True
original=read('verification/full-365/execution-attempt1/offline/actual/windows-offline.json')
assert original['failures']==1 and original['errors']==0 and len(original['failed_cases'])==1
assert original['failed_cases'][0]['test']=='tests.test_expansion_reference_313.ExpansionReference313Tests.test_official_label_and_legacy_limits_are_explicit_not_DLC2_or_current_calibration'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R).decode().strip()=='23215171e35900a1b75aebb44e66d4bf657f267a'
p=R/'tests/test_expansion_reference_313.py';before=p.read_bytes();s=before.decode('utf8')
old="        self.assertIn('内容拓展·一',model.NOTICE);self.assertIn('尚未整体迁移',model.NOTICE)"
assert s.count(old)==1
new="""        self.assertIn('内容拓展·一',model.NOTICE)
        self.assertIn('固定资料',model.NOTICE);self.assertIn('须按对应条件确认',model.NOTICE)
        self.assertIn('以该项结果旁注明的适用范围为准',model.NOTICE)
        self.assertIn('更新前的固定基准',model.LEGACY_NOTICE)
        self.assertIn('数值计算和位置映射尚未完整适配',model.LEGACY_NOTICE)"""
s=s.replace(old,new);ast.parse(s)
out=R/'verification/full-365/repair';out.mkdir()
(out/'before-test_expansion_reference_313.py').write_bytes(before)
p.write_bytes(s.encode('utf8'))
receipt={'section':365,'kind':'maintenance_within_functional365_no_new_section',
 'reason':'The old313 test incorrectly kept the old standalone-version NOTICE wording after352 moved fixed references to ordinary pages. Verify the new general notice and the separate real legacy-calculation notice without deleting any applicability or unknown boundary.',
 'original_failure':'verification/full-365/execution-attempt1/offline/actual/windows-offline.json',
 'files':{'tests/test_expansion_reference_313.py':{'before_sha256':sha256(before).hexdigest(),'after_sha256':sha256(p.read_bytes()).hexdigest()}},
 'product_code_data_or_mechanism_modified':False,'test_methods_or_selectors_removed':False,
 'packet_baseline_and_position_not_migrated_assertions_preserved':True,
 'new_assertions_executed':False,'at_UTC':datetime.now(timezone.utc).isoformat()}
(out/'repair-scope.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(out/'execution-repair.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({'repair_applied_not_validated':True,'changed_test_only':True}))
