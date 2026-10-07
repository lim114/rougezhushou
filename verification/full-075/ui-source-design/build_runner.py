"""Build external actual Qt runner. Root exclusively executes it under Wine."""
import ast,difflib,hashlib,json
from collections import Counter
from pathlib import Path
P=Path(__file__).resolve().parent
BASE=Path('/workspace/.compat/wine-ui-smoke-070.py')
EXPECTED='3bba0d28376165b84938906b45048f31b75d89cf6e1c4d1e5246d17f6272f9b3'
raw=BASE.read_bytes();assert hashlib.sha256(raw).hexdigest()==EXPECTED
(P/'wine-ui-smoke-070-preserved.py').write_bytes(raw)
base=raw.decode();helpers=(P/'public_contracts.py').read_text()+'\n'+(P/'cases075.py').read_text()
fragment=(P/'supplemental-checks.py.fragment').read_text()
marker='        # Final visible screenshot scenario demonstrates the restored explanation.\n'
assert base.count(marker)==1
text=base.replace(marker,fragment+'\n'+marker)
assert text.count('def source_hashes():')==1
text=text.replace('def source_hashes():',helpers+'\n\ndef source_hashes():',1)
for old in (
    "receipt['preserved_old_checks']=len(checks)-(supplemental_end-supplemental_start)-(new_end-new_start)-(latest_end-latest_start)",
    "receipt['preserved_full_060_checks']=len(checks)-(new_end-new_start)-(latest_end-latest_start)",
    "receipt['preserved_full_065_checks']=len(checks)-(latest_end-latest_start)"):
    assert text.count(old)==1,old;text=text.replace(old,old+'-(current_end-current_start)')
old="        receipt['total_actual_checks']=len(checks)"
new="        receipt['preserved_full_070_checks']=len(checks)-(current_end-current_start)\n        assert receipt['preserved_full_070_checks']==841,receipt['preserved_full_070_checks']\n"+old
assert text.count(old)==1;text=text.replace(old,new)
renames={name:name.replace('-070','-075') for name in ('wine-ui-report-difference-070.json',
    'wine-window-070.png','wine-ui-070.json','wine-ui-failure-070.png','wine-sown-tile-control-070.png')}
for old,new in renames.items():text=text.replace(old,new)
ast.parse(text)
target=P/'wine-ui-smoke-075.py';target.write_text(text)
diff=''.join(difflib.unified_diff(base.splitlines(keepends=True),text.splitlines(keepends=True),
    fromfile='wine-ui-smoke-070.py',tofile='wine-ui-smoke-075.py'))
(P/'runner-075.patch').write_text(diff)
# Independently reconstruct the base, allowing only filename/counter wrappers.
rebuilt=text.replace(fragment+'\n','',1).replace(helpers+'\n\n','',1)
for old,new in renames.items():rebuilt=rebuilt.replace(new,old)
rebuilt=rebuilt.replace("-(current_end-current_start)","")
rebuilt=rebuilt.replace("        receipt['preserved_full_070_checks']=len(checks)\n        assert receipt['preserved_full_070_checks']==841,receipt['preserved_full_070_checks']\n",'')
assert rebuilt==base,'Prior841 source changed beyond explicit wrappers'
from cases075 import cases075,preview_cases075
data=json.loads(Path('/workspace/rougezhushou/rouge/data/run-config.json').read_bytes())
counts=Counter(row['section'] for row in cases075(data['squads']))
battle=json.loads(Path('/workspace/rougezhushou/rouge/data/battle-previews.json').read_bytes())
counts.update(row['section'] for row in preview_cases075(battle['stages']))
pending="receipt['section75_final_checks_pending']=True" in text
receipt={'scope':'Static construction only; actual Qt/Wine requires root receipt',
    'base070_sha256':EXPECTED,'base_actual_checks':841,'base_skills':87,
    'prior841_body_preserved':True,'syntax_valid':True,'case_design_by_section':dict(counts),
    'new_case_design_count':sum(counts.values()),'total_case_design_count':841+sum(counts.values()),
    'section75_final_checks_pending':pending,'ready_for_actual_execution':not pending,
    'gui_executed':False,'wine_executed':False,'runner_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
    'diff_sha256':hashlib.sha256((P/'runner-075.patch').read_bytes()).hexdigest()}
(P/'runner-static-review.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(receipt,ensure_ascii=False))
