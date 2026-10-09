"""Archive a verified section; only the fifth-section full PASS permits commit/push."""
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

spec = json.loads(Path(sys.argv[1]).read_bytes())
n = spec['number']
ref = f'working-tree-section-{n:03d}'
receipt = f'verification/sections/{n:03d}.json'
assert subprocess.check_output(['git', 'branch', '--show-current'], text=True).strip() == 'codex/p2-development'
cp_path = Path('DEVELOPMENT_CHECKPOINT.json')
cp = json.loads(cp_path.read_bytes())
assert cp['completed_sections'] == n - 1
assert cp['policy']['commit_after_each_section'] is False
assert cp['policy']['commit_interval'] == 5
assert spec['verification']['actual_window_verified_by_root'] is True
Path(receipt).write_text(json.dumps({'section': n, 'completion_ref': ref, 'branch': 'codex/p2-development',
    'validated_at': datetime.now(timezone.utc).isoformat(), 'commit_status': 'pending_next_fifth_section_full_PASS',
    'completion_ref_is_Git_tag': False, **spec['verification']}, ensure_ascii=False, indent=2) + '\n')
cp['sections'].append({'number': n, 'completion_ref': ref, 'topic': spec['topic'], 'verification': receipt,
    'commit_status': 'pending_batch_full_PASS', 'completion_ref_is_Git_tag': False})
cp.update(completed_sections=n, next_section=n+1, next_action=spec['next_action'], full_validation_due=n%5 == 0)
cp.setdefault('pending_batch_sections', []).append(n)
cp['pending_batch_save'] = {'next_full_validation_after': ((n+4)//5)*5,
    'commit_and_push_after_full_PASS': True, 'destination': 'origin codex/p2-development',
    'last_committed_section': cp.get('last_saved_batch', {}).get('after_section', 92), 'section_source_snapshots_are_archived': True}
cp_path.write_text(json.dumps(cp, ensure_ascii=False, indent=2) + '\n')
def edit(name, fn):
    path = Path(name)
    data = path.read_bytes()
    old = data.decode().replace('\r\n', '\n')
    new = fn(old)
    path.write_bytes(new.replace('\n', '\r\n').encode() if b'\r\n' in data else new.encode())
edit('WORK_IN_PROGRESS.md', lambda old: f'# 连续开发断点 · 第 {n} 节验收并存档\n\n'
    f'`codex/p2-development`，实际源码快照 `{ref}`（不是Git标签）；本节尚未单独提交。'
    + spec['summary'] + f'\n\n下一步：{spec["next_action"]}。'
    + '按最新用户规则：每节保存源码、检验与断点，每五节全量通过后统一commit并推送GitHub当前开发分支，再自动继续。'
    + 'P2完成后转P3；同问题三次未解决则搁置；低于15%额度完成当前必要检验后收尾，目前无额度API。'
    + f'见 `{receipt}` 与 `DEVELOPMENT_CHECKPOINT.json`。\n\n---\n\n' + old)
edit('PROJECT_COMPLETED.md', lambda old: f'# 连续开发 {n:03d} · {spec["topic"]}\n\n'
    + spec['summary'] + f' 见 `{receipt}`。按五节提交规则已验收存档，等待本组全量通过后统一commit/push。\n\n---\n\n' + old)
edit('BATCH_CONTINUOUS_P2.md', lambda old: old + f'\n## {n:03d} · {spec["topic"]}\n\n'
    + spec['summary'] + f'\n\n验证 `{receipt}`。本节源码快照已冻结，尚无单独Git提交或标签；本组第五节全量通过后统一提交并推送。'
    + spec.get('limitations', '') + '\n')
