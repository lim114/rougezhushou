"""Archive the actual five-section validation without incrementing section 100."""
import datetime
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    spec_path = Path(sys.argv[1])
    spec = json.loads(spec_path.read_bytes())
    root = Path('/workspace/rougezhushou')
    assert subprocess.check_output(['git', 'branch', '--show-current'], cwd=root, text=True).strip() == 'codex/p2-development'
    assert not subprocess.check_output(['git', 'status', '--porcelain'], cwd=root, text=True).strip()
    guard = json.loads(Path(spec['guard']).read_bytes())
    actual = {p.relative_to(root).as_posix(): sha(p) for name in ('rouge', 'tests', 'scripts')
              for p in sorted((root/name).rglob('*')) if p.is_file() and p.suffix in ('.py', '.json') and '__pycache__' not in p.parts}
    assert actual == guard['source_sha256'] and len(actual) == 743
    for name, value in guard['source_additional_sha256'].items():
        assert sha(root/name) == value
    for path in spec['successful_primary_files']:
        assert Path(path).read_bytes() == b'0\n', path
    linux = json.loads(Path(spec['linux_full']).read_bytes())
    wine = json.loads(Path(spec['wine_full']).read_bytes())
    selected = json.loads(Path(spec['wine_selected']).read_bytes())
    for receipt in (linux, wine):
        assert receipt['available_checks_passed'] is True
        assert receipt['failures'] == receipt['errors'] == 0
        assert not receipt['source_drift']
    assert selected['passed'] is True and not selected['source_drift']
    for receipt in (wine, selected):
        assert not receipt['adapter_source_drift'] and not receipt['source_additional_drift']
    gui = json.loads(Path(spec['gui_receipt']).read_bytes())
    supervisor = json.loads(Path(spec['gui_supervisor']).read_bytes())
    raw_gui = Path(spec['gui_primary']).read_bytes()
    if gui.get('passed') is True:
        assert raw_gui == b'0\n' and supervisor['child_primary_exit'] == supervisor['supervisor_exit'] == 0
        assert gui['complete_ui_validation'] is True
        saved = json.loads(Path(spec['saved_audit']).read_bytes())
        assert saved['passed'] is True and saved['saved_states'] == 52 and saved['actual_gui_checks'] == 4283
        visual = json.loads(Path(spec['visual_audit']).read_bytes())
        assert visual['actually_viewed_pngs'] == 4 and visual['pngs'] == gui['screenshots100']
        status = 'PASSED_AVAILABLE_MAINTAINED_AND_BOUNDED_GUI_SCOPE'
    else:
        assert raw_gui != b'0\n' and spec['actual_gui_attempts'] == 3
        assert spec['gui_deferred_after_three'] is True
        status = 'AVAILABLE_SUITES_PASSED_GUI_DEFERRED_AFTER_THREE_ACTUAL_ATTEMPTS'
    stamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    assert head == '8436f906842cd45b7553d8f54f2b0efc0619f097'
    archive = root/'verification/full-100'
    assert not archive.exists()
    entries = list(spec['files'])
    for path, destination in ((spec_path, 'root-archive-spec.json'), (Path(__file__), 'root-full100-archive-v1.py')):
        entries.append({'source_path': str(path), 'archive_path': destination, 'bytes': path.stat().st_size, 'sha256': sha(path)})
    paths = set()
    for row in entries:
        source = Path(row['source_path'])
        relative = Path(row['archive_path'])
        assert source.is_file() and not source.is_symlink()
        assert not any(part in source.parts for part in ('.local', '.venv', '.git', '__pycache__'))
        assert not relative.is_absolute() and '..' not in relative.parts and relative.as_posix() not in paths
        paths.add(relative.as_posix())
        assert source.stat().st_size == row['bytes'] and sha(source) == row['sha256'], source
    archive.mkdir(parents=True)
    copied = []
    for row in entries:
        source = Path(row['source_path']); destination = archive/row['archive_path']
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        assert destination.stat().st_size == row['bytes'] and sha(destination) == row['sha256']
        copied.append({'path': row['archive_path'], 'original': str(source), 'bytes': row['bytes'], 'sha256': row['sha256']})
    manifest = {'kind': 'ROOT_ACTUAL_EXPLICIT_PUBLIC_ARCHIVE_BYTE_VERIFIED', 'files': copied,
                'file_count': len(copied), 'total_bytes': sum(row['bytes'] for row in copied),
                'prepared_at_Beijing': stamp, 'private_state_included': False}
    (archive/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
    (archive/'REPORT_ZH.md').write_text(spec['report_zh']+'\n')
    (archive/'README.md').write_text(spec['readme']+'\n')
    closure = {'after_section': 100, 'completed_section_increment': 0, 'status': status,
               'available_checks_passed': gui.get('passed') is True,
               'batch_validation_closed': True, 'complete_repository_validation': False,
               'native_windows_game_chat_verified': False, 'product_commit': head,
               'validated_at_Beijing': stamp, 'archive': 'verification/full-100',
               'linux': {key:linux[key] for key in ('tests_run', 'tests_passed', 'historical_or_declared_skips', 'unavailable_records', 'unavailable_parent_count', 'failures', 'errors')},
               'linux_receipt_source_files': len(linux['source_sha256']),
               'wine': {key:wine[key] for key in ('tests_run', 'tests_passed', 'historical_or_declared_skips', 'unavailable_records', 'unavailable_parent_count', 'failures', 'errors', 'environment_capability_skips')},
               'selected_wine': {key:selected[key] for key in ('tests_run', 'skipped', 'failures', 'errors')},
               'gui_passed': gui.get('passed') is True, 'actual_gui_attempts': spec['actual_gui_attempts'],
               'main_source_files': 743, 'supplemental_CORE_verified': True,
               'full095_deferred_preserved': True,
               'old095_complete_function_vector_measured': False,
               'saved_legacy_codec_aliases_verified': False,
               'scope': 'Maintained available selectors plus bounded healthy full090 functional Qt suite on current100; specialist96-100 receipts remain separately archived.'}
    (archive/'closure.json').write_text(json.dumps(closure, ensure_ascii=False, indent=2)+'\n')
    cp_path = root/'DEVELOPMENT_CHECKPOINT.json';cp = json.loads(cp_path.read_bytes())
    assert cp['completed_sections'] == 100 and cp['next_section'] == 101
    cp['current_full100_checkpoint'] = closure
    cp['full_validation_due'] = False
    cp['current_batch_commit_policy']['next_full_validation_after'] = 105
    cp['next_action'] = '依序推进101缓存消费者安全、102库存确认资格与遗漏回归登记；每节实际检验/归档/commit/push，105后再次全量并总结。机制未知须有资料；native Windows/game/chat仍未验。'
    cp['last_verified_cloud_save'] = {'section':100, 'commit':head, 'remote':'origin codex/p2-development', 'proof':'verification/full-100/product100/section100-publication-v1.json'}
    cp['current_section_save']['status'] = 'ACTUAL_COMMITTED_PUSHED_REMOTE_EQUAL_CLEAN'
    cp['current_section_save']['actual_commit_sha'] = head
    if gui.get('passed') is True:
        cp['last_full_validation'] = closure
    else:
        cp['deferred_problems'].append({'id':'full100_bounded_GUI', 'failed_attempts':3, 'counts_as_passed':False, 'evidence':'verification/full-100', 'restart_conditions':'Obtain independent new diagnosis or changed verified runtime prerequisite; do not perform fourth identical full100 GUI attempt.'})
    cp_path.write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n')
    paragraph = f'## 第96–100节五节检查完成记录\n\n{stamp}（北京时间）。{status}。Linux 2036项、Wine 2100项的可用维护检查无失败/错误；跳过与不可用仍单列。窗口结果见 verification/full-100/closure.json。96–100五次实际提交均已推送；当前编号仍100，下一节101。P2三组机制缺口保留，不以缓存修复冒称机制完成；原生Windows、游戏、聊天未验。每节保存，105后再作五节总结。\n\n---\n\n'
    for name in ('WORK_IN_PROGRESS.md', 'PROJECT_COMPLETED.md'):
        path = root/name;path.write_text(paragraph+path.read_text())
    for path, value in guard['source_sha256'].items():
        assert sha(root/path) == value
    print(json.dumps({'status':status, 'completed_sections':100, 'next_section':101, 'archive_files':len(copied), 'archive_bytes':manifest['total_bytes'], 'source_files':743},ensure_ascii=False))


if __name__ == '__main__':
    main()
