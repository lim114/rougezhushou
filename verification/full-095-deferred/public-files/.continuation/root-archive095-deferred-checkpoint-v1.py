"""Preserve explicit public evidence; no project, codec, test or Wine execution."""
import hashlib
import json
import shutil
import stat
from datetime import datetime, timezone
from pathlib import Path

BASE = Path('/workspace/.continuation')
COMPAT = Path('/workspace/.compat')
ROOT = Path('/workspace/rougezhushou')
OUTPUT = ROOT / 'verification/full-095-deferred'
PLAN = BASE / 'full095-deferred-manual-selection-source-v1/selection-plan095.json'
FILES = {}

def sha_file(path):
    h = hashlib.sha256()
    size = 0
    with path.open('rb') as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b''):
            size += len(part)
            h.update(part)
    return {'path': str(path), 'bytes': size, 'sha256': h.hexdigest()}

def add(path, expected=None, category='explicit_public_source'):
    path = Path(path)
    assert path.is_absolute() and '..' not in path.parts
    assert path.is_relative_to(Path('/workspace')) and str(path.resolve(strict=True)) == str(path)
    assert not any(p.is_symlink() for p in (path, *path.parents))
    assert stat.S_ISREG(path.lstat().st_mode)
    assert path.suffix.lower() not in ('.dll', '.exe', '.so', '.pyd', '.pem', '.key')
    full = sha_file(path)
    assert full['bytes'] < 100 * 1024 * 1024
    if expected is not None:
        assert all(full[k] == expected[k] for k in ('path', 'bytes', 'sha256')), (full, expected)
    name = str(path)
    if name in FILES:
        assert FILES[name]['source'] == full
        if category not in FILES[name]['categories']:
            FILES[name]['categories'].append(category)
    else:
        FILES[name] = {'source': full, 'categories': [category],
                       'archive_path': 'public-files/' + path.relative_to(Path('/workspace')).as_posix()}
    return full

def document(ref, category):
    add(ref['path'], ref, category)
    return json.loads(Path(ref['path']).read_bytes())

