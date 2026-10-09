"""Root-only original743 real MainWindow probe; Source compiled, never run by author.

Observation only: complete/primary0 is not a product pass. Real Qt signal
exceptions and direct constructor exceptions are retained without inventing a
successful UI outcome. All persisted data is public and isolated.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import time
import traceback

APP_SHA = '34f0c92061460b239fd0af80ec263673765a16753826f6151fde87a88b89a35b'
VIEW_SHA = '5bef7b6f03592a5df615711568d116a0ffd9170f9be99832ca75d9eee78fcdb4'
SNACK = 'rogue_6_from_relic_13'
UNKNOWN_BOUND = 'public-unknown-char-buff-101'
UNKNOWN_PENDING = 'public-unknown-pending-buff-101'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def source_map(root):
    result = {}
    for folder in ('rouge', 'tests', 'scripts'):
        assert (root/folder).is_dir()
        for path in sorted((root/folder).rglob('*')):
            relative = path.relative_to(root)
            if '__pycache__' in relative.parts or path.suffix not in ('.py', '.json'):
                continue
            assert not path.is_symlink()
            if path.is_file():result[relative.as_posix()] = sha(path.read_bytes())
    return dict(sorted(result.items()))


def write_json(path, value):
    temporary = path.with_suffix(path.suffix+'.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2)+'\n', encoding='utf-8')
    os.replace(temporary, path)


def account():
    return {'id': 'mechanist', 'scope': 'operator_profile',
            'fields': {'elite': 2, 'level': 80, 'trust': 100, 'potential': 1,
                       'module_id': None, 'module_level': 0, 'selected_skill': 3},
            'skill_ranks': {'1': 7, '3': 10}, 'captured_at': 1000.0,
            'sources': {}, 'field_times': {}, 'skill_times': {}}


def member(kind):
    value = {**account(), 'scope': 'run', 'present': True,
             'recruitment_kind': 'non_emergency', 'char_buff_ids': [SNACK],
             'char_buffs_complete': False, 'char_buff_absent_ids': [],
             'char_buff_pending_ids': [], 'invalid_fields': [],
             'invalid_skill_ranks': [], 'missing_fields': []}
    if kind == 'unknown-bound':value['char_buff_ids'] = [UNKNOWN_BOUND]
    if kind == 'unknown-pending':value['char_buff_pending_ids'] = [UNKNOWN_PENDING]
    return value


def run_fixture(kind):
    return {'id': 'public-charbuff101-original', 'started_at': 0.0,
            'last_read': 1000.0, 'operators': {'mechanist': member(kind)},
            'crew_count': 1, 'selected_operator': 'mechanist',
            'relics': {}, 'relic_count': 0, 'bar_signature': [],
            'inventory_verified': True, 'inventory_confirmed_at': 1000.0,
            'relic_icon_memory': None, 'history': [], 'resources': {},
            'tactical_tools': {}, 'config': {}, 'maps': {},
            'last_node_content': None, 'node_contents': []}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', required=True)
    parser.add_argument('--guard', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    root = Path(args.root).resolve();output = Path(args.out).resolve()
    assert not output.exists() and output != root and root not in output.parents
    guard_path = Path(args.guard).resolve();guard_raw = guard_path.read_bytes()
    guard = json.loads(guard_raw)
    expected = guard.get('source_sha256', guard.get('source_sha256_after'))
    assert type(expected) is dict and len(expected) == 743
    assert expected['rouge/app.py'] == APP_SHA and expected['rouge/training_view.py'] == VIEW_SHA
    assert source_map(root) == expected
    output.mkdir(parents=True);(output/'public-state').mkdir()
    rows = [];qt_errors = [];active = {'id': 'preimport'};finished = threading.Event()
    receipt = {'kind': 'ROOT_ACTUAL_ORIGINAL743_CHARBUFF_MAINWINDOW_OBSERVATION',
               'product_pass': False, 'observation_complete': False,
               'runner_sha256': sha(Path(__file__).read_bytes()),
               'source_guard_path': str(guard_path), 'source_guard_sha256': sha(guard_raw),
               'source_before': expected, 'rows': rows, 'Qt_signal_exceptions': qt_errors,
               'started_at_UTC': datetime.now(timezone.utc).isoformat(),
               'private_state_access': False, 'game_chat_sampling_executed': False,
               'native_windows_verified': False, 'deadline_seconds': 300}
    old_hook = sys.excepthook;application = None;module = None;original_backend = None
    start = time.perf_counter()

    def deadline():
        if not finished.wait(300):
            write_json(output/'timeout.json', {'product_pass': False, 'active_case': active['id'],
                       'elapsed': time.perf_counter()-start, 'reason': 'Root-declared300sprobeBudget'})
            os._exit(124)

    def observed_exception(kind, error, trace):
        qt_errors.append({'case': active['id'], 'type': kind.__name__, 'message': str(error),
                          'traceback': ''.join(traceback.format_exception(kind, error, trace))})
        old_hook(kind, error, trace)

    threading.Thread(target=deadline, daemon=True).start();sys.excepthook = observed_exception
    try:
        sys.path.insert(0, str(root))
        from PySide6 import __version__ as pyside_version
        from PySide6.QtCore import qVersion
        from PySide6.QtWidgets import QApplication
        from rouge import app as module
        from rouge.run_state import RunState
        application = QApplication.instance() or QApplication([])
        receipt.update(python=sys.version, sys_platform=sys.platform,
                       pyside=pyside_version, qt=qVersion())
        assert pyside_version == '6.9.3' and qVersion() == '6.9.3'
        original_backend = module.DesktopBackend
        for identity in ('healthy-snack', 'unknown-bound', 'unknown-pending'):
            active['id'] = identity;window = None
            with tempfile.TemporaryDirectory(prefix='public-charbuff101-', dir=output/'public-state') as directory:
                folder = Path(directory);account_path = folder/'account.json';run_path = folder/'run.json'
                account_raw = (json.dumps({'mechanist': account()}, ensure_ascii=False, allow_nan=False, indent=2)+'\n').encode()
                run_raw = (json.dumps(run_fixture(identity), ensure_ascii=False, allow_nan=False, indent=2)+'\n').encode()
                account_path.write_bytes(account_raw);run_path.write_bytes(run_raw)
                loaded = RunState(run_path)
                assert not loaded.preserve_unreadable
                assert loaded.state['operators']['mechanist'] == member(identity)
                assert run_path.read_bytes() == run_raw
                module.OPERATOR_STATE = account_path;module.RUN_STATE = run_path;module.SETTINGS = folder/'settings.json'
                module.DesktopBackend = lambda _path, callback, public=folder: original_backend(public/'chat', callback)
                row = {'id': identity, 'original_JSON_accepted': True,
                       'fixture_member': member(identity),
                       'original_disk_sha256': {'account': sha(account_raw), 'run': sha(run_raw)},
                       'constructor_returned': False, 'Qt_signal_exceptions': []}
                start_errors = len(qt_errors)
                try:
                    window = module.MainWindow();row['constructor_returned'] = True
                    window.resize(1400, 1050);window.show();window.centralWidget().setCurrentIndex(1)
                    application.processEvents()
                    assert not window.auto.isChecked() and not window.timer.isActive()
                    assert not window.busy and not window.chat_busy and not window.desktop_request_busy
                    assert window.desktop.process is None and not window.desktop.pending
                    window.operator_choices.select_value('mechanist')
                    index = window.skill.findData(3);assert index >= 0
                    window.skill.setCurrentIndex(index);window.calculate();application.processEvents()
                    row.update(target_buff_status=window.target_buff_status.text(),
                               damage_text=window.damage_text.toPlainText(),
                               damage_result=window.damage_result,
                               displayed_level=window.level.value(),
                               actual_run_metadata=window.current_run_operator_state())
                    if identity == 'healthy-snack':
                        assert window.damage_result['result']['estimate']['skill']['sp_cost'] == 28
                        assert not qt_errors[start_errors:]
                except BaseException as error:
                    row['direct_exception'] = {'type': type(error).__name__, 'message': str(error),
                                               'traceback': traceback.format_exc()}
                    if identity == 'healthy-snack':raise
                finally:
                    for top in list(application.topLevelWidgets()):
                        if isinstance(top, module.MainWindow):
                            top.close();application.processEvents();top.deleteLater()
                    application.processEvents()
                    row['Qt_signal_exceptions'] = qt_errors[start_errors:]
                    row['original_disks_unchanged'] = account_path.read_bytes() == account_raw and run_path.read_bytes() == run_raw
                    row['tmp_absent'] = not account_path.with_suffix('.tmp').exists() and not run_path.with_suffix('.tmp').exists()
                    assert row['original_disks_unchanged'] and row['tmp_absent']
                    rows.append(row)
                    write_json(output/'progress.json', {'rows': rows, 'Qt_signal_exceptions': qt_errors})
                    print(json.dumps({'observed_case': identity, 'constructor_returned': row['constructor_returned'],
                                      'Qt_exceptions': len(row['Qt_signal_exceptions']),
                                      'direct_exception': row.get('direct_exception')}, ensure_ascii=False), flush=True)
        assert len(rows) == 3
        assert source_map(root) == expected
        receipt.update(observation_complete=True, elapsed_seconds=time.perf_counter()-start,
                       finished_at_UTC=datetime.now(timezone.utc).isoformat())
        return 0
    except BaseException as error:
        receipt['probe_failure'] = {'case': active['id'], 'type': type(error).__name__, 'message': str(error),
                                    'traceback': traceback.format_exc()}
        raise
    finally:
        if module is not None and original_backend is not None:module.DesktopBackend = original_backend
        sys.excepthook = old_hook
        write_json(output/'observations.json', receipt);finished.set()


if __name__ == '__main__':
    raise SystemExit(main())
