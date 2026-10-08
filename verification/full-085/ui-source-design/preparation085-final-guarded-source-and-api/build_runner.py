"""Create pending085 candidate preserving all proven080 bytes and semantics."""
import ast,difflib,hashlib,json
from collections import Counter
from pathlib import Path
HERE=Path(__file__).resolve().parent
BASE=Path('/workspace/.compat/wine-ui-smoke-080.py')
EXPECTED='c58ff7ac462e7a9aa457e4b59471a162cbf5c6daf58192f6b5a852901fcdcc98'
raw=BASE.read_bytes();assert hashlib.sha256(raw).hexdigest()==EXPECTED
(HERE/'wine-ui-smoke-080-preserved.py').write_bytes(raw)
base=raw.decode();helpers=(HERE/'public_contracts.py').read_text()+'\n'+(HERE/'cases085.py').read_text()
fragment=(HERE/'supplemental-checks.py.fragment').read_text()
marker='        # Final visible screenshot scenario demonstrates the restored explanation.\n'
assert base.count(marker)==1 and base.count('def source_hashes():')==1
text=base.replace(marker,fragment+'\n'+marker).replace('def source_hashes():',helpers+'\n\ndef source_hashes():',1)
counter_names=('preserved_old_checks','preserved_full_060_checks','preserved_full_065_checks',
               'preserved_full_070_checks','preserved_full_075_checks')
for key in counter_names:
 line=next(line for line in base.splitlines()if line.strip().startswith(f"receipt['{key}']=len(checks)"))
 assert text.count(line)==1;text=text.replace(line,line+'-(group085_end-group085_start)')
old="        receipt['total_actual_checks']=len(checks)"
new="        receipt['preserved_full_080_checks']=len(checks)-(group085_end-group085_start)\n        assert receipt['preserved_full_080_checks']==3063,receipt['preserved_full_080_checks']\n"+old
assert text.count(old)==1;text=text.replace(old,new)
renames={name:name.replace('-080','-085')for name in ('wine-ui-report-difference-080.json','wine-window-080.png',
 'wine-ui-080.json','wine-ui-failure-080.png','wine-sown-tile-control-080.png',
 'wine-movement-reference-080.png','wine-medical-trait-080.png')}
for old,new in renames.items():text=text.replace(old,new)
pending="receipt['sections83_85_final_checks_pending']=True"in text
entry=("if __name__ == '__main__' and "+str(pending)+":\n"
       "    raise RuntimeError('UI085 final source/schema are pending; no Qt execution is permitted')\n\n")
text=entry+text;ast.parse(text)
target=HERE/'wine-ui-smoke-085.py';target.write_text(text)
(HERE/'runner-085.patch').write_text(''.join(difflib.unified_diff(base.splitlines(keepends=True),text.splitlines(keepends=True),fromfile='wine-ui-smoke-080.py',tofile='wine-ui-smoke-085.py')))
restored=text.removeprefix(entry).replace(fragment+'\n','',1).replace(helpers+'\n\n','',1)
for old,new in renames.items():restored=restored.replace(new,old)
restored=restored.replace('-(group085_end-group085_start)','')
restored=restored.replace("        receipt['preserved_full_080_checks']=len(checks)\n        assert receipt['preserved_full_080_checks']==3063,receipt['preserved_full_080_checks']\n",'')
assert restored==base,'Complete proven3063 body modified beyond new wrappers/outputs'
from cases085 import cases085
counts=Counter(row['section']for row in cases085())
receipt={'scope':'Static-only pending085 design; no API/Qt/Wine proof','base080_sha256':EXPECTED,
 'old3063_complete_body_reconstructed_exactly':True,'base_skills':87,'syntax_valid':True,
 'new_case_design_by_section':dict(counts),'new_case_design_count':sum(counts.values()),
 'total_case_design_count':3063+sum(counts.values()),'sections83_85_pending':pending,
 'pending_entry_guard_before_any_import_or_Qt':True,'ready_for_actual_execution':not pending,
 'gui_executed':False,'wine_executed':False,'runner_sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
(HERE/'runner-static-review.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(receipt,ensure_ascii=False))
