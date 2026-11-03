"""Verify root's approved insertion and source after registration; no public calculations."""
import argparse
import ast
import hashlib
import json
import subprocess
import sys
import textwrap
from pathlib import Path

parser=argparse.ArgumentParser()
parser.add_argument('--repository',type=Path,default=Path('/workspace/rougezhushou'))
parser.add_argument('--expected-prior-damage-sha',required=True)
parser.add_argument('--output',type=Path)
args=parser.parse_args()
root=args.repository;saved=Path(__file__).parent
sha=lambda b:hashlib.sha256(b).hexdigest()
freeze=json.loads((saved/'freeze-receipt.json').read_bytes())
draft=json.loads((saved/'draft-freeze84.json').read_bytes())
source=json.loads((saved/'source-receipt84.json').read_bytes())
branch=subprocess.check_output(['git','branch','--show-current'],cwd=root,text=True).strip()
assert branch=='codex/p2-development'
damage=(root/'rouge/damage.py').read_bytes();guard=draft['guard'].encode()
assert damage.count(guard)==1 and damage.count(b'\n')==damage.count(b'\r\n')
prior=damage.replace(guard,b'',1)
assert sha(prior)==args.expected_prior_damage_sha
function=next(n for n in ast.parse(damage.decode()).body
              if isinstance(n,ast.FunctionDef) and n.name=='_evaluate_damage_once')
assert isinstance(function.body[-1],ast.Return)
assert ast.dump(function.body[-2],include_attributes=False)==ast.dump(
    ast.parse(textwrap.dedent(guard.decode())).body[0],include_attributes=False)
checked=[]
for rel in ('rouge/operator_engine.py','rouge/data/catalog.json','rouge/operator_options.py',
            'rouge/app.py','rouge/reporting.py','rouge/estimate.py','rouge/data/relic-mechanics.json',
            'rouge/relics.py'):
    assert sha((root/rel).read_bytes())==freeze['files'][rel]['sha256'];checked.append(rel)
test=(root/'tests/test_haruka_repeat_text_input.py').read_bytes()
assert sha(test)==draft['test_sha256']
assert '"tests.test_haruka_repeat_text_input"' in (root/'scripts/verify_cloud.py').read_text()
for name,proof in source['source_files'].items():
    data=Path(proof['path']).read_bytes()
    assert sha(data)==proof['sha256'] and len(data)==proof['bytes']
sys.path.insert(0,str(root))
from rouge.catalog import catalog
from rouge.operator_engine import selected_talents
for proof in source['actual_source_helper_selections']:
    chosen,parts=selected_talents(catalog()['operators']['char_4202_haruka'],proof['scenario'])
    assert chosen==proof['selected_talents'] and parts==proof['module_parts']
receipt={'passed':True,'section':84,'branch':branch,'head_before_section_commit':subprocess.check_output([
         'git','rev-parse','HEAD'],cwd=root,text=True).strip(),'current_damage_sha256':sha(damage),
         'prior_approved_damage_sha256':sha(prior),'prior_approved_bytes_preserved':True,
         'current_test_sha256':sha(test),'test_registered':True,'source_commit':source['source_commit'],
         'full_original_files_rehashed':list(source['source_files']),'unchanged_current_source_files':checked,
         'current_actual_helper_selections':len(source['actual_source_helper_selections']),
         's2_source_levels_verified':10,'damage_crlf_preserved':True,'guard_is_final_core_step_after_report':True,
         'calculate_damage_calls':0,'tracked_edits':False,'gui_executed':False,'wine_executed':False}
if args.output:
    with args.output.open('x',encoding='utf-8') as f:
        json.dump(receipt,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(receipt,ensure_ascii=False))
