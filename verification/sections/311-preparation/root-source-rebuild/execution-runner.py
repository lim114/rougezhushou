from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import json, subprocess, sys
ROOT = Path(__file__).resolve().parents[1]
out = ROOT / 'verification/sections/311-preparation/root-source-rebuild'
out.mkdir()
handoff = json.loads((ROOT / '.cache/p3-311-model/HANDOFF_FINAL.json').read_bytes())
names = set(handoff['promotion_files'])
names.update(p.relative_to(ROOT).as_posix() for p in (ROOT / 'research/p3-boss-hunt-311').rglob('*') if p.is_file())
def bound(): return {name: sha256((ROOT / name).read_bytes()).hexdigest() for name in sorted(names)}
before = bound()
argv = [sys.executable, '-B', '-X', 'utf8', 'scripts/build_boss_hunt_reference_311.py']
started = datetime.now(timezone.utc).isoformat()
with (out / 'stdout.txt').open('xb') as stdout, (out / 'stderr.txt').open('xb') as stderr:
    process = subprocess.Popen(argv, cwd=ROOT, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr)
    code = process.wait()
after = bound()
report = {'section': 311, 'kind': 'actual_canonical_source_rebuild_not_product_acceptance',
          'argv': argv, 'actual_retained_popen_pid': process.pid, 'actual_exit': code,
          'started_utc': started, 'ended_utc': datetime.now(timezone.utc).isoformat(),
          'source_sha256_before': before, 'source_sha256_after': after,
          'source_unchanged': before == after, 'passed': code == 0 and before == after}
(out / 'process.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
(out / 'process.exit').write_text(str(code) + '\n', encoding='ascii')
(out / 'execution-runner.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({key: value for key, value in report.items() if not key.startswith('source_sha')}, ensure_ascii=False))
raise SystemExit(0 if report['passed'] else 1)
