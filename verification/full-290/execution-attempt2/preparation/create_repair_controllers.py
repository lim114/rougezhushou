"""Prepare only a new290 repair namespace; do not freeze or launch anything."""
from pathlib import Path
import ast
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ORIGINAL = ROOT / '.cache/p3-full290-prep'
first_freeze = ROOT / 'verification/full-290/source-freeze.json'
names = ('full290_runtime_common.py', 'prepare_full290_window.py',
         'produce_final_freeze_290.py', 'run_full290_orchestration.py',
         'offline290_launcher.py', 'archive_full290_outputs.py',
         'run_p3_supplementary_windows_290.py', 'supplementary290_launcher.py',
         'archive_p3_supplementary_290.py', 'inventory_environment_290.py')


def exact_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError('One exact reviewed anchor required: ' + old[:100])
    return text.replace(old, new, 1)


records = {}
for name in names:
    path = ORIGINAL / name
    original = path.read_bytes()
    text = original.decode('utf8')
    text = text.replace('.cache/p3-full290-prep', '.cache/p3-full290-repair-prep')
    text = text.replace('verification/full-290/source-freeze.json', 'verification/full-290/source-freeze-repair.json')
    text = text.replace('execution-attempt1', 'execution-attempt2').replace('p3-supplementary-attempt1', 'p3-supplementary-attempt2')
    text = text.replace('rouge-full290-', 'rouge-full290-repair-')
    # Fresh attempt authorities; historical275/261 filenames and fixture
    # assertions stay unchanged and remain explicitly historical.
    text = text.replace('FULL290_ROOT_OWNED_ACTUAL_EXECUTION', 'FULL290_REPAIR_ROOT_OWNED_ACTUAL_EXECUTION')
    text = text.replace('FULL290_ROOT_OWNED_P3_SUPPLEMENTARY_EXECUTION', 'FULL290_REPAIR_ROOT_OWNED_P3_SUPPLEMENTARY_EXECUTION')
    text = text.replace('FULL290_FOUR_COMMAND_ORCHESTRATION', 'FULL290_REPAIR_FOUR_COMMAND_ORCHESTRATION')
    text = text.replace('FULL290_P3_FIVE_WINDOW_ORCHESTRATION', 'FULL290_REPAIR_P3_FIVE_WINDOW_ORCHESTRATION')
    if name == 'full290_runtime_common.py':
        text = exact_once(text, "    if supplemental_public_inputs() != data.get('supplemental_public_inputs_sha256'):",
            "    if data.get('actual_validation_attempt') != 2:\n        raise ValueError('This namespace accepts only actual290 repair attempt2')\n    if supplemental_public_inputs() != data.get('supplemental_public_inputs_sha256'):")
    if name == 'prepare_full290_window.py':
        text = text.replace('verification/full-285/source-freeze.json', 'verification/full-290/source-freeze.json')
        text = exact_once(text,
            "    text = text.replace('SECTION275_ACTUAL_WINDOWS_OWNED_POPEN_SUPERVISION', 'SECTION290_ACTUAL_WINDOWS_OWNED_POPEN_SUPERVISION')",
            "    text = text.replace('SECTION275_ACTUAL_WINDOWS_OWNED_POPEN_SUPERVISION', 'SECTION290_ATTEMPT2_ACTUAL_WINDOWS_OWNED_POPEN_SUPERVISION')\n    text = text.replace('0<args.timeout<=1200', '0<args.timeout<=1800').replace('bounded <=1200-second', 'bounded <=1800-second')")
        text = text.replace('actual_full290_native_attempt=1', 'actual_full290_native_attempt=2')
        text = exact_once(text, "'binding_ready': True, 'runtime_executed': False, 'actual_section': 290,",
            "'binding_ready': True, 'runtime_executed': False, 'actual_section': 290, 'actual_validation_attempt': 2,")
    if name == 'produce_final_freeze_290.py':
        text = text.replace('verification/full-285/source-freeze.json', 'verification/full-290/source-freeze.json')
        text = text.replace('Previous full285 source/selector scope was removed', 'Attempt1 full290 source/selector scope was removed')
        text = exact_once(text, "    before = runner_api_snapshot()", "    before = runner_api_snapshot()\n    import ast\n    parser_tree = ast.parse((ROOT / 'scripts/verify_full_available.py').read_bytes())\n    verbosity_option = any(isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)\n        and node.func.attr == 'add_argument' and any(isinstance(arg, ast.Constant) and arg.value == '--verbosity' for arg in node.args)\n        for node in ast.walk(parser_tree))\n    if not verbosity_option:\n        raise ValueError('Root must add the reviewed optional --verbosity runner argument before attempt2 freeze')")
        text = exact_once(text, "    record = {'section': 290, 'root_declared': True,",
            "    record = {'section': 290, 'root_declared': True, 'actual_validation_attempt': 2,\n              'prior_attempt_freeze_relative': 'verification/full-290/source-freeze.json',\n              'prior_attempt_freeze_sha256': sha(ROOT / 'verification/full-290/source-freeze.json'),")
    if name == 'run_full290_orchestration.py':
        text = text.replace("'--timeout', '1200'", "'--timeout', '1800'")
        text = text.replace('timeout=1290', 'timeout=1890')
    if name == 'offline290_launcher.py':
        text = exact_once(text, "sys.argv = [str(ROOT / 'scripts/verify_full_available.py'), '--output', str(out)]",
            "sys.argv = [str(ROOT / 'scripts/verify_full_available.py'), '--output', str(out), '--verbosity', '2']")
        text = exact_once(text, "'actual_suite_exit': code, 'exception': error,", "'actual_suite_exit': code, 'exception': error, 'actual_validation_attempt': 2, 'runner_verbosity': 2,")
    if name == 'run_p3_supplementary_windows_290.py':
        text = text.replace("'--timeout', '1200'", "'--timeout', '1800'")
    if name == 'supplementary290_launcher.py':
        text = text.replace("sha(ROOT / 'verification/full-290/source-freeze.json')", "sha(ROOT / 'verification/full-290/source-freeze-repair.json')")
        text = exact_once(text, "'kind': 'FULL290_CANONICAL_P3_NATIVE_WINDOW_CLOSURE', 'mode': args.mode,", "'kind': 'FULL290_CANONICAL_P3_NATIVE_WINDOW_CLOSURE', 'actual_validation_attempt': 2, 'mode': args.mode,")
    if name == 'archive_full290_outputs.py':
        text = exact_once(text, "'actual_section': 290, 'root_freeze_sha256': sha(FREEZE),", "'actual_section': 290, 'actual_validation_attempt': 2, 'root_freeze_sha256': sha(FREEZE),")
    target = HERE / name
    if target.exists():
        raise ValueError('Never overwrite a prepared repair tool: ' + name)
    ast.parse(text)
    target.write_bytes(text.encode('utf8'))
    records[name] = {'original_controller': path.relative_to(ROOT).as_posix(),
                     'original_sha256': hashlib.sha256(original).hexdigest(),
                     'repair_controller_sha256': hashlib.sha256(target.read_bytes()).hexdigest()}
ledger = {'kind': 'FULL290_ATTEMPT2_PREPARATION_ONLY', 'tools': records,
          'prior_actual_attempt_freeze_sha256': hashlib.sha256(first_freeze.read_bytes()).hexdigest(),
          'prior_archives_unchanged': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in (
              'verification/full-290/execution-attempt1/archive-manifest.json',
              'verification/full-290/p3-supplementary-attempt1/archive-manifest.json')},
          'timeout_seconds': 1800, 'outer_controller_wait_seconds': 1890,
          'offline_verbosity': 2, 'GUI_or_full_or_freeze_executed': False,
          'production_or_original_attempt_modified': False}
with (HERE / 'controller-adaptation-290.json').open('xb') as file:
    file.write((json.dumps(ledger, ensure_ascii=False, indent=2) + '\n').encode('utf8'))
print(json.dumps({'prepared_controller_files': len(records), 'executed': False}))
