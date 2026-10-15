"""Generate static checks for the new attempt only; no fixture execution."""
from pathlib import Path
import ast

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
text = (ROOT / '.cache/p3-full290-prep/check_preparation_290.py').read_text(encoding='utf8')
text = text.replace('.cache/p3-full290-prep', '.cache/p3-full290-repair-prep')
text = text.replace('verification/full-285/source-freeze.json', 'verification/full-290/source-freeze.json')
text = text.replace("'--timeout', '1200'", "'--timeout', '1800'")
text = text.replace('all_previous_419_selectors_retained', 'all_attempt1_430_selectors_retained')
text = text.replace('all_previous_1193_source_paths_retained', 'all_attempt1_1221_source_paths_retained')
text = text.replace("check(len(added) == 11 and all(any('_' + str(n) in name for n in range(286, 291)) for name in added), 'all_eleven_286_290_module_selectors_added')", "check(not added, 'repair_uses_exact_same_430_selector_list')\ncheck(snapshot['selectors'] == previous['selectors'], 'same_full_ordered_selector_union_no_scope_change')\ncheck(set(snapshot['source_sha256']) == set(previous['source_sha256']), 'same_1221_maintained_source_paths')")
text = text.replace('previous_full285_freeze_sha256', 'original_attempt1_freeze_sha256')
anchor = "record = {\n"
if text.count(anchor) != 1:
    raise ValueError('Expected one static record anchor')
extra = '''check('timeout=1890' in (HERE / 'run_full290_orchestration.py').read_text(encoding='utf8'), 'outer_wait_1890')
supervisor = (HERE / 'legacy/supervisor275.py').read_text(encoding='utf8')
check('0<args.timeout<=1800' in supervisor and '0<args.timeout<=1200' not in supervisor, 'new_owned_supervisor_allows1800')
check("'--timeout', '1800'" in (HERE / 'run_p3_supplementary_windows_290.py').read_text(encoding='utf8'), 'five_supplementary_timeouts1800')
check("'--verbosity', '2'" in (HERE / 'offline290_launcher.py').read_text(encoding='utf8'), 'offline_verbosity2_explicit')
check('source-freeze-repair.json' in str(FREEZE), 'repair_freeze_path_only')
check('execution-attempt2' in (HERE / 'archive_full290_outputs.py').read_text(encoding='utf8'), 'main_attempt2_archive_only')
check('p3-supplementary-attempt2' in (HERE / 'archive_p3_supplementary_290.py').read_text(encoding='utf8'), 'supplementary_attempt2_archive_only')
adaptation = json.loads((HERE / 'controller-adaptation-290.json').read_bytes())
check(sha(ROOT / 'verification/full-290/source-freeze.json') == adaptation['prior_actual_attempt_freeze_sha256'], 'original_attempt1_freeze_unchanged')
check(all(sha(ROOT / path) == expected for path, expected in adaptation['prior_archives_unchanged'].items()), 'both_original_attempt1_archives_unchanged')
'''
text = text.replace(anchor, extra + anchor)
text = text.replace("'kind': 'FULL290_STATIC_PREPARATION_NOT_FULL_VALIDATION'", "'kind': 'FULL290_ATTEMPT2_STATIC_PREPARATION_NOT_FULL_VALIDATION'")
ast.parse(text)
target = HERE / 'check_preparation_290.py'
with target.open('xb') as file:
    file.write(text.encode('utf8'))
print('Created fresh attempt2 static checker; not run yet.')
