import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path('/workspace/rougezhushou')
BASE = Path('/workspace/.continuation')
def ref(path):
    path = Path(path)
    assert path.is_file() and not path.is_symlink()
    raw = path.read_bytes()
    return {'path': str(path), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}

assert subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT).decode().strip() == 'codex/p2-development'
guard = json.loads((BASE / 'root-source-095-v2.json').read_bytes())['source_sha256_after']
actual = {p.relative_to(ROOT).as_posix(): ref(p)['sha256'] for folder in ('rouge', 'tests', 'scripts')
          for p in (ROOT / folder).rglob('*') if p.is_file() and p.suffix in ('.py', '.json')}
assert len(actual) == 735 and actual == guard
launch = BASE / 'root-full095-wine_ui-cache-retry-v1-actual-launch.json'
assert json.loads(launch.read_bytes())['launch_result']['session_id'] == 53266
assert not (BASE / 'root-full095-wine_ui-cache-retry-v1.exit-code').exists()
assert not Path('/workspace/.compat/wine-ui-095-cache-retry-v1.json').exists()
index = Path('/workspace/.compat/full095-ui-native-cache-retry-v1/wine-ui-full-native-index-095.json')
snapshot = BASE / 'root-full095-ui-cache-progress-03-native-index.json'
with snapshot.open('xb') as handle:
    handle.write(index.read_bytes())
progress = json.loads(snapshot.read_bytes())
assert progress['outcome'] == 'pending'
recorded = datetime.now(timezone.utc).isoformat()
record = {'status': 'ACTUAL_UI_RUNNING_NOT_FULLPASS_NOT_COMMITTED_OR_PUSHED',
          'recorded_at': recorded, 'section': 95, 'next_section_after_batch_save': 96,
          'branch': 'codex/p2-development', 'actual_launch': ref(launch),
          'actual_progress_snapshot': ref(snapshot),
          'actual_records_completed_at_snapshot': progress['records_completed'],
          'actual_closed_chunks_at_snapshot': len(progress['chunks']),
          'actual_states_committed_at_snapshot': progress['states_committed'],
          'primary_exit_code': None, 'primary_exit_code_captured': False,
          'six_completed_zero_checkpoint': ref(BASE / 'ROOT_CURRENT_WORK_095_SIX_ZERO_UI_CACHE_READY.json'),
          'original_UI_unknown_exit_checkpoint': ref(BASE / 'ROOT_CURRENT_WORK_095_UI_SESSION_LOST_PRIMARY_UNAVAILABLE.json'),
          'new_UI_source_binding': ref(BASE / 'full095-regression-ui-cache-resume-final-v1/actual-full095-source-binding.json'),
          'saved_review_executed': False, 'final_full_context_passed': False,
          'commit_performed': False, 'push_performed': False,
          'source_count': len(actual), 'source_drift': [],
          'future096_097_Source_preparation_is_not_completed_work': True,
          'native_Windows_game_chat_verified': False}
out = BASE / 'ROOT_CURRENT_WORK_095_UI_CACHE_RETRY_PROGRESS_V3.json'
with out.open('x', encoding='utf-8') as handle:
    json.dump(record, handle, ensure_ascii=False, indent=2)
    handle.write('\n')
wip = ROOT / 'WORK_IN_PROGRESS.md'
previous = wip.read_bytes()
backup = BASE / 'root-WORK_IN_PROGRESS-before095-ui-live-v3.bin'
with backup.open('xb') as handle:
    handle.write(previous)
prefix = f'''# 第95节全量检验实际断点 · 六项通过，窗口重试运行中

截至{recorded}，第93—95节功能及各节专项检验已存档；六项全量步骤真实primary0已保留。新窗口重试session53266已实际启动，当前闭合记录{progress['records_completed']}条、native块{len(progress['chunks'])}个；这是进行中的快照，尚无窗口收据或退出码，不能计为全量通过。735维护源码与已验收95快照完全一致。原窗口连接丢失后的退出码继续保持NULL，原Wine全量链接夹具失败及精选子进程超时记录保留；相应已通过重试不重复执行。Wine兼容验证不代表原生Windows/game/chat验证。

断点：云环境.continuation/ROOT_CURRENT_WORK_095_UI_CACHE_RETRY_PROGRESS_V3.json、实际启动记录及独立保存的native进度快照。下一步：继续等待实际窗口完成；primary0后实际查看四张PNG、执行保存证据检验和严格全量finish，再归档、统一一次commit并正常push至GitHub当前codex/p2-development分支；自动继续96—100。96培养条件说明及97保存异常处理目前仅源码方案和审查准备，不计完成；不改冻结的DEVELOPMENT_CHECKPOINT.json以免改变当前全量绑定。

---

'''
if b'\r\n' in previous:
    prefix = prefix.replace('\n', '\r\n')
wip.write_bytes(prefix.encode('utf-8') + previous)
assert wip.read_bytes().endswith(previous)
print(json.dumps({'checkpoint': ref(out), 'wip': ref(wip), 'prior_wip_preserved': ref(backup),
                  'actual_progress': [progress['records_completed'], len(progress['chunks'])],
                  'maintained_source_drift': [], 'commit_or_push': False}))
