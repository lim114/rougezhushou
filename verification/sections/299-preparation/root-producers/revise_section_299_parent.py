from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'.cache/p3-299-root-integration/candidate/rouge/battle_view.py';raw=source.read_bytes()
assert sha256(raw).hexdigest()=='970a331b6ba7ee4ef99f51add48683d78339b6dc4eb1c603e056cf1eccdd43b9'
nl='\r\n'if b'\r\n'in raw else'\n'
old="        resolved=spawn_candidates.resolve_reference(token)\n        reference=resolved['member'].get('spawn_reference') if resolved else None"
new="""        relation,member=panel._selected()
        if not relation or not member or not panel.open_spawn_button.isEnabled() or member.get('token')!=token:
            return False
        resolved=spawn_candidates.resolve_reference(token)
        if not resolved:
            self._refresh_spawn_candidates()
            return False
        reference=resolved['member'].get('spawn_reference')"""
a=old.replace('\n',nl).encode();b=new.replace('\n',nl).encode();assert raw.count(a)==1;raw=raw.replace(a,b)
raw=raw.replace('只查看固定主出怪计划；条件分支不借用同名候选组。'.encode(),
 '这里查看常规出怪资料；特殊出怪请使用上方的条件与位置入口。'.encode())
raw=raw.replace("preview.setWindowTitle('出怪候选资料 · '+panel.packet['stage_name']+' · '+resolved['member']['display_name'])".encode(),
 "preview.setWindowTitle('候选条目的独立战斗预览')".encode())
target=ROOT/'.cache/p3-299-root-integration/revision2/rouge/battle_view.py';target.parent.mkdir(parents=True,exist_ok=True)
assert not target.exists();target.write_bytes(raw)
note={'section':299,'kind':'root_parent_candidate_revision_before_product_promotion',
 'before_sha256':sha256(source.read_bytes()).hexdigest(),'after_sha256':sha256(raw).hexdigest(),
 'changes':['Parent additionally requires the exact currently selected manual relation/member token and an enabled manual button; old same-source token cannot reopen a preview after selection cleared or source recovery.',
 'Failed fresh resolver refreshes new references, clearing source-invalid targets without changing parent filters.',
 'Tooltip uses ordinary Chinese. Separate preview has a generic title because its own public stage controls remain interactive.'],
 'actual_tests_run':0,'production_modified':False}
p=target.parents[1]/'REVISION.json';p.write_bytes((json.dumps(note,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps(note,ensure_ascii=False))
