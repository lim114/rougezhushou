"""Prepare the four section300 publication producers. Does not execute them."""
import ast
from hashlib import sha256
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
prior=ROOT/'.cache/p3-299-publication-prep'
parent='796c5d406a8d4ac36d924ce6d70db9081267ef68'
old_parent='b56cbf352cf5d171f52ba05839312950df462e8c'
for name in ('stage_section_300.py','verify_publication_300.py'):
 text=(HERE/(name+'.txt')).read_text(encoding='utf8');ast.parse(text)
 (HERE/name).write_bytes(text.encode('utf8'))
push=(prior/'push_section_299.py').read_text(encoding='utf8').replace('299','300').replace(old_parent,parent)
finish=(prior/'finish_publication_299.py').read_text(encoding='utf8').replace('299','300').replace(old_parent,parent)
finish=finish.replace("==300 and 'active_section'", "==301 and 'active_section'")
finish=finish.replace("'next_section':300", "'next_section':301")
finish=finish.replace("'prepare_tools_300.py','prepare_ready_300.py','READY.json','RUN_PLAN.md','BASELINE.json'", "'prepare_publication.py','stage_section_300.py.txt','verify_publication_300.py.txt','READY.json','RUN_PLAN.md','BASELINE.json'")
finish=finish.replace('next300 only after','next301 only after')
for name,text in (('push_section_300.py',push),('finish_publication_300.py',finish)):
 ast.parse(text);(HERE/name).write_bytes(text.encode('utf8'))
print({p.name:sha256(p.read_bytes()).hexdigest()for p in HERE.glob('*.py')})
