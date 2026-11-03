"""Execute only directly related prior tests, with public call accounting."""
import json
import sys
import unittest
from pathlib import Path

OUT = Path(__file__).resolve().parent
TARGET = OUT / 'draft'
sys.path.insert(0, str(TARGET))
import rouge.damage as damage

real_calculate = damage.calculate_damage
calls = 0


def calculate(*args, **kwargs):
    global calls
    calls += 1
    return real_calculate(*args, **kwargs)


damage.calculate_damage = calculate
patterns = ['test_neural_relic_034.py', 'test_neural_sources_035.py',
            'test_mantra_events_024.py', 'test_mantra_manual_events.py',
            'test_mantra_talent_qualification.py', 'test_neural_incoming_count_metadata.py',
            'test_s1_neural_boundary.py', 'test_neural_incoming_clock.py']
suite = unittest.TestSuite()
for pattern in patterns:
    suite.addTests(unittest.defaultTestLoader.discover(str(TARGET / 'tests'), pattern=pattern))
result = unittest.TextTestRunner(verbosity=2).run(suite)
receipt = {'passed': result.wasSuccessful(), 'tests': result.testsRun, 'skipped': len(result.skipped),
           'failures': len(result.failures), 'errors': len(result.errors), 'API_calls': calls,
           'patterns': patterns, 'new_nine_tests_not_repeated': True}
(OUT / 'related-tests083.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt))
sys.exit(0 if result.wasSuccessful() else 1)
