"""Execute exactly the nine frozen new methods by explicit file import."""
import importlib.util
import json
import sys
import unittest
from pathlib import Path

OUT = Path(__file__).resolve().parent
source = OUT.with_name('p2-orchid-near-text-085') / 'draft'
sys.path.insert(0, str(source))
spec = importlib.util.spec_from_file_location('independent_frozen_new_tests085', source / 'tests/test_orchid_near_text_input.py')
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
suite = unittest.defaultTestLoader.loadTestsFromModule(module)
result = unittest.TextTestRunner(verbosity=2).run(suite)
receipt = {'passed': result.wasSuccessful(), 'source': str(source), 'tests_run': result.testsRun,
    'skipped': result.skipped, 'failures': [(str(t), err) for t, err in result.failures],
    'errors': [(str(t), err) for t, err in result.errors], 'old_related40_not_repeated': True,
    'gui_executed': False, 'wine_executed': False, 'tracked_edits': False}
(OUT / 'independent-new-tests085.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(receipt, ensure_ascii=False))
assert result.testsRun == 9 and not result.skipped and result.wasSuccessful()
