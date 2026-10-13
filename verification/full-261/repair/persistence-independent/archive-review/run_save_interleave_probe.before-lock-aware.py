"""Actual RunState.save with a barrier only around the real write-phase return."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import threading

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from rouge.run_state import RunState
import rouge.persistence_install as install

sources = [ROOT / 'rouge/run_state.py', ROOT / 'rouge/persistence_install.py']
source_hashes = lambda: {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in sources}
receipt = {'source_sha256_before': source_hashes(), 'cases': [],
           'actual_RunState_save': True, 'actual_public_temporary_io': True,
           'only_test_seam': 'barrier around the real write_temporary_record return; no IO/result substituted',
           'native_windows_verified': False, 'game_actions': 0, 'chat_requests': 0}
for initial in (True, False):
    with tempfile.TemporaryDirectory(prefix='public-261-run-save-interleave-') as folder:
        destination = Path(folder) / 'run.json'
        if not initial:
            seed = RunState(destination)
            assert seed.save() is True
        first, second = RunState(destination), RunState(destination)
        first.state['id'] = '00000000-0000-4000-8000-00000000000a'
        second.state['id'] = '00000000-0000-4000-8000-00000000000b'
        ready = {'A': threading.Event(), 'B': threading.Event()}
        release = {'A': threading.Event(), 'B': threading.Event()}
        actual_write = install.write_temporary_record
        outcomes = {}
        def barrier_write(path, text):
            result = actual_write(path, text)
            identity = 'A' if json.loads(text)['id'] == first.state['id'] else 'B'
            ready[identity].set()
            assert release[identity].wait(5), 'phase-release timeout'
            return result
        def save(identity, state):
            try:
                outcomes[identity] = {'returned': state.save(), 'save_issue': state.save_issue}
            except BaseException as error:
                outcomes[identity] = {'unexpected_error': repr(error)}
        install.write_temporary_record = barrier_write
        a = threading.Thread(target=save, args=('A', first))
        b = threading.Thread(target=save, args=('B', second))
        try:
            a.start()
            assert ready['A'].wait(5), 'A never reached real write-phase boundary'
            b.start()
            assert ready['B'].wait(5), 'B never reached real write-phase boundary'
            release['A'].set()
            a.join(5)
            assert not a.is_alive()
            published_by_a = json.loads(destination.read_text(encoding='utf-8'))['id']
            release['B'].set()
            b.join(5)
            assert not b.is_alive()
            receipt['cases'].append({'first_install': initial, 'outcomes': outcomes,
                'first_writer_own_id': first.state['id'], 'second_writer_own_id': second.state['id'],
                'id_published_by_first_save': published_by_a,
                'first_save_returned_success_and_published_other_state':
                    outcomes['A'].get('returned') is True and published_by_a != first.state['id']})
        finally:
            release['A'].set(); release['B'].set()
            a.join(5)
            if b.ident is not None:
                b.join(5)
            install.write_temporary_record = actual_write
receipt['source_sha256_after'] = source_hashes()
receipt['source_drift'] = receipt['source_sha256_after'] != receipt['source_sha256_before']
print(json.dumps(receipt, ensure_ascii=False, indent=2))
