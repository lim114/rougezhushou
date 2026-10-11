"""Refresh public continuation pointers; never read private runtime state."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
START = '<!-- live-cloud-index:start -->'
END = '<!-- live-cloud-index:end -->'


def update(root=ROOT):
    root = Path(root)
    checkpoint = json.loads((root / 'DEVELOPMENT_CHECKPOINT.json').read_text(encoding='utf-8'))
    completed = checkpoint['completed_sections']
    fulls = sorted((root / 'verification').glob('full-*/native.json'),
                   key=lambda p: int(p.parent.name.split('-')[1]))
    fulls = [p for p in fulls if int(p.parent.name.split('-')[1]) <= completed]
    latest = fulls[-1] if fulls else None
    files = ['DEVELOPMENT_CHECKPOINT.json', 'PROJECT_PROGRESS.md', 'WORK_IN_PROGRESS.md',
             'PROJECT_COMPLETED.md', 'AGENTS.md', f'verification/sections/{completed:03}.json']
    index = {
        'project': 'rougezhushou', 'branch': 'codex/p2-development',
        'completed_sections': completed, 'next_section': checkpoint['next_section'],
        'batch_status': checkpoint.get('batch_status'),
        'next_full_validation_after': checkpoint['next_full_validation_after'],
        'commit_reference': 'the commit containing this index; verify Git branch and remote before resuming',
        'latest_full_receipt': latest.relative_to(root).as_posix() if latest else None,
        'latest_full_available_checks_passed': json.loads(latest.read_text(encoding='utf-8'))['available_checks_passed'] if latest else None,
        'priority_order': 'P2 first; independently evidenced P3 may advance; preserve P1; recognition last',
        'node_scope': 'list all source-covered possible events and conditions; no generation probabilities',
        'project_complete': False,
        'sections': checkpoint['sections'],
        'public_pointers': {f: hashlib.sha256((root / f).read_bytes()).hexdigest()
                            for f in files if (root / f).is_file()},
        'private_state_included': False,
    }
    (root / 'CLOUD_INDEX.json').write_text(json.dumps(index, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')
    path = root / 'CLOUD_HANDOFF.md'
    old = path.read_text(encoding='utf-8')
    if START in old:
        before, rest = old.split(START, 1)
        _, after = rest.split(END, 1)
        old = before + after.lstrip('\n')
    block = (f'{START}\n# 当前云端续接索引 · 第{completed}节\n\n'
             f'已完成至{completed}，后续{checkpoint["next_section"]}；本批状态 `{checkpoint.get("batch_status")}`。'
             f'下次定期全量{checkpoint["next_full_validation_after"]}。每节更新本入口和 CLOUD_INDEX.json 并随功能提交普通推送。\n\n'
             '恢复时先核对远端 `codex/p2-development`、真实源码和 DEVELOPMENT_CHECKPOINT.json。'
             '当前待办仅在 PROJECT_PROGRESS.md；完成范围在 PROJECT_COMPLETED.md，逐节回执在 verification/sections/。'
             'P2尚未全部完成；原生动作/结束时钟和当前游戏面板不能用公式参考代替验收。节点只列来源覆盖的候选与条件，不要求生成概率。\n\n'
             f'最新本机全量：`{index["latest_full_receipt"]}`，可用范围全通过：`{index["latest_full_available_checks_passed"]}`。'
             'Windows后台采样和聊天不等于云端验证；本批不操作游戏、不发送聊天。私人配置与本局记忆只保留本机。'
             f'下面是历史交接，不代表当前节数。\n{END}\n\n')
    path.write_text(block+old, encoding='utf-8', newline='\n')


if __name__ == '__main__':
    update()
