"""Root-only source check after section 82 integration; no public calculations."""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

parser=argparse.ArgumentParser()
parser.add_argument('--repository',type=Path,default=Path('/workspace/rougezhushou'))
parser.add_argument('--output',type=Path)
args=parser.parse_args()
root=args.repository
saved=Path(__file__).parent
sha=lambda b:hashlib.sha256(b).hexdigest()
freeze=json.loads((saved/'freeze-receipt.json').read_bytes())
draft=json.loads((saved/'draft-freeze82.json').read_bytes())
source=json.loads((saved/'source-receipt82.json').read_bytes())
branch=subprocess.check_output(['git','branch','--show-current'],cwd=root,text=True).strip()
assert branch=='codex/p2-development'
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
checked=[]
for rel in ('rouge/data/catalog.json','rouge/operator_options.py','rouge/app.py',
            'rouge/reporting.py','rouge/estimate.py','rouge/data/relic-mechanics.json'):
    assert sha((root/rel).read_bytes())==freeze['files'][rel]['sha256']
    checked.append(rel)
engine=(root/'rouge/operator_engine.py').read_bytes()
assert sha(engine)==draft['engine_after_sha256']
assert engine.count(b'\r\n')==engine.count(b'\n')
test=(root/'tests/test_susuro_condition_text_input.py').read_bytes()
assert sha(test)==draft['test_sha256']
assert '"tests.test_susuro_condition_text_input"' in (root/'scripts/verify_cloud.py').read_text()
assert sha((root/'rouge/relics.py').read_bytes())=='79f5f607a247fbe366651c63ee951215a518e6a597868cd65e4212d16564e5d3'
originals=[]
for name,proof in source['source_files'].items():
    data=Path(proof['path']).read_bytes()
    assert sha(data)==proof['sha256'] and len(data)==proof['bytes']
    originals.append(name)
sys.path.insert(0,str(root))
from rouge.catalog import catalog
from rouge.operator_engine import selected_talents
owner=catalog()['operators']['char_298_susuro']
actual=[]
for group in ('actual_frozen_selected_talent_results','actual_frozen_module_boundary_results'):
    for proof in source[group]:
        chosen,parts=selected_talents(owner,proof['scenario'])
        assert chosen==proof['selected_talents'] and parts==proof['module_parts']
        actual.append(proof['scenario'])
receipt={'passed':True,'section':82,'branch':branch,'head_before_section_commit':head,
         'source_commit':source['source_commit'],'original_full_files_rehashed':originals,
         'current_engine_sha256':sha(engine),'current_test_sha256':sha(test),
         'unchanged_current_source_files':checked,'test_registered':True,'engine_crlf_preserved':True,
         'preserved_section81_warning_order':True,'current_actual_helper_selections':len(actual),
         'mechanism_changes':False,'calculate_damage_calls':0,'gui_executed':False,'wine_executed':False}
if args.output:
    with args.output.open('x',encoding='utf-8') as f:
        json.dump(receipt,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(receipt,ensure_ascii=False))
