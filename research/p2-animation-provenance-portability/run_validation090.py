"""Run the explicitly bounded initial CLI and then the six new test methods."""
from pathlib import Path
import importlib.util
import json
import subprocess
import sys
import unittest

OUT = Path(__file__).resolve().parent
DRAFT = OUT / 'draft'


def write_json(name, value):
    with (OUT / name).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


mode = sys.argv[1]
assert (OUT / 'review-freeze090.json').exists(), 'Freeze must precede execution'
if mode == 'precheck':
    command = [sys.executable, '-I', str(DRAFT / 'scripts/verify_original_animation_provenance.py'),
               '--repository-root', str(DRAFT)]
    completed = subprocess.run(command, cwd=OUT, capture_output=True, text=True,
                               encoding='utf-8', timeout=20)
    with (OUT / 'precheck-stdout.json').open('x', encoding='utf-8') as stream:
        stream.write(completed.stdout)
    with (OUT / 'precheck-stderr.log').open('x', encoding='utf-8') as stream:
        stream.write(completed.stderr)
    report = json.loads(completed.stdout)
    receipt = {'format_version': 1, 'command': command, 'exit_code': completed.returncode,
               'CLI_invocations': 1, 'CLI_reported_verifier_entries': report['verifier_function_entries'],
               'direct_verifier_entries': 0, 'passed': completed.returncode == 0 and report['passed'],
               'tests': 0, 'application_API_project_helper_formatter_parser_network_Qt_Wine_calls': 0}
    write_json('precheck-operation090.json', receipt)
    print(json.dumps(receipt))
    raise SystemExit(0 if receipt['passed'] else 1)
assert mode == 'newtests'
precheck = json.loads((OUT / 'precheck-operation090.json').read_bytes())
assert precheck['passed'], 'No tests after a failed precheck'
sys.path.insert(0, str(DRAFT))
spec = importlib.util.spec_from_file_location('candidate_provenance_tests090',
                                            DRAFT / 'tests/test_original_animation_provenance.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
suite = unittest.defaultTestLoader.loadTestsFromTestCase(module.OriginalAnimationProvenanceTests)
assert suite.countTestCases() == 6
with (OUT / 'new-tests.log').open('x', encoding='utf-8', newline='\n') as stream:
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
ledger = dict(module.ENTRY_LEDGER)
count = ledger['CLI_reported_verifier_entries'] + ledger['direct_verifier_entries']
receipt = {'format_version': 1, 'tests_run': result.testsRun, 'failures': len(result.failures),
           'errors': len(result.errors), 'skips': len(result.skipped),
           'passed': result.wasSuccessful(), 'new_test_entry_ledger': ledger,
           'new_tests_verifier_function_entries': count,
           'precheck_CLI_invocations_separate': precheck['CLI_invocations'],
           'precheck_verifier_function_entries_separate': precheck['CLI_reported_verifier_entries'],
           'author_total_verifier_entries': count + precheck['CLI_reported_verifier_entries'],
           'fixed_budget_maximum': 28,
           'test_runs': 1, 'old_87_tests_or_matrices_repeated': False,
           'application_API_project_helper_formatter_source_parser_network_Qt_Wine_calls': 0}
write_json('new-tests-operation090.json', receipt)
print(json.dumps(receipt))
assert receipt['author_total_verifier_entries'] <= 28
assert ledger['CLI_invocations'] == ledger['CLI_reported_verifier_entries']
raise SystemExit(0 if receipt['passed'] else 1)
