import datetime
import hashlib
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent
PYTHON = '/workspace/rougezhushou/.venv/bin/python'
RELATED = ['test_damage', 'test_charge_reference', 'test_empty_enemy_scope', 'test_impact_delay_037']
RELATED += ['test_enemy_environment.EnemyEnvironmentTests.' + name for name in (
    'test_relic_enemy_modifiers_follow_stage_and_difficulty_and_are_reported',
    'test_portal_keeps_main_depth_and_missing_context_does_not_guess',
    'test_boss_reduction_is_independent_from_relic_vulnerability_and_preserves_healing_and_timing',
    'test_emergency_stage_and_region_use_pinned_enemy_instead_of_manual_defense')]
runs = []
for label, package, tests, expected in (
        ('baseline-related', 'baseline', RELATED, 0),
        ('baseline-new-regression', 'baseline', ['test_declared_count_input_types'], 1),
        ('draft-related-and-new', 'draft', RELATED + ['test_declared_count_input_types'], 0)):
    test_path = ROOT / ('draft/tests' if label == 'baseline-new-regression' else package + '/tests')
    command = [PYTHON, '-m', 'unittest', *tests]
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1',
               PYTHONPATH=str(ROOT / package) + ':' + str(test_path))
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    completed = subprocess.run(command, cwd=ROOT / package, env=env,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    log = ROOT / f'{label}.log'
    log.write_text(completed.stdout)
    assert completed.returncode == expected, (label, completed.stdout)
    runs.append({'label': label, 'command': command, 'cwd': str(ROOT / package),
                 'started_utc': started, 'exit_code': completed.returncode,
                 'expected_exit_code': expected, 'log': str(log),
                 'log_sha256': hashlib.sha256(log.read_bytes()).hexdigest(),
                 'summary': [line for line in completed.stdout.splitlines()
                             if line.startswith(('Ran ', 'FAILED ', 'OK'))]})
receipt = {'initial_discovery_attempt': {
    'cwd': str(ROOT / 'draft'), 'tests_run': 87, 'exit_code': 1, 'errors': 2,
    'scope': 'All six copied old modules plus new tests; two unrelated prerequisites absent.',
    'missing': ['tests.offline_scope_retirement', 'samples/native-client/run-map-empty.png'],
    'resolution': 'Use the relevant calculation modules and four enemy calculation/state methods; omit legacy retired-source test import and screenshot-dependent recognition method. No private/untracked screenshot copied.'},
    'fresh_related_runs': runs}
(ROOT / 'test-receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(receipt, ensure_ascii=False))
