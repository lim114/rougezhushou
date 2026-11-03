import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

BASE = Path('/workspace/.continuation')
ROOT = Path('/workspace/rougezhushou')
COMPAT = Path('/workspace/.compat')
def ref(path):
    path = Path(path)
    assert path.is_file() and not path.is_symlink()
    data = path.read_bytes()
    return {'path': str(path), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}

raw = BASE / 'root-full095-wine_ui-cache-retry-v1.exit-code'
receipt = COMPAT / 'wine-ui-095-cache-retry-v1.json'
assert not raw.exists() and not receipt.exists()
guard_path = BASE / 'root-source-095-v2.json'
guard = json.loads(guard_path.read_bytes())['source_sha256_after']
current = {p.relative_to(ROOT).as_posix(): ref(p)['sha256']
           for folder in ('rouge', 'tests', 'scripts') for p in (ROOT / folder).rglob('*')
           if p.is_file() and p.suffix in ('.py', '.json')}
assert len(current) == 735 and current == guard
index_path = COMPAT / 'full095-ui-native-cache-retry-v1/wine-ui-full-native-index-095.json'
snapshot = BASE / 'root-full095-ui-cache-session-lost-v1-native-index.json'
with snapshot.open('xb') as handle:
    handle.write(index_path.read_bytes())
index = json.loads(snapshot.read_bytes())
assert index['outcome'] == 'pending'
native_refs = []
for row in index['chunks']:
    full = ref(COMPAT / row['file'])
    assert full['bytes'] == row['bytes'] and full['sha256'] == row['sha256']
    native_refs.append(full)
processes = {}
for pid in (50454, 50457, 50470, 50474):
    directory = Path('/proc') / str(pid)
    processes[str(pid)] = {'exists': directory.exists()}
    if directory.exists():
        processes[str(pid)].update(status=(directory/'status').read_text(), stat=(directory/'stat').read_text())
        assert '\nState:\tZ ' in processes[str(pid)]['status']
observations = {name: ref(BASE / ('root-full095-' + name + '-observation.json'))
                for name in ('linux_full', 'wine_full', 'linux_selected', 'wine_selected', 'linux_pip', 'wine_pip')}
for full in observations.values():
    d = json.loads(Path(full['path']).read_bytes())
    assert d['primary_exit_code'] == 0 and d['primary_exit_code_captured'] is True
record = {'section': 95, 'status': 'INCOMPLETE_UI_EXECUTION_SESSION_LOST_PRIMARY_UNAVAILABLE',
          'observed_at': datetime.now(timezone.utc).isoformat(),
          'actual_original_UI_session_id': 53266,
          'actual_original_UI_start_from_prior_trusted_observation': '2026-10-09T01:00:23.000Z',
          'lost_session_observation': 'Root write_stdin(session_id=53266) returned Unknown process id 53266 at the actual UTC clock observation 2026-10-09T04:28:14Z.',
          'primary_exit_code': None, 'primary_exit_code_captured': False,
          'raw_primary_status_absent': True, 'final_UI_receipt_absent': True,
          'actual_root_requested_process_termination': False,
          'cause_of_external_session_loss': 'UNKNOWN', 'physical_process_observation': processes,
          'actual_launch': ref(BASE / 'root-full095-wine_ui-cache-retry-v1-actual-launch.json'),
          'console': ref(BASE / 'root-full095-ui-cache-retry-v1-console.log'),
          'native_index': ref(index_path), 'preserved_native_index_snapshot': ref(snapshot),
          'closed_native_chunks': len(index['chunks']), 'closed_targeted_records': index['records_completed'],
          'states_committed': index['states_committed'], 'native_outcome': index['outcome'],
          'all_closed_compressed_chunk_refs_verified': native_refs,
          'source_guard': ref(guard_path), 'source_files_unchanged': 735, 'source_drift': [],
          'six_completed_primary_observations_preserved': observations,
          'previous_incomplete_UI': ref(BASE / 'ROOT_CURRENT_WORK_095_UI_SESSION_LOST_PRIMARY_UNAVAILABLE.json'),
          'same_UI_execution_problem_incomplete_attempt_count': 2,
          'third_attempt_may_use_reviewed_profile_identity_cache': True,
          'third_attempt_failure_requires_deferral': True,
          'saved_review_executed': False, 'full_validation_passed': False,
          'commit_performed': False, 'push_performed': False,
          'native_Windows_game_chat_verified': False}
out = BASE / 'ROOT_CURRENT_WORK_095_UI_CACHE_SESSION_LOST_PRIMARY_UNAVAILABLE.json'
with out.open('x', encoding='utf-8') as handle:
    json.dump(record, handle, ensure_ascii=False, indent=2)
    handle.write('\n')
wip = ROOT / 'WORK_IN_PROGRESS.md'
before = wip.read_bytes()
backup = BASE / 'root-WORK_IN_PROGRESS-before095-ui-cache-session-lost-v1.bin'
with backup.open('xb') as handle:
    handle.write(before)
prefix = '# 第95节恢复断点 · 第二次窗口会话失效，结束码未知\n\n截至' + record['observed_at'] + '，Root实际恢复检查确认session53266失效，进程缺失或zombie；留下136836条闭合记录、2310个native块，但无原始结束码与最终收据，未完成。Root没有请求终止，外部会话失效原因UNKNOWN。六项真实已通过步骤和735源码原字节保留。第三次采用已独立审阅的profile identity缓存候选，保持全部断言和完整测试；若同一问题第三次仍无法完成则搁置并保留恢复条件。新的Source模板/候选不计完成；95批次未commit/push。完整断点为.continuation/ROOT_CURRENT_WORK_095_UI_CACHE_SESSION_LOST_PRIMARY_UNAVAILABLE.json。\n\n---\n\n'
if b'\r\n' in before:
    prefix = prefix.replace('\n', '\r\n')
wip.write_bytes(prefix.encode('utf-8') + before)
assert wip.read_bytes().endswith(before)
print(json.dumps({'checkpoint': ref(out), 'native_snapshot': ref(snapshot), 'wip': ref(wip),
                  'original_wip_preserved': ref(backup), 'primary_exit_code': None,
                  'closed_chunk_refs_verified': len(native_refs), 'six_primary0_preserved': 6,
                  'fullPASS_or_commit_or_push': False}))
