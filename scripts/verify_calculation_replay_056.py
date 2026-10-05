"""Compare freshly computed 0.55/0.56 public calculations at exact leaf paths.

The historical 0.50 file supplies inputs only. It is never a numeric baseline.
Both calculators run in fresh subprocesses to avoid importing the other package.
Default policy rejects every changed numeric value. An exception requires an
exact case/path/before/after plus independently pinned mechanism evidence.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
import re
from pathlib import Path
import subprocess
import struct
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / '.cache/research/calculation-replay-056'
ORIGINAL_INPUTS = ROOT / '.cache/p1-050/before-default-results.json'
OLD_EPOCH = ROOT / '.cache/research/page-routing-056/epoch-1791136902879484600'
OLD_PACKAGE = OLD_EPOCH / 'baseline-source'
OLD_SEAL = OLD_EPOCH / 'baseline-seal-1791137793542949500.json'
RUNE_ORACLE_INPUTS = ROOT / '.cache/research/relic-panel-056/replay-fight25-oracle-inputs.json'
RUNE_ORACLE_INPUTS_SHA = 'f23f596b9fdfb5f968d6917523c0c75fff0fe71be5d7f1d1e7040303ed8e18bf'
FIGHT_ROWS = (700, 706, 712, 718, 724, 730)
SPEED_ROWS = (701, 707, 713, 719, 725, 731)

# These additions describe the origin/layer of a resolved effect. They do not
# authorize changing its value or any calculated metric. Every leaf is retained.
SOURCE_METADATA = {'source_buff_index', 'source_buff_key', 'attribute_layer',
                   'formula_item', 'native_count_scale', 'native_rune_base',
                   'native_rune_factor', 'stacking_evidence', 'secondary_source'}
METADATA_PATH = re.compile(r'^/(?:applied_effects|relic_resolution/(?:rules|token_effects))/\d+/([^/]+)$')
RECORD_METADATA_PATH = re.compile(r'^/relic_resolution/records/\d+/applied/\d+/([^/]+)$')
DISPLAY_LIST_PATH = re.compile(
    r'^/(?:warnings|assumptions|estimate/notes|timing/notes|report/sections/\d+/notes'
    r'|relic_resolution/warnings|run_resolution/(?:notes|pending))(/\d+)?$')
LABEL_PATH = re.compile(r'^/report/sections/\d+/metrics/\d+/(?:label|unit)$')
MISSING = object()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, allow_nan=False,
                                   separators=(',', ':'))+'\n', encoding='utf-8')


def public_path(path):
    path = Path(path).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError('Artifact/source path must remain inside this workspace')
    relative = path.relative_to(ROOT).as_posix()
    if '.local' in Path(relative).parts:
        raise ValueError('Private runtime is outside this verifier scope')
    return relative


def sources(package):
    package = Path(package).resolve()
    public_path(package)
    paths = list((package/'rouge').glob('*.py')) + list((package/'rouge/data').rglob('*.json'))
    return {p.relative_to(package).as_posix(): sha(p) for p in sorted(paths)}


def verify_old_seal():
    seal = read(OLD_SEAL)
    if seal.get('passed') is not True or seal.get('frozen_reader_version') != '0.55':
        raise ValueError('Unsealed 0.55 source baseline')
    old = sources(OLD_PACKAGE)
    expected = seal['original_source_sha256']
    if old != expected:
        raise ValueError('Frozen 0.55 Python/JSON package differs from its seal')
    return old


def worker(package, inputs, output, receipt):
    package, inputs, output, receipt = map(Path, (package, inputs, output, receipt))
    for path in (package, inputs, output, receipt):
        public_path(path)
    before = sources(package)
    sys.path.insert(0, str(package.resolve()))
    from rouge.damage import calculate_damage
    import rouge.damage
    if not Path(rouge.damage.__file__).resolve().is_relative_to(package.resolve()):
        raise AssertionError('Wrong calculator package imported')
    start = time.perf_counter()
    rows, errors = [], []
    for index, scenario in enumerate(read(inputs)):
        entry = {'index': index, 'scenario': deepcopy(scenario)}
        try:
            entry['result'] = calculate_damage(deepcopy(scenario))
        except Exception as error:
            entry['error'] = {'type': type(error).__name__, 'message': str(error)}
            errors.append(index)
        rows.append(entry)
    write(output, rows)
    after = sources(package)
    record = {'passed': not errors and before == after, 'cases': len(rows), 'errors': errors,
              'package': public_path(package), 'imported_damage': public_path(rouge.damage.__file__),
              'input_sha256': sha(inputs), 'output_sha256': sha(output),
              'source_sha256': before, 'source_stable_during_calculation': before == after,
              'elapsed_seconds': time.perf_counter()-start,
              'private_runtime_read_or_written': False, 'game_actions': 0, 'chat_requests': 0}
    write(receipt, record)
    return 0 if record['passed'] else 1


def oracle_worker(inputs, output, receipt):
    """Recompute six rows through unchanged 0.55 skills/timing/enemy models.

    The injected basis comes from the independently pinned raw-table oracle,
    never the 0.56 result. Only two old owner battle effects are removed. Token
    effects and enemy branches remain; token HP alone passes the proven writer.
    All monkeypatches live in this isolated process, with no package-file edits.
    """
    inputs, output, receipt = map(Path, (inputs, output, receipt))
    for path in (inputs, output, receipt):
        public_path(path)
    before = verify_old_seal()
    if sha(RUNE_ORACLE_INPUTS) != RUNE_ORACLE_INPUTS_SHA:
        raise ValueError('Independent raw oracle input differs from pinned evidence')
    cases = read(RUNE_ORACLE_INPUTS)
    if tuple(row['row_index'] for row in cases) != FIGHT_ROWS:
        raise ValueError('Independent oracle case scope changed')
    all_inputs = read(inputs)
    sys.path.insert(0, str(OLD_PACKAGE.resolve()))
    import rouge.catalog as old_catalog
    import rouge.damage as old_damage
    import rouge.relics as old_relics
    import rouge.summons as old_summons
    if not Path(old_damage.__file__).resolve().is_relative_to(OLD_PACKAGE.resolve()):
        raise AssertionError('Oracle must use frozen 0.55 package')
    original_attributes = old_catalog.operator_attributes
    original_prepare = old_relics.prepare
    original_token_attributes = old_summons.token_attributes
    active = None
    injections, removals, token_writes = [], [], []

    def writer(value):
        return round(struct.unpack('<f', struct.pack('<f', value))[0])

    def attributes(operator, *args, **kwargs):
        stats = deepcopy(original_attributes(operator, *args, **kwargs))
        if operator != active['scenario']['operator']:
            raise AssertionError('Owner-only oracle received a different operator')
        raw, rune = active['cultivated'], active['rune_integer']
        for key, source in (('hp', 'maxHp'), ('attack', 'atk'), ('defense', 'def')):
            if stats[key] != raw[source]:
                raise AssertionError('Frozen cultivation disagrees with independent raw table')
        for key, source in (('hp', 'maxHp'), ('attack', 'atk')):
            expected = writer(raw[source] * 1.3)
            if rune[source] != expected:
                raise AssertionError('Raw input and independent float32 writer disagree')
            stats[key] = expected
        injections.append({'row_index': active['row_index'], 'operator': operator,
                           'cultivated': raw, 'injected_hp': stats['hp'],
                           'injected_attack': stats['attack']})
        return stats

    def prepare_owner(scenario, profile):
        prepared, resolution = original_prepare(scenario, profile)
        removed = [e for e in prepared['effects'] if
                   e.get('relic_id') == 'rogue_6_relic_fight_25'
                   and e['kind'] in ('hp_pct', 'attack_pct')]
        if sorted((e['kind'], e['value']) for e in removed) != [('attack_pct', .3), ('hp_pct', .3)]:
            raise AssertionError('Old owner effect removal does not match the two raw multipliers')
        prepared['effects'] = [e for e in prepared['effects'] if e not in removed]
        removals.append({'row_index': active['row_index'], 'removed': deepcopy(removed),
                         'enemy_spawn_branch': deepcopy(resolution.get('enemy_effects', {})),
                         'retained_token_effects': deepcopy(resolution['token_effects'])})
        return prepared, resolution

    def token_attributes(profile, scenario, token_id, hp_pct=0):
        stats = deepcopy(original_token_attributes(profile, scenario, token_id, hp_pct))
        if hp_pct:
            if hp_pct != .3 or scenario.get('module_id'):
                raise AssertionError('Token oracle is limited to the proven unmixed fight25 multiplier')
            raw = original_token_attributes(profile, scenario, token_id, 0)
            if stats['hp'] != raw['hp'] * 1.3:
                raise AssertionError('Old token HP includes an unrecognized source')
            stats['hp'] = writer(raw['hp'] * 1.3)
            # Selected tokens have exact integral ATK after this multiplier.
            # No token skill uses ATK in these six owner-only input cases.
            if raw['attack'] * 1.3 != writer(raw['attack'] * 1.3):
                raise AssertionError('Token ATK would require a separate pre-skill injection')
            token_writes.append({'row_index': active['row_index'], 'token_id': token_id,
                                 'raw_hp': raw['hp'], 'rune_hp': stats['hp'],
                                 'raw_attack': raw['attack'],
                                 'rune_attack': writer(raw['attack'] * 1.3)})
        return stats

    old_catalog.operator_attributes = attributes
    old_relics.prepare = prepare_owner
    old_summons.token_attributes = token_attributes
    start, rows = time.perf_counter(), []
    for active in cases:
        index, scenario = active['row_index'], active['scenario']
        if scenario != all_inputs[index]:
            raise AssertionError('Oracle row differs from original public scenario')
        rows.append({'index': index, 'scenario': deepcopy(scenario),
                     'result': old_damage.calculate_damage(deepcopy(scenario))})
    write(output, rows)
    after = verify_old_seal()
    record = {'passed': before == after, 'cases': len(rows),
              'method': 'Pinned raw basis + native float32 integer writer, then frozen 0.55 skill/timing/enemy models.',
              'old_source_sha256': before, 'imported_damage': public_path(old_damage.__file__),
              'source_stable_during_calculation': before == after,
              'oracle_inputs': public_path(RUNE_ORACLE_INPUTS),
              'oracle_input_sha256': sha(RUNE_ORACLE_INPUTS),
              'public_input_sha256': sha(inputs), 'output_sha256': sha(output),
              'injections': injections, 'owner_effect_removals': removals,
              'token_integer_writes': token_writes, 'elapsed_seconds': time.perf_counter()-start,
              'current_056_calculator_imported': False, 'private_runtime_read_or_written': False,
              'game_actions': 0, 'chat_requests': 0}
    write(receipt, record)
    return 0 if record['passed'] else 1


def run_worker(package, inputs, output, receipt, log):
    command = [sys.executable, str(Path(__file__).resolve()), '_worker',
               '--package', str(package), '--inputs', str(inputs), '--output', str(output),
               '--receipt', str(receipt)]
    with Path(log).open('w', encoding='utf-8') as stream:
        process = subprocess.run(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT,
                                 text=True, check=False)
    if process.returncode:
        raise RuntimeError('Calculator subprocess failed; its original output and log are retained')


def prepare():
    RESEARCH.mkdir(parents=True, exist_ok=True)
    old_sources = verify_old_seal()
    original = read(ORIGINAL_INPUTS)
    if len(original) != 732:
        raise AssertionError('Expected the 732 existing public input cases')
    epoch = RESEARCH / ('epoch-'+str(time.time_ns()))
    epoch.mkdir()
    # Deliberately discard old result values before any calculation/import.
    scenarios = [deepcopy(row['scenario']) for row in original]
    write(epoch/'inputs.json', scenarios)
    run_worker(OLD_PACKAGE, epoch/'inputs.json', epoch/'before-055-results.json',
               epoch/'before-055-worker.json', epoch/'before-055-worker.log')
    receipt = {'stage': 'baseline_prepared', 'passed': True, 'cases': len(scenarios),
               'historical_file_used_for_inputs_only': public_path(ORIGINAL_INPUTS),
               'historical_input_file_sha256': sha(ORIGINAL_INPUTS),
               'input_sha256': sha(epoch/'inputs.json'),
               'old_calculator_seal': public_path(OLD_SEAL), 'old_calculator_seal_sha256': sha(OLD_SEAL),
               'old_source_sha256': old_sources,
               'before_output_sha256': sha(epoch/'before-055-results.json'),
               'before_worker_sha256': sha(epoch/'before-055-worker.json'),
               'private_runtime_read_or_written': False, 'game_actions': 0, 'chat_requests': 0}
    write(epoch/'baseline-preparation.json', receipt)
    print(json.dumps({'passed': True, 'stage': 'baseline_prepared', 'epoch': public_path(epoch),
                      'cases': len(scenarios)}, ensure_ascii=False))
    return 0


def escaped(key):
    return str(key).replace('~', '~0').replace('/', '~1')


def delta(before, after, path=''):
    if isinstance(before, dict) and isinstance(after, dict):
        for key in sorted(set(before)|set(after)):
            yield from delta(before.get(key, MISSING), after.get(key, MISSING), path+'/'+escaped(key))
    elif isinstance(before, list) and isinstance(after, list):
        for index in range(max(len(before), len(after))):
            yield from delta(before[index] if index < len(before) else MISSING,
                             after[index] if index < len(after) else MISSING, path+'/'+str(index))
    elif before is MISSING or after is MISSING:
        yield {'path': path, 'operation': 'add' if before is MISSING else 'remove',
               **({} if before is MISSING else {'before': before}),
               **({} if after is MISSING else {'after': after})}
    elif before != after or type(before) != type(after):
        yield {'path': path, 'operation': 'replace', 'before': before, 'after': after,
               'before_type': type(before).__name__, 'after_type': type(after).__name__}


def numeric(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def textual(value):
    return isinstance(value, str) or (isinstance(value, list) and all(isinstance(v, str) for v in value))


def classify(change, index, allowances):
    path = change['path']
    before, after = change.get('before', MISSING), change.get('after', MISSING)
    metadata = METADATA_PATH.fullmatch(path) or RECORD_METADATA_PATH.fullmatch(path)
    if (metadata and metadata.group(1) in SOURCE_METADATA and change['operation'] == 'add'):
        return 'source_metadata_addition'
    if DISPLAY_LIST_PATH.fullmatch(path) and all(v is MISSING or textual(v) for v in (before, after)):
        return 'display_text_change'
    if LABEL_PATH.fullmatch(path) and isinstance(before, str) and isinstance(after, str):
        return 'display_label_change'
    if numeric(before) and numeric(after) and before == after:
        return 'numeric_type_schema_only'
    allowance = allowances.get((index, path))
    def exact(side, value):
        return ((side not in allowance and value is MISSING) or
                (side in allowance and value is not MISSING and
                 type(value) is type(allowance[side]) and value == allowance[side]))
    if (allowance and change['operation'] == allowance.get('operation', 'replace')
            and exact('before', before) and exact('after', after)):
        change['evidence'] = allowance['evidence']
        change['verified_mechanism'] = allowance['mechanism']
        return 'exact_evidence_bound_change'
    return 'unexpected_numeric_change' if numeric(before) or numeric(after) else 'unexpected_structural_change'


def load_allowances(path):
    if path is None:
        return {}
    public_path(path)
    result = {}
    for entry in read(path):
        key = (entry['row_index'], entry['path'])
        if key in result or not isinstance(key[0], int) or not 0 <= key[0] < 732:
            raise ValueError('Duplicate or out-of-scope case allowance')
        if entry['mechanism'] not in ('attribute_rune', 'redeploy', 'grudge'):
            raise ValueError('Unsupported mechanism allowance')
        operation = entry.get('operation', 'replace')
        if (operation not in ('add', 'remove', 'replace') or
                ('before' in entry) != (operation != 'add') or
                ('after' in entry) != (operation != 'remove')):
            raise ValueError('An allowance must match an exact addition, removal or replacement')
        if not entry.get('evidence'):
            raise ValueError('A changed numerical path needs fixed source evidence')
        for evidence in entry['evidence']:
            source = ROOT/evidence['path']
            public_path(source)
            if sha(source) != evidence['sha256']:
                raise ValueError('Mechanism evidence hash mismatch')
        result[key] = entry
    return result


def frozen_sources(freeze):
    """Verify the whole formal seal, including non-calculator binary assets."""
    public_path(freeze)
    record = read(freeze)
    expected = record.get('source_sha256', record.get('source_hashes'))
    if not isinstance(expected, dict):
        raise ValueError('Formal comparison needs a full source freeze dictionary')
    current = {}
    for name in expected:
        path = ROOT/name
        if public_path(path) != name:
            raise ValueError('Frozen path must be canonical and inside workspace')
        current[name] = sha(path)
    if current != expected:
        raise ValueError('Current formal source assets differ from supplied freeze')
    return current


def compare(epoch, freeze, allowances_file=None, retained_after=None):
    epoch = Path(epoch).resolve()
    if not epoch.is_relative_to(RESEARCH):
        raise ValueError('Use a prepared calculation replay epoch')
    prepared = read(epoch/'baseline-preparation.json')
    verify_old_seal()
    for filename, key in [('inputs.json', 'input_sha256'), ('before-055-results.json', 'before_output_sha256'),
                          ('before-055-worker.json', 'before_worker_sha256')]:
        if sha(epoch/filename) != prepared[key]:
            raise ValueError('Prepared 0.55 baseline was modified')
    public_path(freeze)
    frozen = read(freeze)
    source_map = frozen.get('source_sha256', frozen.get('source_hashes'))
    if not isinstance(source_map, dict):
        raise ValueError('Formal comparison needs the current source freeze dictionary')
    full_frozen = frozen_sources(freeze)
    current = sources(ROOT)
    if any(source_map.get(name) != value for name, value in current.items()):
        raise ValueError('Current Python/JSON source is not fully frozen by supplied receipt')
    allowances = load_allowances(allowances_file)
    stage = epoch/('compare-'+str(time.time_ns()))
    stage.mkdir()
    if retained_after is None:
        run_worker(ROOT, epoch/'inputs.json', stage/'after-056-results.json',
                   stage/'after-056-worker.json', stage/'after-056-worker.log')
        after_file = stage/'after-056-results.json'
    else:
        retained_after = Path(retained_after).resolve()
        if not retained_after.is_relative_to(epoch):
            raise ValueError('Retained original output must belong to this epoch')
        retained = read(retained_after/'receipt.json')
        after_file = retained_after/'after-056-results.json'
        original_worker = read(retained_after/'after-056-worker.json')
        if (sha(after_file) != retained['after_output_sha256'] or
                sha(after_file) != original_worker['output_sha256'] or
                original_worker['input_sha256'] != prepared['input_sha256'] or
                original_worker['source_sha256'] != current or
                original_worker['passed'] is not True or
                retained['freeze_receipt_sha256'] != sha(freeze)):
            raise ValueError('Retained current output no longer binds the same inputs and frozen source')
    before, after = read(epoch/'before-055-results.json'), read(after_file)
    if len(before) != 732 or len(after) != 732:
        raise AssertionError('All 732 cases must be present in both original result files')
    changes, unexpected, matched_allowances = [], [], set()
    categories = Counter()
    for index, (old, new) in enumerate(zip(before, after)):
        if old['index'] != index or new['index'] != index or old['scenario'] != new['scenario']:
            raise AssertionError('Calculator inputs or row order changed')
        differences = list(delta(old['result'], new['result']))
        if not differences:
            continue
        for difference in differences:
            kind = classify(difference, index, allowances)
            difference['category'] = kind
            categories[kind] += 1
            if kind == 'exact_evidence_bound_change':
                matched_allowances.add((index, difference['path']))
            if kind.startswith('unexpected_'):
                unexpected.append({'row_index': index, 'scenario': old['scenario'], **difference})
        changes.append({'row_index': index, 'scenario': old['scenario'], 'differences': differences})
    unused = sorted(set(allowances)-matched_allowances)
    stable = current == sources(ROOT) and full_frozen == frozen_sources(freeze)
    receipt = {'version': '0.56.0', 'passed': not unexpected and not unused and stable,
               'comparison': 'Fresh frozen 0.55 calculator versus frozen current 0.56 calculator; full structured outputs.',
               'cases': len(before), 'exact_structured_unchanged': len(before)-len(changes),
               'changed_cases': len(changes), 'difference_categories': dict(categories),
               'unexpected_changes': unexpected, 'unused_exact_allowances': unused,
               'historical_050_results_used_as_numeric_baseline': False,
               'freeze_receipt': public_path(freeze), 'freeze_receipt_sha256': sha(freeze),
               'before_output': public_path(epoch/'before-055-results.json'),
               'before_output_sha256': sha(epoch/'before-055-results.json'),
               'after_output': public_path(after_file),
               'after_output_sha256': sha(after_file),
               'complete_difference_file': public_path(stage/'differences.json'),
               'source_sha256': current, 'source_stable_during_comparison': stable,
               'full_formal_source_sha256': full_frozen,
               'full_formal_source_count': len(full_frozen),
               'default_numeric_value_exception_count': 0,
               'exact_evidence_bound_allowances': len(allowances),
               'exact_numeric_value_allowances': sum(
                   e.get('operation', 'replace') == 'replace' and
                   numeric(e.get('before')) and numeric(e.get('after')) and
                   e['before'] != e['after'] for e in allowances.values()),
               'retained_after_stage': public_path(retained_after) if retained_after else None,
               'verifier_sha256': sha(Path(__file__)),
               'private_runtime_read_or_written': False, 'game_actions': 0, 'chat_requests': 0}
    write(stage/'differences.json', changes)
    receipt['complete_difference_sha256'] = sha(stage/'differences.json')
    write(stage/'receipt.json', receipt)
    print(json.dumps({'passed': receipt['passed'], 'cases': receipt['cases'],
                      'unchanged': receipt['exact_structured_unchanged'], 'changed': len(changes),
                      'categories': dict(categories), 'unexpected_changes': len(unexpected),
                      'receipt': public_path(stage/'receipt.json')}, ensure_ascii=False))
    return 0 if receipt['passed'] else 1


def leaf(result, path):
    for part in path.lstrip('/').split('/'):
        part = part.replace('~1', '/').replace('~0', '~')
        result = result[int(part)] if isinstance(result, list) else result[part]
    return result


def oracle(epoch, retained_after):
    """Create exact allow-list only after independent 0.55 oracle equality."""
    epoch, retained_after = Path(epoch).resolve(), Path(retained_after).resolve()
    if not epoch.is_relative_to(RESEARCH) or not retained_after.is_relative_to(epoch):
        raise ValueError('Oracle artifacts must stay in their public replay epoch')
    retained = read(retained_after/'receipt.json')
    current_output = ROOT/retained['after_output']
    if sha(current_output) != retained['after_output_sha256']:
        raise ValueError('Original failed output changed')
    stage = epoch/('independent-oracle-'+str(time.time_ns()))
    stage.mkdir()
    command = [sys.executable, str(Path(__file__).resolve()), '_oracle_worker',
               '--inputs', str(epoch/'inputs.json'), '--output', str(stage/'results.json'),
               '--receipt', str(stage/'worker.json')]
    with (stage/'worker.log').open('w', encoding='utf-8') as stream:
        process = subprocess.run(command, cwd=ROOT, stdout=stream,
                                 stderr=subprocess.STDOUT, text=True, check=False)
    if process.returncode:
        raise RuntimeError('Independent oracle failed; log and partial originals preserved')
    independently_computed = {row['index']: row for row in read(stage/'results.json')}
    after = read(current_output)
    before = read(epoch/'before-055-results.json')
    shared_numeric_checked, oracle_failures = 0, []
    for index, row in independently_computed.items():
        def common_numeric(old, new, path=''):
            if isinstance(old, dict) and isinstance(new, dict):
                for key in sorted(set(old) & set(new)):
                    yield from common_numeric(old[key], new[key], path+'/'+escaped(key))
            elif isinstance(old, list) and isinstance(new, list):
                for key, (a, b) in enumerate(zip(old, new)):
                    yield from common_numeric(a, b, path+'/'+str(key))
            elif numeric(old) and numeric(new):
                yield path, old, new
        for path, expected, actual in common_numeric(row['result'], after[index]['result']):
            shared_numeric_checked += 1
            if expected != actual:
                oracle_failures.append({'row_index': index, 'path': path,
                                        'expected': expected, 'actual': actual})
    evidence_files = [RUNE_ORACLE_INPUTS,
                      ROOT/'.cache/research/relic-panel-056/native-evidence.json',
                      ROOT/'.cache/research/relic-panel-056/audit-1791139604548055300.json',
                      ROOT/'.cache/research/relic-panel-056/freeze.json',
                      stage/'results.json', stage/'worker.json']
    evidence = [{'path': public_path(p), 'sha256': sha(p)} for p in evidence_files]
    audit = read(evidence_files[2])
    native_seal = read(evidence_files[3])
    if (sha(evidence_files[1]) != native_seal['native_evidence_sha256'] or
            native_seal['latest_audit_receipt'] != evidence_files[2].name):
        raise AssertionError('Native/raw mechanism evidence differs from its independent seal')
    if audit['passed'] is not True or audit['rune_source_entries'] != 120:
        raise AssertionError('Unverified source-layer evidence')
    expected_sources = [('rogue_6_relic_fight_25', 1, 'char_attribute_mul', 'hp_pct', .3),
                        ('rogue_6_relic_fight_25', 2, 'char_attribute_mul', 'attack_pct', .3),
                        ('rogue_6_from_relic_9', 0, 'char_attribute_add', 'attack_speed', 50.)]
    for rid, source_index, source_key, kind, value in expected_sources:
        matching = [r for r in audit['rune_source_matrix'] if r['id'] == rid and
                    r['source_index'] == source_index and r['source_key'] == source_key and
                    r['kind'] == kind and r['raw_value'] == value]
        if len(matching) != 1:
            raise AssertionError('Exact source-index/value evidence missing')
    allowances = []
    for change in retained['unexpected_changes']:
        index, path, operation = change['row_index'], change['path'], change['operation']
        entry = {'row_index': index, 'path': path, 'operation': operation,
                 'mechanism': 'attribute_rune', 'evidence': evidence}
        if operation == 'replace' and numeric(change.get('before')) and numeric(change.get('after')):
            if index not in independently_computed:
                raise AssertionError('Changed numerical path has no independent row oracle')
            expected = leaf(independently_computed[index]['result'], path)
            if expected != change['after']:
                oracle_failures.append({'row_index': index, 'path': path,
                                        'expected': expected, 'actual': change['after']})
            # int/float representation is a separately recorded schema change.
            # Preserve the oracle value; casting only matches the output type
            # after exact numeric equality, never hides a numerical difference.
            represented = type(change['after'])(expected)
            if represented != expected:
                raise AssertionError('Numeric schema conversion would lose the oracle value')
            entry.update(before=change['before'], after=represented,
                         independent_oracle_value=expected,
                         independent_oracle_type=type(expected).__name__)
        elif operation == 'remove' and path.startswith('/applied_effects/'):
            removed = change['before']
            if ((index in FIGHT_ROWS and path in ('/applied_effects/0', '/applied_effects/1')
                 and (removed['kind'], removed['value'], removed['relic_id']) in
                 (('hp_pct', .3, 'rogue_6_relic_fight_25'),
                  ('attack_pct', .3, 'rogue_6_relic_fight_25'))) or
                (index in SPEED_ROWS and path == '/applied_effects/0' and
                 (removed['kind'], removed['value'], removed['relic_id']) ==
                 ('attack_speed', 50., 'rogue_6_from_relic_9'))):
                kept = [e for r in after[index]['result']['relic_resolution']['records']
                        for e in r['applied'] if all(e.get(k) == v for k, v in removed.items())]
                if len(kept) != 1 or kept[0].get('attribute_layer') != 'relic_rune':
                    raise AssertionError('Removed battle effect source not preserved uniquely as rune')
                source = next(item for item in expected_sources if item[0] == removed['relic_id']
                              and item[3] == removed['kind'])
                if (kept[0].get('source_buff_index') != source[1] or
                        kept[0].get('source_buff_key') != source[2] or
                        kept[0].get('formula_item') !=
                        ('ADDITION' if removed['kind'] == 'attack_speed' else 'MULTIPLIER')):
                    raise AssertionError('Retained rune metadata does not match its exact raw source')
                entry['before'] = removed
                entry['retained_source'] = kept[0]
            else:
                raise AssertionError('Structural removal is outside precise source scope')
        elif (operation == 'add' and index in FIGHT_ROWS and path in (
              '/relic_resolution/enemy_effects/spawn_hp_rules/0/source_buff_index',
              '/relic_resolution/enemy_effects/spawn_hp_rules/0/source_buff_key')):
            expected = 0 if path.endswith('/source_buff_index') else 'global_buff_normal'
            old_rule = before[index]['result']['relic_resolution']['enemy_effects']['spawn_hp_rules'][0]
            new_rule = after[index]['result']['relic_resolution']['enemy_effects']['spawn_hp_rules'][0]
            if ({k:v for k,v in new_rule.items() if k not in ('source_buff_index', 'source_buff_key')}
                    != old_rule or change['after'] != expected):
                raise AssertionError('Enemy branch changed beyond two source metadata fields')
            entry['after'] = expected
        else:
            raise AssertionError('Unexplained difference cannot become an oracle allowance')
        allowances.append(entry)
    record = {'passed': not oracle_failures, 'independent_cases': 6,
              'shared_numeric_leaf_paths_verified': shared_numeric_checked,
              'oracle_failures': oracle_failures, 'exact_allowance_count': len(allowances),
              'numeric_value_allowances': sum(e['operation'] == 'replace' for e in allowances),
              'structure_removals': sum(e['operation'] == 'remove' for e in allowances),
              'source_metadata_additions': sum(e['operation'] == 'add' for e in allowances),
              'original_failed_receipt': public_path(retained_after/'receipt.json'),
              'original_failed_receipt_sha256': sha(retained_after/'receipt.json'),
              'oracle_output': public_path(stage/'results.json'),
              'oracle_output_sha256': sha(stage/'results.json'),
              'oracle_worker': public_path(stage/'worker.json'),
              'oracle_worker_sha256': sha(stage/'worker.json'),
              'allowance_file': public_path(stage/'exact-allowances.json'),
              'private_runtime_read_or_written': False, 'game_actions': 0, 'chat_requests': 0}
    if record['passed']:
        write(stage/'exact-allowances.json', allowances)
        record['allowance_sha256'] = sha(stage/'exact-allowances.json')
    write(stage/'receipt.json', record)
    print(json.dumps({'passed': record['passed'], 'oracle_failures': len(oracle_failures),
                      'numeric_paths': shared_numeric_checked, 'exact_allowances': len(allowances),
                      'receipt': public_path(stage/'receipt.json')}, ensure_ascii=False))
    return 0 if record['passed'] else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('prepare', 'compare', 'oracle', '_worker', '_oracle_worker'))
    parser.add_argument('--epoch', type=Path)
    parser.add_argument('--freeze', type=Path)
    parser.add_argument('--allowances', type=Path)
    parser.add_argument('--retained-after', type=Path)
    parser.add_argument('--package', type=Path)
    parser.add_argument('--inputs', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--receipt', type=Path)
    args = parser.parse_args()
    if args.mode == 'prepare':
        return prepare()
    if args.mode == 'compare':
        if args.epoch is None or args.freeze is None:
            parser.error('compare requires --epoch and --freeze')
        return compare(args.epoch, args.freeze, args.allowances, args.retained_after)
    if args.mode == 'oracle':
        if args.epoch is None or args.retained_after is None:
            parser.error('oracle requires --epoch and --retained-after')
        return oracle(args.epoch, args.retained_after)
    if args.mode == '_oracle_worker':
        if None in (args.inputs, args.output, args.receipt):
            parser.error('_oracle_worker requires inputs/output/receipt')
        return oracle_worker(args.inputs, args.output, args.receipt)
    if None in (args.package, args.inputs, args.output, args.receipt):
        parser.error('_worker requires package/inputs/output/receipt')
    return worker(args.package, args.inputs, args.output, args.receipt)


if __name__ == '__main__':
    raise SystemExit(main())
