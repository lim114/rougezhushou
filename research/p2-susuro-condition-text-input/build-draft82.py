import hashlib
import json
import shutil
from pathlib import Path

OUT=Path(__file__).parent
freeze=json.loads((OUT/'freeze-receipt.json').read_bytes())
assert json.loads((OUT/'source-receipt82.json').read_bytes())['passed']
for rel,info in freeze['files'].items():
    data=(OUT/'frozen'/rel).read_bytes()
    assert hashlib.sha256(data).hexdigest()==info['sha256']
draft=OUT/'draft'
assert not draft.exists()
shutil.copytree(OUT/'frozen',draft,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
p=draft/'rouge/operator_engine.py'
before=p.read_bytes()
assert before.replace(b'\r\n',b'').count(b'\n')==0
anchor="        elif op in ('char_196_sunbr','char_2025_shu','char_298_susuro'):\r\n".encode()
assert before.count(anchor)==1
guard=("            if (op=='char_298_susuro' and '微创治疗' in self.tv and\r\n"
       "                    isinstance(self.s.get('low_cost_healing_target'),str)):\r\n"
       "                raise ValueError('low_cost_healing_target 不接受文本条件；请使用布尔值。')\r\n").encode()
after=before.replace(anchor,anchor+guard)
p.write_bytes(after)
assert after.replace(b'\r\n',b'').count(b'\n')==0
test=OUT/'test_susuro_condition_text_input.py'
shutil.copyfile(test,draft/'tests'/test.name)
unchanged=[]
for rel,info in freeze['files'].items():
    if rel=='rouge/operator_engine.py':continue
    assert hashlib.sha256((draft/rel).read_bytes()).hexdigest()==info['sha256']
    unchanged.append(rel)
receipt={'passed':True,'baseline_commit':freeze['baseline_commit'],'baseline_file_count':len(freeze['files']),
         'unchanged_old_files':len(unchanged),'changed_old_file':'rouge/operator_engine.py',
         'engine_before_sha256':hashlib.sha256(before).hexdigest(),'engine_after_sha256':hashlib.sha256(after).hexdigest(),
         'added_test':'tests/'+test.name,'test_sha256':hashlib.sha256(test.read_bytes()).hexdigest(),
         'guard':guard.decode(),'engine_crlf_preserved':True,'tracked_edits':False,
         'gui_executed':False,'wine_executed':False,'calculate_calls':0}
(OUT/'draft-freeze82.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(receipt,ensure_ascii=False))
