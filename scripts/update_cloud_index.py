"""Refresh public continuation pointers; never read private runtime state."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
START = '<!-- live-cloud-index:start -->'
END = '<!-- live-cloud-index:end -->'


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _public_json(root, relative):
    _require(isinstance(relative, str), 'Public receipt path must be a string.')
    path = (root / relative).resolve()
    _require(path.is_relative_to((root / 'verification').resolve()),
             'Publication/section receipts must stay in public verification.')
    _require(path.is_file(), 'Missing public receipt: ' + relative)
    return json.loads(path.read_text(encoding='utf-8'))


def validate_delivery(root, checkpoint):
    """Reject stale active fields; previous verified publication may be one behind.

    current_section_save describes this enclosing commit and therefore does not
    embed its own not-yet-created hash. last_verified_cloud_save describes an
    already existing, independently verified remote commit with a hash-bound public proof. During a new feature
    section that record may be the previous section; during260 maintenance the
    already pushed functional260 is admissible without creating section261.
    A numbered repair explicitly requested by the user has its own receipt
    kind and authorization; it is never classified as a functional section.
    """
    root = Path(root).resolve()
    section = checkpoint.get('completed_sections')
    _require(type(section) is int and section > 0,
             'completed_sections must be a positive integer.')
    _require(checkpoint.get('next_section') == section + 1,
             'next_section must be completed_sections + 1.')
    _require(checkpoint.get('branch') == 'codex/p2-development',
             'Checkpoint branch must be codex/p2-development.')
    expected_receipt = f'verification/sections/{section:03}.json'
    rows = checkpoint.get('sections')
    _require(isinstance(rows, list) and rows,
             'Current completed section must have a recorded section row.')
    _require(rows[-1].get('number') == section
             and rows[-1].get('verification') == expected_receipt,
             'Last section row differs from completed_sections/current receipt.')
    section_receipt = _public_json(root, expected_receipt)
    _require(section_receipt.get('section') == section,
             'Current section receipt differs from completed_sections.')

    current_repair = section_receipt.get('kind') == 'user_requested_repair_section'
    if current_repair:
        authorized = checkpoint.get('policy', {}).get('current_user_requested_repair_section')
        _require(type(authorized) is int and authorized == section
                 and section_receipt.get('user_requested') is True,
                 'Requested repair needs its exact current user authorization and receipt.')
    current_scope = ('current_requested_repair_section' if current_repair
                     else 'current_functional_section')

    current = checkpoint.get('current_section_save') or {}
    _require(current.get('section') == section,
             'current_section_save is stale; it must name completed_sections.')
    _require(current.get('verification') == expected_receipt,
             'current_section_save must name the current public section receipt.')
    _require(current.get('scope') == current_scope,
             'Current save scope must match its functional or explicitly requested repair receipt.')
    _require(current.get('binding') == 'enclosing_commit',
             'Current save binding must explicitly be enclosing_commit, not a self hash.')

    published = checkpoint.get('last_verified_cloud_save') or {}
    saved_section = published.get('section')
    _require(type(saved_section) is int and saved_section in (section - 1, section),
             'last_verified_cloud_save must be current or previous section; older records are historical.')
    saved_repair = current_repair if saved_section == section else False
    if saved_section != section:
        saved_reference = f'verification/sections/{saved_section:03}.json'
        # Historical functional fixtures may predate section receipts. A
        # repair publication always needs its explicit public authorization.
        if (root / saved_reference).is_file() or published.get('scope') == 'previous_requested_repair_section':
            saved_receipt = _public_json(root, saved_reference)
            _require(saved_receipt.get('section') == saved_section,
                     'Previous section receipt differs from verified publication.')
            saved_repair = saved_receipt.get('kind') == 'user_requested_repair_section'
            if saved_repair:
                _require(saved_receipt.get('user_requested') is True,
                         'Previous repair publication needs its recorded user authorization.')
    expected_scope = (('current_' if saved_section == section else 'previous_')
                      + ('requested_repair_section' if saved_repair else 'functional_section'))
    _require(published.get('scope') == expected_scope,
             'Verified publication scope must distinguish current from previous section.')
    _require(not checkpoint.get('policy', {}).get('new_functional_sections_paused')
             or saved_section == section or current_repair,
             'Paused functional development requires the current functional section publication.')
    _require(published.get('binding') == 'verified_remote_commit',
             'Verified publication binding must be explicit and distinct from enclosing_commit.')
    commit = published.get('commit')
    _require(isinstance(commit, str) and re.fullmatch(r'[0-9a-f]{40}', commit),
             'Verified remote commit needs the complete actual Git SHA.')
    proof_reference = published.get('proof')
    proof = _public_json(root, proof_reference)
    proof_sha = published.get('proof_sha256')
    _require(isinstance(proof_sha, str) and re.fullmatch(r'[0-9a-f]{64}', proof_sha)
             and hashlib.sha256((root / proof_reference).read_bytes()).hexdigest() == proof_sha,
             'Verified publication must bind the exact public proof bytes.')
    _require(proof.get('passed') is True
             and proof.get('section') == saved_section
             and proof.get('branch') == 'codex/p2-development'
             and proof.get('commit') == commit
             and proof.get('local_HEAD') == commit == proof.get('remote_HEAD')
             and proof.get('remote_branch') == 'origin/codex/p2-development'
             and type(proof.get('push_primary_exit')) is int
             and proof.get('push_primary_exit') == 0,
             'Public publication proof must bind the actual local/remote development SHA.')

    # Real Git-object/remote freshness is audited at publication, outside this
    # portable reader. Re-reading a hash-bound proof is not a new remote check.

    cadence = checkpoint.get('current_batch_commit_policy') or {}
    _require('next_full_validation_after' in checkpoint
             and 'next_full_validation_after' in cadence
             and 'next_full_validation_after' in checkpoint.get('policy', {}),
             'All three active cadence pointers must be present.')
    next_full = checkpoint.get('next_full_validation_after')
    _require(cadence.get('next_full_validation_after') == next_full
             == checkpoint.get('policy', {}).get('next_full_validation_after'),
             'Active batch cadence differs from the authoritative next full validation.')
    available = checkpoint.get('current_available_full_validation')
    if available is not None:
        last = checkpoint.get('last_full_validation') or {}
        _require(available.get('section') == last.get('after_section')
                 and available.get('receipt') == last.get('receipt'),
                 'Current full validation pointer differs from last_full_validation.')
    batch = checkpoint.get('current_batch')
    if batch is not None:
        _require(batch.get('start') == checkpoint.get('batch_start_section')
                 and batch.get('end') == checkpoint.get('batch_target_section')
                 and batch.get('status') == checkpoint.get('batch_status')
                 and batch.get('next_section') == section + 1
                 and batch.get('next_full_validation_after') == next_full,
                 'Current batch pointer differs from the authoritative active batch.')
    return {'current_section': section, 'current_binding': 'enclosing_commit',
            'current_scope': current_scope,
            'verified_remote_section': saved_section,
            'verified_remote_scope': expected_scope,
            'verified_remote_commit': commit}


def update(root=ROOT):
    root = Path(root)
    requirements = root / 'PROJECT_REQUIREMENTS.md'
    if not requirements.is_file():
        raise FileNotFoundError('Cloud index requires PROJECT_REQUIREMENTS.md; do not publish an incomplete requirements pointer.')
    checkpoint = json.loads((root / 'DEVELOPMENT_CHECKPOINT.json').read_text(encoding='utf-8'))
    completed = checkpoint['completed_sections']
    validate_delivery(root, checkpoint)
    fulls = sorted((root / 'verification').glob('full-*/native.json'),
                   key=lambda p: int(p.parent.name.split('-')[1]))
    fulls = [p for p in fulls if int(p.parent.name.split('-')[1]) <= completed]
    latest = fulls[-1] if fulls else None
    declared=checkpoint.get('last_full_validation') or {}
    if (type(declared.get('after_section')) is int and declared['after_section']<=completed
            and declared['after_section'] >= (int(latest.parent.name.split('-')[1]) if latest else 0)):
        reference=declared.get('receipt')
        match=re.fullmatch(r'verification/full-(\d+)/[^/]+\.json',reference or '')
        if not match or int(match[1])!=declared['after_section']:
            raise ValueError('Cloud full receipt must name its declared public verification section.')
        candidate=(root/reference).resolve()
        if not candidate.is_relative_to((root/'verification').resolve()):
            raise ValueError('Cloud full receipt must remain inside public verification.')
        if not candidate.is_file():raise FileNotFoundError('Declared latest full receipt is missing: '+reference)
        latest=candidate
    files = ['DEVELOPMENT_CHECKPOINT.json', 'PROJECT_PROGRESS.md', 'WORK_IN_PROGRESS.md',
             'PROJECT_COMPLETED.md', 'AGENTS.md', 'PROJECT_REQUIREMENTS.md',
             f'verification/sections/{completed:03}.json']
    index = {
        'project': 'rougezhushou', 'branch': 'codex/p2-development',
        'completed_sections': completed, 'next_section': checkpoint['next_section'],
        'batch_status': checkpoint.get('batch_status'),
        'next_full_validation_after': checkpoint['next_full_validation_after'],
        'commit_reference': 'the commit containing this index; verify Git branch and remote before resuming',
        'latest_full_receipt': latest.relative_to(root).as_posix() if latest else None,
        'latest_full_available_checks_passed': json.loads(latest.read_text(encoding='utf-8'))['available_checks_passed'] if latest else None,
        'priority_order': ' → '.join(checkpoint.get('policy', {}).get(
            'priority_order', ['P2', 'P3', 'P1'])) + '；识别优化最后；未完成事项保留',
        'node_scope': 'list all source-covered possible events and conditions; no generation probabilities',
        'project_complete': False,
        'current_batch_target_section': checkpoint['policy'].get('current_user_batch_target_section'),
        'requirements': {'path': 'PROJECT_REQUIREMENTS.md',
                         'sha256': hashlib.sha256(requirements.read_bytes()).hexdigest(),
                         'scope': 'current product requirements and delivery rules; historical handoffs do not override it'},
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
             f'推进终点：{index["current_batch_target_section"] if index["current_batch_target_section"] is not None else "未指定数字终点"}。'
             f'下次定期全量{checkpoint["next_full_validation_after"]}。每节更新本入口和 CLOUD_INDEX.json 并随功能提交普通推送。\n\n'
             '恢复时先核对远端 `codex/p2-development`、真实源码和 DEVELOPMENT_CHECKPOINT.json。'
             '当前待办仅在 PROJECT_PROGRESS.md；完成范围在 PROJECT_COMPLETED.md，逐节回执在 verification/sections/。'
             '当前产品要求与交付边界见 PROJECT_REQUIREMENTS.md，并随每节索引核对摘要、提交到同一分支。'
             f'当前工作顺序：{index["priority_order"]}。'
             'P2尚未全部完成；原生动作/结束时钟和当前游戏面板不能用公式参考代替验收。节点只列来源覆盖的候选与条件，不要求生成概率。\n\n'
             f'最新记录全量：`{index["latest_full_receipt"]}`，可用范围全通过：`{index["latest_full_available_checks_passed"]}`。'
             'Windows后台采样和聊天不等于云端验证；本批不操作游戏、不发送聊天。私人配置与本局记忆只保留本机。'
             f'下面是历史交接，不代表当前节数。\n{END}\n\n')
    path.write_text(block+old, encoding='utf-8', newline='\n')


if __name__ == '__main__':
    update()
