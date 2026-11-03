"""Record a bounded necessary check run; never replaces full validation."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path.cwd()
DEST = ROOT / sys.argv[1]
DEST.mkdir(parents=True, exist_ok=False)
modules = ['tests.test_direct_landmark_288', 'tests.test_player_tile_information_288', 'tests.test_direct_landmark_mapping', 'tests.test_direct_landmark_extension', 'tests.test_map_direct_continuation', 'tests.test_map_projection_048', 'tests.test_map_projection_049', 'tests.test_map_projection_051', 'tests.test_map_ground_extension', 'tests.test_player_information_view_286', 'tests.test_battle_reward_planning', 'tests.test_moving_reward_integration_287', 'tests.test_player_node_information_286', 'tests.test_player_battle_information_286', 'tests.test_readable_battle_047', 'tests.test_cloud_index_sync']
paths = set(ROOT.glob('rouge/**/*.py')) | set(ROOT.glob('rouge/data/*.json'))
paths |= {ROOT / ('tests/' + m.rsplit('.', 1)[-1] + '.py') for m in modules}
paths |= {ROOT / p for p in ('scripts/verify_full_available.py', 'scripts/update_cloud_index.py',
    'scripts/verify_direct_map_window_288.py', 'scripts/extend_direct_landmark_288.py')}
paths |= set(ROOT.glob('research/p3-map-direct-road-288/*'))

def hashes():
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(paths) if p.is_file()}

before = hashes()
env = dict(os.environ, QT_QPA_PLATFORM='offscreen', PYTHONDONTWRITEBYTECODE='1')
argv = [sys.executable, '-B', '-X', 'utf8', '-m', 'unittest', '-v', *modules]
started = datetime.now(timezone.utc).isoformat()
with (DEST / 'stdout.txt').open('xb') as stdout, (DEST / 'stderr.txt').open('xb') as stderr:
    result = subprocess.run(argv, cwd=ROOT, env=env, stdout=stdout, stderr=stderr)
after = hashes()
report = {'kind': 'necessary_change_related_tests_not_full_suite', 'argv': argv,
          'modules': modules, 'source_commit_before': subprocess.check_output(
              ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
          'started_utc': started, 'finished_utc': datetime.now(timezone.utc).isoformat(),
          'exit_code': result.returncode, 'source_sha256_before': before,
          'source_sha256_after': after, 'source_unchanged': before == after,
          'game_sampling_verified': False, 'chat_verified': False,
          'full_scope_reduced': False, 'full_suite_rerun': False}
(DEST / 'process.json').write_bytes((json.dumps(report, ensure_ascii=False, indent=2) + '\n').encode('utf8'))
print(json.dumps({'exit_code': result.returncode, 'source_unchanged': before == after,
                  'receipt': str(DEST / 'process.json')}))
raise SystemExit(result.returncode if before == after else 97)
