"""Source closure for already validated Phatm2 S2 manual count aliases."""
import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = Path('/workspace/rougezhushou')
PACKAGE = OUT / 'frozen'
HEAD = json.loads((OUT / 'freeze.json').read_text())['baseline_head']
sys.dont_write_bytecode = True
sys.path.insert(0, str(PACKAGE))
from rouge.catalog import catalog
from rouge.operator_options import OPTIONS

sources = {}
raw = {}
for name, expected in (
    ('character_table', '68e3a3b5ee0d407ce234afaa5867c6fda6379a6843c7d5317a7bbda4779f8697'),
    ('skill_table', '86f4aa64c785f39727edd06d6dd8a4f27f371c8e4ace5345ba0dc61dee1386ca')):
    path = ROOT / '.cache/p2-s1-binding' / (name + '.json')
    blob = path.read_bytes()
    sha = hashlib.sha256(blob).hexdigest()
    assert sha == expected
    sources[name] = {'path': str(path), 'sha256': sha, 'bytes': len(blob),
                     'actual_bytes_rehashed_now': True, 'new_download': False,
                     'source_commit': 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'}
    raw[name] = json.loads(blob)

operator = 'char_1042_phatm2'
profile = catalog()['operators'][operator]
skill_id = profile['skills'][1]['id']
assert raw['character_table'][operator]['skills'][1]['skillId'] == skill_id
raw_skill = raw['skill_table'][skill_id]
for rank in range(1, 11):
    values = {entry['key']: entry['value'] for entry in raw_skill['levels'][rank - 1]['blackboard']}
    assert values == profile['skills'][1]['levels'][rank - 1]['values']
control = next(entry for entry in OPTIONS[operator] if entry[0] == 'bait_triggers')
assert control == ('bait_triggers', '当前窗口诱饵触发次数', 0, 100, (2,))
selectors = {'character_table.char_1042_phatm2.skills[1]': raw['character_table'][operator]['skills'][1],
             'skill_table.' + skill_id + '.levels': raw_skill['levels']}
(OUT / 'pinned-bait-selectors.json').write_text(json.dumps(selectors, ensure_ascii=False, indent=2) + '\n')

reads = []
for rel in ('rouge/reporting.py', 'rouge/estimate.py', 'rouge/damage.py', 'rouge/operator_engine.py'):
    text = (PACKAGE / rel).read_text()
    for node in ast.walk(ast.parse(text)):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == 'get' and node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)
                and any(word in node.args[0].value for word in (
                    'count', 'hits', 'kills', 'ticks', 'casts', 'triggers', 'state',
                    'weight', 'stacks', 'entries', 'stones', 'bursts'))):
            reads.append({'file': rel, 'line': node.lineno, 'field': node.args[0].value,
                          'source': ast.get_source_segment(text, node)})

prior = 'research/p2-incoming-clock/source-receipt.json'
prior_bytes = subprocess.check_output(['git', '-C', str(ROOT), 'show', HEAD + ':' + prior])
(OUT / 'reused-incoming-clock-source-receipt.json').write_bytes(prior_bytes)
receipt = {'baseline_head': HEAD, 'source_files': sources,
           'validated_integer_input': {'operator': operator, 'skill': 2, 'control': control,
               'existing_validator': "Combat.option('bait_triggers',0,maximum=100,integer=True)",
               'existing_parsing': 'finite float followed by nonnegative integer/range validation',
               'manual_maximum_not_native_trigger_cap': True},
           'all_ten_skill_blackboards_match_pinned_original': True,
           'source_selectors': 'pinned-bait-selectors.json',
           'raw_count_reads_searched': sorted(reads, key=lambda row: (row['file'], row['line'])),
           'narrow_defect': 'S2 finisher ignores the validated numeric count, tests raw-string truthiness, then int(raw). String zero creates an unrequested pending bait source and masks damage; decimal aliases fail after successful integer validation.',
           'scope_exclusions': ['Deepcolor summon_count belongs to63', 'checkbox truthiness belongs to62/64',
               'Wisdel raw ghost count/casts belongs to separate readonly candidate66',
               'Closure prior casts has its own strict number-only validation, not a previously accepted numeric-string path',
               'legacy damage count reads use normalized integer copies; skill_rank strings are rejected before the int read'],
           'reused_existing_receipt': {'tracked_path': prior, 'snapshot_head': HEAD,
               'sha256': hashlib.sha256(prior_bytes).hexdigest(),
               'historical_original_download_not_claimed_as_current': True},
           'unknowns_preserved': ['deployment attack snapshot', 'first tick', 'refresh or overlap',
               'actual bait event clock', 'actual full cast/cycle attribution', 'native/current-hotfix attachment'],
           'no_new_numerical_game_model': True, 'no_new_event_schedule': True,
           'production_edits': 0, 'private_state_read': False, 'native_validation': False}
(OUT / 'source-closure.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'baseline_head': HEAD, 'raw_hashes_match': True,
                  'skill_ranks_checked': 10, 'raw_reads_searched': len(reads),
                  'scope': 'only existing validated Phatm2 S2 bait_triggers'}))
