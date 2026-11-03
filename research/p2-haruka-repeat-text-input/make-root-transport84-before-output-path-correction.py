"""Emit an exact insertion patch from approved current bytes; never edit the checkout."""
import argparse
import ast
import difflib
import hashlib
import json
import subprocess
from pathlib import Path

parser=argparse.ArgumentParser()
parser.add_argument('--repository',type=Path,default=Path('/workspace/rougezhushou'))
parser.add_argument('--expected-current-damage-sha',required=True)
parser.add_argument('--output-patch',type=Path,required=True)
parser.add_argument('--output-receipt',type=Path,required=True)
args=parser.parse_args()
saved=Path(__file__).parent
frozen=json.loads((saved/'draft-freeze84.json').read_bytes())
sha=lambda b:hashlib.sha256(b).hexdigest()
root=args.repository
branch=subprocess.check_output(['git','branch','--show-current'],cwd=root,text=True).strip()
assert branch=='codex/p2-development'
before=(root/'rouge/damage.py').read_bytes()
assert sha(before)==args.expected_current_damage_sha
assert before.count(b'\n')==before.count(b'\r\n')
guard=frozen['guard'].encode()
assert guard not in before
function=next(n for n in ast.parse(before.decode()).body
              if isinstance(n,ast.FunctionDef) and n.name=='_evaluate_damage_once')
assert isinstance(function.body[-1],ast.Return) and ast.unparse(function.body[-1].value)=='result'
assert any(isinstance(n,ast.Assign) and ast.unparse(n)=="result['report'] = build_report(scenario, result)"
           for n in function.body)
lines=before.splitlines(keepends=True)
offset=sum(map(len,lines[:function.body[-1].lineno-1]))
assert before[offset:].startswith(b'    return result\r\n')
after=before[:offset]+guard+before[offset:]
assert after.replace(guard,b'',1)==before
test=saved/'test_haruka_repeat_text_input.py'
test_bytes=test.read_bytes()
assert sha(test_bytes)==frozen['test_sha256']
assert not (root/'tests'/test.name).exists()
name='rouge/damage.py';test_name='tests/'+test.name
patch=('diff --git a/'+name+' b/'+name+'\n'+''.join(difflib.unified_diff(
       before.decode().splitlines(True),after.decode().splitlines(True),fromfile='a/'+name,tofile='b/'+name))+
       'diff --git a/'+test_name+' b/'+test_name+'\nnew file mode 100644\n'+''.join(difflib.unified_diff(
       [],test_bytes.decode().splitlines(True),fromfile='/dev/null',tofile='b/'+test_name)))
with args.output_patch.open('xb') as f:f.write(patch.encode())
numstat=subprocess.check_output(['git','apply','--numstat',str(args.output_patch)],cwd=root,text=True)
assert numstat.splitlines()==['2\t0\t'+name,str(len(test_bytes.splitlines()))+'\t0\t'+test_name]
check=subprocess.run(['git','apply','--check',str(args.output_patch)],cwd=root,capture_output=True,text=True)
assert check.returncode==0,check.stderr
receipt={'passed':True,'section':84,'branch':branch,'current_head':subprocess.check_output([
         'git','rev-parse','HEAD'],cwd=root,text=True).strip(),'current_damage_before_sha256':sha(before),
         'adapted_damage_after_sha256':sha(after),'guard_sha256':sha(guard),'test_sha256':sha(test_bytes),
         'patch_sha256':sha(args.output_patch.read_bytes()),'patch_numstat':numstat,'readonly_applycheck_exit':0,
         'prior_current_bytes_preserved_exact_when_two_guard_lines_removed':True,
         'insertion':'After all existing validated current guards and completed report, before function final return',
         'tracked_edits':False,'calculate_damage_calls':0,'gui_executed':False,'wine_executed':False}
with args.output_receipt.open('x',encoding='utf-8') as f:
    json.dump(receipt,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(receipt,ensure_ascii=False))
