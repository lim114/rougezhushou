"""Check the existing native contract and the changed offline counter scope."""
import hashlib
import json
import sys
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
RESEARCH = ROOT / '.cache/research/ammo-capacity-062'
MODULES = ['tests.test_ammo_capacity_062', 'tests.test_ammo_counter_055', 'tests.test_ammo_refill_041']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_contract():
    directory = ROOT / '.cache/research/p1-angel-s2-055'
    extraction = json.loads((directory / 's2-counter-events.json').read_text(encoding='utf-8'))
    receipt = json.loads((directory / 'VERIFICATION.json').read_text(encoding='utf-8'))
    method = next(m for m in extraction['method_windows'] if m['entry_va'] == '0x180f517b0')
    assert not extraction['process_memory_read'] and not extraction['game_dll_executed']
    assert receipt['all_native_bytes_match_original']
    assert method['function_bytes'] == 221
    assert method['code_sha256'] == receipt['methods'][method['entry_va']]['code_sha256']
    instructions = {i['address']: i for i in method['instructions']}
    assert (instructions['0x180f51830']['mnemonic'], instructions['0x180f51830']['operands']) == ('add', 'eax, edi')
    assert (instructions['0x180f51837']['mnemonic'], instructions['0x180f51837']['operands']) == ('mov', 'dword ptr [rbx + 0x48], eax')
    raw = b''.join(bytes.fromhex(i['bytes']) for i in method['instructions'])
    assert len(raw) == 221 and hashlib.sha256(raw).hexdigest() == method['code_sha256']
    bookdir = ROOT / '.cache/research/p1-native-runtime-054'
    sealpath = bookdir / 'book-proof-seal.json'
    seal = json.loads(sealpath.read_text(encoding='utf-8'))
    for name, expected in seal['files'].items():
        assert sha(bookdir / name) == expected, name
    summary = json.loads((bookdir / 'timer-book-sniper-summary.json').read_text(encoding='utf-8'))
    # The full unchanged source, not only these selected instructions, remains
    # linked in the receipt. No claim about the current live hotfix is made.
    paths = [directory / 's2-counter-events.json', directory / 'VERIFICATION.json',
             directory / 'REPORT.md', sealpath, bookdir / 'timer-book-sniper-summary.json',
             *[bookdir / name for name in seal['files']]]
    return {p.relative_to(ROOT).as_posix(): sha(p) for p in paths}


def snapshot():
    paths = [*(ROOT / 'rouge').rglob('*.py'), *(ROOT / 'rouge/data').rglob('*.json'),
             Path(__file__), *[ROOT.joinpath(*m.split('.')).with_suffix('.py') for m in MODULES]]
    return {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(set(paths))}


def main():
    sources = source_contract()
    before = snapshot()
    RESEARCH.mkdir(parents=True, exist_ok=True)
    log = RESEARCH / ('tests-' + str(time.time_ns()) + '.log')
    with log.open('x', encoding='utf-8') as stream:
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(MODULES))
    after = snapshot()
    receipt = {
        'version': '0.62.0', 'passed': result.wasSuccessful() and before == after,
        'tests_run': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
        'skipped': len(result.skipped), 'test_modules': MODULES,
        'test_log': log.relative_to(ROOT).as_posix(), 'test_log_sha256': sha(log),
        'source_sha256': before, 'source_stable': before == after, 'mechanism_source_sha256': sources,
        'scope': 'Raw expenditure preservation and rejection of stale current-maximum parameters; no new skill callback schedule.',
        'recognition_changed': False, 'all_priority_1_completed': False,
        'private_state_used': False, 'game_actions': 0, 'chat_requests': 0,
    }
    with (ROOT / 'AMMO_0.62_VERIFICATION.json').open('x', encoding='utf-8') as stream:
        json.dump(receipt, stream, ensure_ascii=False, indent=2)
    print(json.dumps({k: receipt[k] for k in ('passed', 'tests_run', 'failures', 'errors', 'skipped', 'source_stable')}))
    return 0 if receipt['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
