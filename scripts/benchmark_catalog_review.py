"""Measure a frozen source revision and this revision in separate Qt processes.

Only public catalogs and temporary empty state are used. No capture, chat,
credentials or public downloads are permitted. Does not measure recognition.
"""
from contextlib import ExitStack
from hashlib import sha256
from pathlib import Path
from statistics import median
from tempfile import TemporaryDirectory
from time import perf_counter
from types import ModuleType
from unittest.mock import patch
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
NAMES = ('expansion_reference', 'view_catalog', 'player_item_hover', 'player_inventory')


def frozen_modules(previous):
    import rouge
    for name in NAMES:
        canonical = 'rouge.' + name
        path = ROOT / 'rouge' / (name + '.py')
        module = ModuleType(canonical)
        # The code is frozen; asset paths still refer to identical public data.
        module.__file__ = str(path)
        module.__package__ = 'rouge'
        sys.modules[canonical] = module
        setattr(rouge, name, module)
        exec(compile((previous / path.name).read_bytes(), str(path), 'exec'), module.__dict__)


def data_projection(reference, inventory, pictures, public):
    packet = reference.packet()
    assert packet is not None
    result = {'categories': {name: {str(delta): reference.rows(name, changes_only=delta, reference=packet)
                            for delta in (False, True)} for name, _ in reference.CATEGORIES}}
    states = [{}, {'relics': {'rogue_6_relic_legacy_1': {},
                             'rogue_6_relic_legacy_3': {'held': False},
                             'rogue_6_relic_legacy_2': {'held': 'true'}}}]
    filters = [{}, {'rarity': 'NORMAL'}, {'rarity': 'RARE', 'exchange': False},
               {'kind': 'RELIC'}, {'kind': 'LEGACY'}, {'access': 'unlock'},
               {'access': 'special'}, {'access': 'uncovered'}, {'access': 'invalid'},
               {'source_node': '不期而遇'}, {'source_node': '不期'}, {'category': '不在图鉴中'}]
    result['inventories'] = [inventory.inventory_rows(state, query, held, public_data=public,
        version=version, packet=packet, **filters_)
        for state in states for query in ('', '希望', '独活') for held in (False, True)
        for version in ('base', 'dlc1', 'dlc2') for filters_ in filters]
    from rouge.catalog import catalog, operator_profiles
    result['operator_groups'] = [(name, [(title, key) for title, key, _ in rows])
        for name, rows in pictures.operator_groups(operator_profiles(), catalog()['operators'])]
    raw = json.dumps(result, ensure_ascii=False, separators=(',', ':'), sort_keys=True).encode()
    return {'exact_result_sha256': sha256(raw).hexdigest(),
            'inventory_combinations': len(result['inventories']), 'category_modes': 20,
            'operator_branches': len(result['operator_groups'])}


def run(mode, previous, output):
    if mode == 'before':
        frozen_modules(previous)
    from PySide6.QtWidgets import QApplication
    from rouge import app as a, public_archive, public_node_statistics
    from rouge import expansion_reference as reference, player_inventory as inventory, view_catalog as pictures
    app = QApplication.instance() or QApplication([])
    attempts = []

    def forbidden(name):
        def fail(*args, **kwargs):
            attempts.append(name)
            raise AssertionError(name)
        return fail

    with TemporaryDirectory(prefix='rouge-catalog-review-') as folder, ExitStack() as stack:
        root = Path(folder)
        for key, path in {'ROOT': root, 'SETTINGS': root/'settings.json',
                          'RUN_STATE': root/'run.json', 'OPERATOR_STATE': root/'operators.json'}.items():
            stack.enter_context(patch.object(a, key, path))
        backend = a.DesktopBackend
        stack.enter_context(patch.object(a, 'DesktopBackend', lambda _p, cb: backend(root/'chat', cb)))
        stack.enter_context(patch.object(a, 'list_game_windows', return_value=[]))
        for name in ('connect', 'capture', 'next_frame'):
            stack.enter_context(patch.object(a.GameCapture, name, side_effect=forbidden(name)))
        for name in ('start', 'request'):
            stack.enter_context(patch.object(backend, name, side_effect=forbidden('desktop_'+name)))
        for module, name in ((a, 'stream_chat'), (a, 'read_key'),
                             (public_archive, 'fetch'), (public_node_statistics, 'fetch')):
            stack.enter_context(patch.object(module, name, side_effect=forbidden(name)))
        start = perf_counter()
        window = a.MainWindow()
        construction_ms = (perf_counter()-start)*1000
        try:
            start = perf_counter()
            window.show_compact()
            app.processEvents()
            toolbar_ms = (perf_counter()-start)*1000
            panel = window.inventory_panel
            panel.held.setChecked(False)
            # Warm both versions consistently, then measure repeated real refresh.
            panel.refresh()
            samples = []
            for _ in range(7):
                start = perf_counter()
                panel.refresh()
                samples.append((perf_counter()-start)*1000)
            counts = []
            with patch.object(reference, 'packet', wraps=reference.packet) as packets, \
                    patch.object(inventory, 'inventory_rows', wraps=inventory.inventory_rows) as reads:
                panel.refresh()
                counts = {'packet_reads_per_refresh': packets.call_count,
                          'inventory_builds_per_refresh': reads.call_count}
            projection = data_projection(reference, inventory, pictures, public_archive.load())
        finally:
            window.close()
            app.processEvents()
    assert not attempts
    result = {'mode': mode, 'qpa': app.platformName(), 'passed': True,
              'construction_ms': construction_ms, 'first_toolbar_show_ms': toolbar_ms,
              'inventory_refresh_samples_ms': samples, 'inventory_refresh_median_ms': median(samples),
              'actual_calls': counts, 'projection': projection, 'forbidden_external_calls': attempts,
              'scope': 'public catalogs; isolated empty run; MainWindow construction excludes module imports and Python startup; not recognition or game performance',
              'source_sha256': {name: sha256(((previous if mode == 'before' else ROOT/'rouge') /
                                  (name+'.py')).read_bytes()).hexdigest() for name in NAMES},
              'private_state_used': False}
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x', encoding='utf8') as stream:
        stream.write(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=('before', 'after'), required=True)
    parser.add_argument('--previous', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run(args.mode, args.previous, args.output)
