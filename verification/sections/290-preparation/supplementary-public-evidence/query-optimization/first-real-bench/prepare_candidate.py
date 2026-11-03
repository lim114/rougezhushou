"""Prepare one function-only candidate without touching the live source."""
import ast
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
path=ROOT/'rouge/event_planning.py'
raw=path.read_bytes()
text=raw.decode('utf-8')
tree=ast.parse(text)
node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='choice_resources')
lines=text.splitlines(keepends=True)
function=''.join(lines[node.lineno-1:node.end_lineno])
newline='\r\n' if '\r\n' in function else '\n'
old="        eligibility=next(r for r in choice_eligibility(event_id,scene_key,context)['rows'] if r['choice_key']==choice['key'])"
anchor="    context=_context(context);event=catalog._event(event_id);scene=catalog._scene(event_id,scene_key);rows=[]"
if function.count(old)!=1 or function.count(anchor)!=1:raise ValueError('Original function no longer matches the reviewed seam.')
changed=function.replace(anchor,anchor+newline+'    eligibility_by_key=None')
replacement=newline.join([
    '        if eligibility_by_key is None:',
    '            # One scene result per external query; defer until first needed.',
    '            eligibility_by_key={}',
    "            for reference in choice_eligibility(event_id,scene_key,context)['rows']:",
    "                eligibility_by_key.setdefault(reference['choice_key'],reference)",
    "        if choice['key'] not in eligibility_by_key:raise StopIteration",
    "        eligibility=eligibility_by_key[choice['key']]"])
changed=changed.replace(old,replacement)
candidate=''.join(lines[:node.lineno-1])+changed+''.join(lines[node.end_lineno:])
before_tree=ast.parse(text)
after_tree=ast.parse(candidate)
before_rest=[ast.dump(n) for n in before_tree.body if not isinstance(n,ast.FunctionDef) or n.name!='choice_resources']
after_rest=[ast.dump(n) for n in after_tree.body if not isinstance(n,ast.FunctionDef) or n.name!='choice_resources']
if before_rest!=after_rest:raise ValueError('Candidate changed code outside choice_resources.')
for filename,data in [('before-event-planning.py',raw),('candidate-event-planning.py',candidate.encode('utf-8'))]:
    with (HERE/filename).open('xb') as stream:stream.write(data)
receipt={'scope':'Preparation only; live file unchanged.','before_sha256':hashlib.sha256(raw).hexdigest(),
    'candidate_sha256':hashlib.sha256(candidate.encode('utf-8')).hexdigest(),
    'only_function_changed':'choice_resources','other_module_ast_unchanged':True,
    'qualification_point':'Lazy at original first-use location, preserving empty scenes and earlier resource-parse errors.',
    'first_matching_row_preserved':'setdefault; missing rows keep StopIteration instead of KeyError.',
    'cross_query_cache_added':False}
with (HERE/'candidate-preparation.json').open('x',encoding='utf-8') as stream:json.dump(receipt,stream,ensure_ascii=False,indent=2)
print(json.dumps(receipt,ensure_ascii=False))
