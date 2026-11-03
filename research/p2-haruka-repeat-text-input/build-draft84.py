import hashlib
import json
import shutil
from pathlib import Path

OUT=Path(__file__).parent
freeze=json.loads((OUT/'freeze-receipt.json').read_bytes())
assert json.loads((OUT/'source-receipt84.json').read_bytes())['passed']
for rel,proof in freeze['files'].items():
    assert hashlib.sha256((OUT/'frozen'/rel).read_bytes()).hexdigest()==proof['sha256']
draft=OUT/'draft'
assert not draft.exists()
shutil.copytree(OUT/'frozen',draft,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
p=draft/'rouge/damage.py';before=p.read_bytes()
anchor="    result['report']=build_report(scenario,result)\r\n    return result\r\n\r\ndef _evaluate_damage(prepared".encode()
assert before.count(anchor)==1
guard=("    if scenario['operator']=='char_4202_haruka' and scenario['skill']==2 and isinstance(scenario.get('haruka_repeat'),str):\r\n"
       "        raise ValueError('haruka_repeat 不接受文本条件；请使用布尔值。')\r\n").encode()
after=before.replace(anchor,anchor.replace(b'    return result\r\n',guard+b'    return result\r\n',1))
p.write_bytes(after)
assert before.count(b'\n')==before.count(b'\r\n') and after.count(b'\n')==after.count(b'\r\n')
test=OUT/'test_haruka_repeat_text_input.py'
shutil.copyfile(test,draft/'tests'/test.name)
for rel,proof in freeze['files'].items():
    if rel!='rouge/damage.py':assert hashlib.sha256((draft/rel).read_bytes()).hexdigest()==proof['sha256']
receipt={'passed':True,'baseline_commit':freeze['baseline_commit'],'baseline_public_files':len(freeze['files']),
         'unchanged_old_files':len(freeze['files'])-1,'changed_old_file':'rouge/damage.py',
         'damage_before_sha256':hashlib.sha256(before).hexdigest(),'damage_after_sha256':hashlib.sha256(after).hexdigest(),
         'test_sha256':hashlib.sha256(test.read_bytes()).hexdigest(),'guard':guard.decode(),
         'insertion_location':'_evaluate_damage_once after existing build_report and any approved83 guards, before final return',
         'exact_insertion_scope':'No old whole damage source is transported to root; adapt surgical hunk after83 final bytes.',
         'crlf_preserved':True,'new_calculate_calls':0,'tracked_edits':False,'gui_executed':False,'wine_executed':False}
(OUT/'draft-freeze84.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(receipt,ensure_ascii=False))
