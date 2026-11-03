"""One qualified Four-Sui text gate; preserve other option contracts and CRLF."""
from pathlib import Path
import hashlib
import json

ROOT=Path(__file__).resolve().parent
BASE=ROOT/'baseline060'
DRAFT=ROOT/'draft062'
path=BASE/'rouge/operator_engine.py'
before=path.read_bytes()
old=b"            if self.s.get('four_sui'):\r\n"
assert before.count(old)==1
new=("            if '天有四时' in self.tv and isinstance(self.s.get('four_sui'),str):\r\n"
     "                raise ValueError('four_sui 不接受文本条件；请使用布尔值。')\r\n").encode()+old
out=before.replace(old,new)
(DRAFT/'rouge/operator_engine.py').write_bytes(out)
(ROOT/'operator_engine.baseline060.py').write_bytes(before)
(ROOT/'operator_engine.draft062.py').write_bytes(out)
files={str(p.relative_to(BASE)):hashlib.sha256(p.read_bytes()).hexdigest()
       for p in BASE.rglob('*') if p.is_file() and p.suffix in ('.py','.json')}
(ROOT/'freeze-receipt060.json').write_text(json.dumps({'baseline_head':'c3ccf25d59144227dd0f8f5ca9ef6c8bf81ad8cf',
    'creation':'git archive exact committed public rouge/tests/scripts, no worktree overlay',
    'files':files,'draft_only_source_change':'rouge/operator_engine.py',
    'declared_error_literal':'four_sui 不接受文本条件；请使用布尔值。',
    'prior_readonly_audit_preserved':'/workspace/.continuation/p2-boolean-option-audit-062'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'baseline_files':len(files),'source_changed_lines':2,
                  'before_sha256':hashlib.sha256(before).hexdigest(),
                  'after_sha256':hashlib.sha256(out).hexdigest()},ensure_ascii=False))
