"""Observe one actual read-only full380 sealer; preserve independent outputs."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import argparse
import json
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
def pin(path):
    raw = path.read_bytes()
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha256(raw).hexdigest(), 'bytes': len(raw)}
def now(): return datetime.now(timezone.utc).isoformat()
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sealer', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    sealer = (ROOT / args.sealer).resolve()
    out = (ROOT / args.output).resolve()
    assert sealer.is_relative_to(ROOT) and sealer.is_file() and not sealer.is_symlink()
    assert out.is_relative_to(ROOT / 'verification/full-380/postprocessing-schema-repair') and not out.exists()
    out.mkdir(parents=True)
    bindings = {
        'expected-parent-commit': 'afab40c3bb4ea8b95118e8cbe34aa07204c1c615',
        'freeze-sha256': 'f0934fc4bb9fbd1fe91283d84057cb6486b31e11b3f2980ac4e783e0fe507e42',
        'activation-sha256': 'ff1d8f06ad2adf01648cca5acfc86de0ac9b836db25f8757cd20d966a456b326',
        'archive-manifest-sha256': '295e4af98dff32d3d175e09b9b6d0870addf3ea8883ab4d675152d50cc663ab1',
        'visual-sha256': 'b93e1d24f9c0fa5b467635cec44eb56003b974734dabb29b381349b67aef4ec3',
        'review-helper-sha256': '9152bc20f74886d82d7f27370b5b2c618b8bfd5d23630d74c295a0ecf47f4001',
    }
    argv = [sys.executable, '-B', '-X', 'utf8', str(sealer), '--seal', '--attempt', '2']
    for key, value in bindings.items(): argv.extend(['--'+key, value])
    guarded = ['verification/full-380/source-freeze-attempt2.json',
        '.cache/full380-prepared/attempt-2/activation380.json',
        'verification/full-380/execution-attempt2/archive-manifest.json',
        'verification/full-380/root-visual-review.json',
        '.cache/full380-prepared/attempt-2/review_results380.py',
        'verification/full-380/public-prior-visual-registry.json',
        'verification/full-380/execution-summary380.py']
    before = [pin(ROOT / name) for name in guarded]
    started = now(); start = time.monotonic()
    with (out / 'stdout.txt').open('xb') as stdout, (out / 'stderr.txt').open('xb') as stderr:
        process = subprocess.Popen(argv, cwd=ROOT, stdout=stdout, stderr=stderr)
        exit_code = process.wait()
    after = [pin(ROOT / name) for name in guarded]
    assert after == before, 'Read-only sealer altered protected authority'
    summary = ROOT / 'verification/full-380/summary.json'
    receipt = {'section': 380, 'kind': 'ACTUAL_READONLY_POSTPROCESSING_SEALER_OBSERVATION',
        'started_UTC': started, 'finished_UTC': now(), 'elapsed_seconds': time.monotonic()-start,
        'argv': argv, 'retained_Popen_pid': process.pid, 'actual_observed_child_exit': exit_code,
        'sealer': pin(sealer), 'stdout': pin(out / 'stdout.txt'), 'stderr': pin(out / 'stderr.txt'),
        'guarded_authority_before': before, 'guarded_authority_after': after,
        'guarded_authority_unchanged': True, 'summary_exists_after': summary.exists(),
        'summary': pin(summary) if summary.exists() else None,
        'tests_windows_reviewer_reexecuted': False, 'game_operated': False, 'chat_sent': False,
        'private_state_read_copied_or_restored': False}
    with (out / 'process.json').open('xb') as stream:
        stream.write((json.dumps(receipt, ensure_ascii=False, indent=2)+'\n').encode('utf8'))
    print(json.dumps({'receipt': pin(out / 'process.json'), 'actual_observed_child_exit': exit_code,
        'summary_exists_after': summary.exists()}, ensure_ascii=False))
    return exit_code
if __name__ == '__main__': raise SystemExit(main())
