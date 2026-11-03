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
modules = ['tests.test_event_named_reward_links_289', 'tests.test_event_named_reward_integration_289', 'tests.test_node_catalog', 'tests.test_node_rewards', 'tests.test_node_catalog_view', 'tests.test_node_resource_view', 'tests.test_event_planning', 'tests.test_choice_held_requirements', 'tests.test_original_destinations', 'tests.test_player_node_information_286', 'tests.test_player_information_view_286', 'tests.test_node_map_navigation', 'tests.test_node_history_workflow', 'tests.test_cloud_index_sync']
paths = set(ROOT.glob('rouge/**/*.py')) | set(ROOT.glob('rouge/data/*.json'))
paths |= {ROOT / ('tests/' + m.rsplit('.', 1)[-1] + '.py') for m in modules}
paths |= {ROOT / p for p in ('scripts/verify_full_available.py', 'scripts/update_cloud_index.py',
    'scripts/verify_event_rewards_window_289.py', 'scripts/build_event_named_reward_links_289.py')}
paths |= set(ROOT.glob('research/p3-event-named-rewards-289/*'))

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