def main():
    assert not OUTPUT.exists()
    assert not Path('/proc/67613').exists() or 'State:\tZ' in Path('/proc/67613/status').read_text()
    plan_ref = add(PLAN, category='manual_Source_plan_not_runtime')
    assert plan_ref['sha256'] == 'fb39c50dbe6a3de7eac851538c0ceacc9eeab2ad0f19794ea7d37aed51a5e140'
    plan = json.loads(PLAN.read_bytes())
    selectors = plan['source_selector_inputs']
    config = document(selectors['actual_FINAL_evidence_source_config'], 'explicit_frozen_Source_selector')
    selection = document(selectors['Root_public_selection_v4'], 'explicit_frozen_Source_selector')
    binding = document(selectors['actual_FINAL_identity_binding'], 'actual_Source_binding_not_PASS')
    for ref in config['pinned_source_inputs'].values():
        add(ref['path'], ref)
    for packet in config['public_packets']:
        assert packet['public'] is True and packet['numbered_section_completed'] is False
        mf = add(packet['manifest_path'], category='frozen_public_Source_manifest')
        assert mf['sha256'] == packet['manifest_sha256']
        value = json.loads(Path(mf['path']).read_bytes())
        style = packet['style']
        if style == 'local_artifact_dict':
            rows = [{'path': str(Path(mf['path']).parent / name), **meta}
                    for name, meta in value['artifacts'].items()]
        elif style in ('payload_ref_rows', 'payload_file_rows'):
            rows = value['payload_files']
        elif style == 'source_archive_rows':
            rows = [{'path': r['source_path'], 'bytes': r['bytes'], 'sha256': r['sha256']} for r in value['files']]
        else:
            raise ValueError('Unreviewed manifest style: ' + style)
        assert len(rows) == packet['payload_count']
        for ref in rows:
            add(ref['path'], ref, 'frozen_public_Source_payload_not_section_completion')
    for ref in config['supplemental_public_inputs'].values():
        add(ref['path'], ref, 'explicit_historical_public_Source_or_incomplete_evidence')
    assert len(selection['rows']) == 447
    for row in selection['rows']:
        add(row['file']['path'], row['file'], 'public_Source_recovery_preparation_not_PASS')
    for job in plan['six_actual_passed_jobs']:
        observation = document(job['observation'], 'actual_completed_primary_zero_' + job['job'])
        assert type(observation['primary_exit_code']) is int and observation['primary_exit_code'] == 0
        for key in ('raw_primary', 'console', 'receipt_or_receipt_log', 'producer_source', 'runner_detail_log'):
            if job.get(key) is not None:
                ref = job[key]
                add(ref['path'], ref, 'actual_completed_primary_zero_' + job['job'])
        assert Path(job['raw_primary']['path']).read_bytes() in (b'0\n', b'0\r\n')
    for history in plan['lost_UI_history']:
        document(history['capsule'], 'UI_history_unknown_primary_not_PASS')
        index = document(history['native_index'], 'UI_history_pending_index_not_PASS')
        assert index['outcome'] == 'pending' and len(index['chunks']) == history['closed_chunks']
        for row in index['chunks']:
            p = COMPAT / row['file']
            add(p, {'path': str(p), 'bytes': row['bytes'], 'sha256': row['sha256']}, 'closed_incomplete_UI_history_chunk_not_PASS')
    assert not (BASE / 'root-full095-wine_ui-cache-retry-v1.exit-code').exists()
    completion_path = BASE / 'root-full095-wine_ui-identity-retry-v1-actual-completion.json'
    completion = json.loads(completion_path.read_bytes())
    assert completion['cancelled_by_root'] is True and completion['primary_exit_code'] == 143
    assert completion['last_tool_result']['exit_code'] == 143
    assert Path(completion['exit_code_path']).read_bytes() == b'143\n'
    assert not (COMPAT / 'wine-ui-095-identity-retry-v1.json').exists()
    native = COMPAT / 'full095-ui-native-identity-retry-v1'
    index = json.loads((native / 'wine-ui-full-native-index-095.json').read_bytes())
    assert index['outcome'] == 'pending'
    for row in index['chunks']:
        p = COMPAT / row['file']
        assert p.parent == native
        add(p, {'path': str(p), 'bytes': row['bytes'], 'sha256': row['sha256']}, 'third_cancelled_UI_closed_chunk_not_PASS')
    for path in sorted(native.rglob('*')):
        assert not path.is_symlink()
        assert stat.S_ISDIR(path.lstat().st_mode) or stat.S_ISREG(path.lstat().st_mode)
        if path.is_file():
            add(path, category='third_cancelled_UI_physical_namespace_not_PASS')
    for name in (
        'root-full095-wine_ui-identity-retry-v1-actual-completion.json',
        'root-full095-ui-identity-time-budget-decision-v1.json',
        'root-full095-ui-identity-time-budget-signal-v1.json',
        'root-full095-wine_ui-identity-retry-v1.exit-code',
        'root-full095-ui-identity-retry-v1-console.log',
        'root-stop095-ui-identity-time-budget-v1.log',
        'root-stop095-ui-identity-time-budget-v1.exit-code',
        'ROOT_CURRENT_WORK_095_UI_IDENTITY_RETRY_RUNNING_V1.json',
        'root-full095-ui-identity-progress-v1-native-index.json',
        'root-WORK_IN_PROGRESS-before095-ui-identity-running-v1.bin',
        'root-full095-public-continuation-supplements-v4.json',
        'root-prepare095-public-continuation-supplements-v4.py',
        'root-prepare095-public-continuation-supplements-v4.log',
        'root-prepare095-public-continuation-supplements-v4.exit-code',
        'root-preflight095-origin-development-connection-v1.stdout',
        'root-preflight095-origin-development-connection-v1.stderr',
        'root-preflight095-origin-development-connection-v1.exit-code',
        'root-user-query095-all-remote-heads-v1.stdout',
        'root-user-query095-all-remote-heads-v1.stderr',
        'root-user-query095-all-remote-heads-v1.exit-code',
    ):
        add(BASE / name, category='actual_Root_recovery_or_cancellation_or_remote_read')
    for folder in (
        'full095-deferred-manual-selection-source-v1',
        'full095-recovery-progress-report-independent-review-v1',
        'p2-account-persistence097-runtime-templates-source-pending-v1',
        'p2-runstate-reliability098-validation-source-pending-v1',
    ):
        for path in sorted((BASE / folder).rglob('*')):
            if path.is_file():
                add(path, category='explicit_partial_Source_or_review_not_applied_not_runtime')
    add(Path(__file__).resolve(), category='Root_metadata_archive_Source')
    context_path = binding['actual_inputs']['global_output_plan']['paths']['context_start']
    add(context_path, category='actual_started_context_not_finished')
    for row in FILES.values():
        assert sha_file(Path(row['source']['path'])) == row['source']
    OUTPUT.mkdir()
    for row in FILES.values():
        source = Path(row['source']['path'])
        target = OUTPUT / row['archive_path']
        target.parent.mkdir(parents=True, exist_ok=True)
        with source.open('rb') as src, target.open('xb') as dst:
            shutil.copyfileobj(src, dst, length=1024 * 1024)
        copied = sha_file(target)
        assert copied['bytes'] == row['source']['bytes'] and copied['sha256'] == row['source']['sha256']
        assert sha_file(source) == row['source']
    expected = {row['archive_path'] for row in FILES.values()}
    actual = {p.relative_to(OUTPUT).as_posix() for p in OUTPUT.rglob('*') if p.is_file()}
    assert expected == actual
    manifest = {'format_version': 1, 'status': 'FULL095_DEFERRED_PUBLIC_CHECKPOINT_NOT_FULLPASS',
                'created_at_UTC': datetime.now(timezone.utc).isoformat(),
                'available_full095_passed': False, 'complete_repository_validation': False,
                'complete_ui_validation': False, 'native_windows_verified': False,
                'prior_UI_unknown_primary_exits': [None, None], 'third_UI_primary_exit': 143,
                'third_UI_cancelled_by_Root_for_declared_runtime_budget': True,
                'third_UI_records_saved': index['records_completed'],
                'third_UI_closed_chunks': len(index['chunks']), 'no_fourth_UI_retry': True,
                'Saved_and_visual_and_finish_not_executed': True,
                'six_completed_primary_zero_job_names': [r['job'] for r in plan['six_actual_passed_jobs']],
                'source_guard': binding['root_spec']['completed_working_tree_chain'][-1]['source_guard'],
                'future_development_paused': True, 'commit_or_push_performed_by_collector': False,
                'payload_files': [FILES[name] for name in sorted(FILES)],
                'payload_count': len(FILES), 'payload_bytes': sum(r['source']['bytes'] for r in FILES.values()),
                'qualification': 'Incomplete UI calls and Source preparation are evidence, not successful tests or numbered completion.'}
    with (OUTPUT / 'archive-manifest.json').open('x', encoding='utf-8') as stream:
        json.dump(manifest, stream, ensure_ascii=False, indent=2); stream.write('\n')
    with (OUTPUT / 'README.md').open('x', encoding='utf-8') as stream:
        stream.write('第95节全量窗口检验在第三次尝试后搁置。六项真实0保留；前两次NULL不补写；第三次由Root预算取消，主退出143。全部公开证据按原始字节和SHA归档；不宣称全量PASS。后续开发暂停。\n')
    print(json.dumps({'status': manifest['status'], 'payload_files': len(FILES),
                      'payload_bytes': manifest['payload_bytes'], 'maintained_source_changes': 0,
                      'project_or_test_or_Wine_or_Git_executions': 0}))

if __name__ == '__main__':
    main()
