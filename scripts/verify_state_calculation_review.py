"""Replay public GUI updates against frozen/current source, without game or chat.

Separate before/after processes produce exact full-result/report hashes. This
checks UI input propagation, not independent correctness of all skill mechanics.
"""
from contextlib import ExitStack
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter
from types import ModuleType
from unittest.mock import patch
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
SOURCES = ('ui_state', 'app')


def run(mode, previous, output):
    if mode == 'before':
        import rouge
        for name in SOURCES:
            module = ModuleType('rouge.'+name)
            path = ROOT/'rouge'/(name+'.py')
            module.__file__, module.__package__ = str(path), 'rouge'
            sys.modules[module.__name__] = module
            setattr(rouge, name, module)
            exec(compile((previous/path.name).read_bytes(), str(path), 'exec'), module.__dict__)
    from PySide6.QtWidgets import QApplication
    import numpy as np
    from rouge import app as a, public_archive, public_node_statistics
    from rouge.catalog import catalog
    gui = QApplication.instance() or QApplication([])
    forbidden = []

    def fail(name):
        def called(*args, **kwargs):
            forbidden.append(name)
            raise AssertionError(name)
        return called

    def digest(value):
        return sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                 separators=(',', ':')).encode()).hexdigest()

    with TemporaryDirectory(prefix='rouge-state-review-') as folder, ExitStack() as stack:
        root = Path(folder)
        for key, path in {'ROOT': root, 'SETTINGS': root/'settings.json',
                          'RUN_STATE': root/'run.json', 'OPERATOR_STATE': root/'account.json'}.items():
            stack.enter_context(patch.object(a, key, path))
        backend = a.DesktopBackend
        stack.enter_context(patch.object(a, 'DesktopBackend', lambda _p, cb: backend(root/'chat', cb)))
        stack.enter_context(patch.object(a, 'list_game_windows', return_value=[]))
        for name in ('connect', 'capture', 'next_frame'):
            stack.enter_context(patch.object(a.GameCapture, name, side_effect=fail(name)))
        for name in ('start', 'request'):
            stack.enter_context(patch.object(backend, name, side_effect=fail('desktop_'+name)))
        for owner, name in ((a, 'stream_chat'), (a, 'read_key'),
                            (public_archive, 'fetch'), (public_node_statistics, 'fetch')):
            stack.enter_context(patch.object(owner, name, side_effect=fail(name)))
        w = a.MainWindow()
        rows = []

        def check(label, action):
            with patch.object(a, 'calculate_damage', wraps=a.calculate_damage) as engine, \
                    patch.object(w.run, 'held_relic_ids', wraps=w.run.held_relic_ids) as held:
                start = perf_counter()
                action()
                elapsed = (perf_counter()-start)*1000
            rows.append({'action': label, 'calculate_damage_calls': engine.call_count,
                'held_relic_ids_calls': held.call_count, 'elapsed_ms': elapsed,
                'operator': w.operator.currentData(), 'skill': w.skill.currentData(),
                'level': w.level.value(), 'has_result': w.damage_result is not None,
                'result_sha256': digest(w.damage_result),
                'report_sha256': sha256(w.damage_text.toPlainText().encode()).hexdigest()})

        try:
            w.select_operator('mechanist')
            w.run.state['started_at'], w.run.state['id'] = 1000, 'public-state-review'
            fields = {'elite': 1, 'level': 80, 'potential': 1, 'trust': 100,
                      'module_id': None, 'module_level': 0, 'selected_skill': 1}
            observed = {'operators': [{'id': 'mechanist', 'scope': 'run',
                'fields': fields, 'skill_ranks': {'1': 7}, 'present': True}],
                'selected_operator': 'mechanist',
                'relics': {'ids': [], 'icons': [], 'count': 0, 'source': 'held_bar'},
                'config': {'difficulty': {'value': 10, 'source': 'label'}}}
            check('run_observation', lambda: w.apply_run_observation(deepcopy(observed), 1001))
            check('repeated_frame', lambda: w.apply_run_observation(deepcopy(observed), 1002))
            check('manual_skill', lambda: w.skill.setCurrentIndex(w.skill.findData(2)))
            check('manual_level', lambda: w.level.setValue(75))
            check('manual_operator_switch', lambda: w.select_operator('silverash'))
            check('repeat_does_not_steal_browsing', lambda: w.apply_run_observation(deepcopy(observed), 1003))
            check('sync_relic_checkboxes', w.sync_run_relics)
            w.select_operator('mechanist')
            account = {'id': 'mechanist', 'scope': 'operator_profile',
                       'fields': {**fields, 'elite': 2, 'level': 90}, 'skill_ranks': {'1': 10}}
            frame = {'captured_at': 1004, 'page': 'operator_detail', 'nodes': [],
                     'run': observed, 'operator': account}
            check('combined_run_and_account_frame', lambda: w.sample_received(
                (np.zeros((64, 96, 3), dtype=np.uint8), deepcopy(frame))))
            # Use explicit profile previews for the same complete UI skill sweep.
            w.use_run_training.setChecked(False)
            for op in catalog()['operators']:
                w.select_operator(op)
                for index in range(w.skill.count()):
                    skill = w.skill.itemData(index)
                    check(op+'/S'+str(skill), lambda index=index: w.skill.setCurrentIndex(index))
            state_digest = digest(w.run.state)
            account_digest = digest(w.account_cache.records)
        finally:
            w.close()
            gui.processEvents()
    assert not forbidden
    projection = [{k: v for k, v in row.items() if k not in
                   ('calculate_damage_calls', 'held_relic_ids_calls', 'elapsed_ms')} for row in rows]
    result = {'passed': True, 'mode': mode, 'qpa': gui.platformName(), 'rows': rows,
              'final_run_sha256': state_digest, 'final_account_sha256': account_digest,
              'full_UI_result_and_report_sha256': digest(projection),
              'skill_combinations': sum('/S' in row['action'] for row in rows),
              'forbidden_external_calls': forbidden, 'private_state_used': False,
              'scope': 'public inputs, temporary state, actual synchronous UI and calculation; not independent skill-mechanism validation, recognition or live game',
              'source_sha256': {name: sha256(((previous if mode == 'before' else ROOT/'rouge') /
                                  (name+'.py')).read_bytes()).hexdigest() for name in SOURCES}}
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x', encoding='utf8') as stream:
        stream.write(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'passed': True, 'mode': mode, 'actions': len(rows),
                     'skills': result['skill_combinations'],
                     'projection': result['full_UI_result_and_report_sha256'],
                     'first_actions': rows[:8]}, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=('before', 'after'), required=True)
    parser.add_argument('--previous', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run(args.mode, args.previous, args.output)
