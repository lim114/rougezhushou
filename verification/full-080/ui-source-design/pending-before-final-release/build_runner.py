"""Build external Qt candidate, preserving proven075 and forbidding early execution."""
import ast,difflib,hashlib,json
from collections import Counter
from pathlib import Path
P=Path(__file__).resolve().parent;BASE=Path('/workspace/.compat/wine-ui-smoke-075.py')
EXPECTED='645ebd2e90ab3aef1fa5c9318300bd5e690c5f1dd6cfb67f94ed74f355ca4f03'
raw=BASE.read_bytes();assert hashlib.sha256(raw).hexdigest()==EXPECTED
(P/'wine-ui-smoke-075-preserved.py').write_bytes(raw)
base=raw.decode();helpers=(P/'public_contracts.py').read_text()+'\n'+(P/'cases080.py').read_text()
fragment=(P/'supplemental-checks.py.fragment').read_text()
marker='        # Final visible screenshot scenario demonstrates the restored explanation.\n'
assert base.count(marker)==1 and base.count('def source_hashes():')==1
text=base.replace(marker,fragment+'\n'+marker).replace('def source_hashes():',helpers+'\n\ndef source_hashes():',1)
for key in ('preserved_old_checks','preserved_full_060_checks','preserved_full_065_checks','preserved_full_070_checks'):
 line=next(line for line in base.splitlines()if line.strip().startswith(f"receipt['{key}']=len(checks)"))
 assert text.count(line)==1;text=text.replace(line,line+'-(next_end-next_start)')
old="        receipt['total_actual_checks']=len(checks)"
new="        receipt['preserved_full_075_checks']=len(checks)-(next_end-next_start)\n        assert receipt['preserved_full_075_checks']==1455,receipt['preserved_full_075_checks']\n"+old
assert text.count(old)==1;text=text.replace(old,new)
renames={name:name.replace('-075','-080')for name in('wine-ui-report-difference-075.json','wine-window-075.png',
 'wine-ui-075.json','wine-ui-failure-075.png','wine-sown-tile-control-075.png','wine-movement-reference-075.png')}
for old,new in renames.items():text=text.replace(old,new)
pending="receipt['sections77_80_final_checks_pending']=True"in text
entry_guard=("if __name__ == '__main__' and "+str(pending)+":\n"
             "    raise RuntimeError('UI080 final source/schema are pending; no Qt execution is permitted')\n\n")
text=entry_guard+text
ast.parse(text);target=P/'wine-ui-smoke-080.py';target.write_text(text)
(P/'runner-080.patch').write_text(''.join(difflib.unified_diff(base.splitlines(keepends=True),text.splitlines(keepends=True),
 fromfile='wine-ui-smoke-075.py',tofile='wine-ui-smoke-080.py')))
rebuilt=text.removeprefix(entry_guard).replace(fragment+'\n','',1).replace(helpers+'\n\n','',1)
for old,new in renames.items():rebuilt=rebuilt.replace(new,old)
rebuilt=rebuilt.replace('-(next_end-next_start)','')
rebuilt=rebuilt.replace("        receipt['preserved_full_075_checks']=len(checks)\n        assert receipt['preserved_full_075_checks']==1455,receipt['preserved_full_075_checks']\n",'')
assert rebuilt==base,'Proven1455 body modified beyond explicit new wrappers/outputs'
from cases080 import cases080
counts=Counter(row['section']for row in cases080())
receipt={'scope':'Static-only unfinished080 design; not Qt/Wine proof','base075_sha256':EXPECTED,'base_actual_checks':1455,
 'base_skills':87,'old1455_full_body_reconstructed_exactly':True,'syntax_valid':True,'new_case_design_by_section':dict(counts),
 'new_case_design_count':sum(counts.values()),'total_case_design_count':1455+sum(counts.values()),
 'sections77_80_pending':pending,'ready_for_actual_execution':not pending,'gui_executed':False,'wine_executed':False,
 'pending_entry_guard_before_any_import_or_Qt':True,
 'runner_sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
(P/'runner-static-review.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(receipt,ensure_ascii=False))
