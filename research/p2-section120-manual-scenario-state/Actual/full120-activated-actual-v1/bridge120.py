"""Comparison-only bridge. Root must supply measured, hash-bound admission data."""
import copy
import hashlib
import json
import math
import os
import re
from pathlib import Path, PurePosixPath

INDICES = (18, 19, 20, 21, 38, 39, 40, 41, 44, 45)
METRICS = ('window_seconds', 'window_dps', 'window_hps')
PROOF_NAMES = frozenset(('original_primary', 'candidate_primary', 'original_receipt',
                         'candidate_receipt', 'original_guard', 'candidate_guard', 'pair_audit'))
RESERVED_ROOT_OUTPUTS = frozenset(('window.py', 'bridge120.py', 'launcher120.py',
    'expected-map120.json', 'supervisor120.py', 'root_source_activation.json',
    'source_manifest.json', 'full120-bridge-closure.json', 'full120-113-bridge-ledger.json'))
WINDOWS_RESERVED_STEMS = frozenset(('con', 'prn', 'aux', 'nul',
    *(f'com{number}' for number in range(1, 10)), *(f'lpt{number}' for number in range(1, 10))))


def encoded(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False,
                      separators=(',', ':')).encode('utf-8')


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def scalar(present, value):
    require(type(present) is bool, 'Metric presence must be bool')
    if not present:
        return {'present': False, 'python_type': None, 'value': None, 'float_hex': None}
    require(value is None or type(value) in (float, int), 'Unexpected metric scalar type')
    if type(value) is float:
        require(math.isfinite(value), 'Nonfinite metric')
    return {'present': True, 'python_type': type(value).__name__, 'value': value,
            'float_hex': value.hex() if type(value) is float else None}


def contract_leaf(leaf, candidate):
    if candidate:
        return scalar(leaf['actual_candidate_present'], leaf['actual_candidate_value'])
    return scalar(leaf['old_present'], leaf['old_source_value'])


def validate_leaf(leaf):
    old, new = contract_leaf(leaf, False), contract_leaf(leaf, True)
    for prefix, actual in (('old', old), ('actual_candidate', new)):
        type_key = 'old_python_type' if prefix == 'old' else 'actual_candidate_python_type'
        hex_key = 'old_float_hex' if prefix == 'old' else 'actual_candidate_float_hex'
        require(leaf[type_key] == actual['python_type'], 'Metric type declaration mismatch')
        require(leaf[hex_key] == actual['float_hex'], 'Metric floatbits declaration mismatch')
    require(old['present'] is new['present'], 'Metric key insertion/removal prohibited')
    require(old['python_type'] == new['python_type'], 'Metric domain/type change prohibited')
    require(type(leaf['actual_changed']) is bool, 'Unmeasured changed marker')
    require(leaf['actual_changed'] is (encoded(old) != encoded(new)), 'Incorrect changed marker')
    return old, new


def proof_parts(pin):
    require(type(pin) is dict and set(pin) == {'path', 'bytes', 'sha256'}, 'Invalid artifact pin')
    text = pin['path']
    require(type(text) is str and '\\' not in text and ':' not in text,
            'Canonical portable forward-slash proof path required')
    relative = PurePosixPath(text)
    parts = relative.parts
    require(not relative.is_absolute() and len(parts) >= 2 and parts[0] == 'proofs'
            and '/'.join(parts) == text, 'Proof artifacts must be canonical leaves under proofs/')
    require(parts[0].casefold() not in RESERVED_ROOT_OUTPUTS, 'Reserved activation output namespace')
    for part in parts:
        require(re.fullmatch(r'[a-z0-9][a-z0-9._-]*', part) is not None and not part.endswith('.'),
                'Portable lowercase proof path component required')
        require(part.split('.', 1)[0] not in WINDOWS_RESERVED_STEMS, 'Windows reserved proof component')
    require(type(pin['bytes']) is int and pin['bytes'] >= 0, 'Actual proof byte length required')
    require(type(pin['sha256']) is str and re.fullmatch(r'[0-9a-f]{64}', pin['sha256']) is not None,
            'Actual proof SHA256 required')
    return parts


def validate_proof_paths(proofs):
    require(type(proofs) is dict and set(proofs) == PROOF_NAMES, 'Exact seven actual proof pins required')
    paths = [proof_parts(pin) for pin in proofs.values()]
    folded = [tuple(part.casefold() for part in parts) for parts in paths]
    require(len(set(folded)) == 7, 'Duplicate/case-aliased proof destinations prohibited')
    for index, first in enumerate(folded):
        for second in folded[index + 1:]:
            require(first[:len(second)] != second and second[:len(first)] != first,
                    'Proof file/directory prefix collision prohibited')
    return proofs


def pin_file(base, pin):
    parts = proof_parts(pin)
    base = Path(base)
    require(not base.is_symlink(), 'Proof base symlink prohibited')
    path = base
    for part in parts:
        path = path / part
        require(not path.is_symlink(), 'Proof symlink component prohibited')
    require(path.is_file() and path.resolve().is_relative_to(base.resolve()),
            'Escaped/nonregular artifact pin')
    raw = path.read_bytes()
    require(len(raw) == pin['bytes'] and hashlib.sha256(raw).hexdigest() == pin['sha256'],
            'Actual artifact pin mismatch: ' + pin['path'])
    return raw


class Bridge:
    def __init__(self, map_path, expected_sha256, out):
        path = Path(map_path)
        raw = path.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == expected_sha256, 'Admission map hash mismatch')
        self.mapping = json.loads(raw)
        require(self.mapping['kind'] == 'ROOT_ACTUAL_113_NARROW_WINDOW_METRIC_ADMISSION',
                'Inactive/non-Root admission map')
        require(self.mapping['ready'] is True, 'Unqualified future map')
        self.map_sha256 = expected_sha256
        self.out = Path(out)
        self.ledger = []
        self.consumed = set()
        rows = self.mapping['rows']
        require(tuple(row['literal_index'] for row in rows) == INDICES, 'Exact ten-row allowlist required')
        self.rows = {row['full_source_row_sha256_json_ordered']: row for row in rows}
        require(len(self.rows) == 10, 'Duplicate row identity')
        proofs = validate_proof_paths(self.mapping['proof_files'])  # Validate all destinations before IO/output.
        self.proof_sha256 = proofs['pair_audit']['sha256']
        actual_files = {name: pin_file(path.parent, pin) for name, pin in proofs.items()}
        self.actual_proof_bytes = actual_files  # Copy these already validated bytes; never reread mutable paths.
        for name in ('original_primary', 'candidate_primary'):
            require(actual_files[name].strip() == b'0', 'Original/candidate genuine primary 0 required')
        for name, field in (
                ('original_guard', 'actual113_original_guard_sha256'),
                ('candidate_guard', 'actual113_candidate_guard_sha256'),
                ('original_primary', 'Root_actual_original_primary_exit_sha256'),
                ('candidate_primary', 'Root_actual_candidate_primary_exit_sha256')):
            require(self.mapping[field] == self.mapping['proof_files'][name]['sha256'],
                    'Unbound actual proof: ' + field)
        audit = json.loads(actual_files['pair_audit'])
        require(audit['kind'] == 'ROOT_ACTUAL_113_SAME_INPUT_PROJECTION_AUDIT', 'Wrong Root audit')
        require(audit['passed'] is True and audit['literal_indices'] == list(INDICES),
                'Root actual pair audit incomplete')
        for key in ('same_full_callers', 'only_measured_window_metric_leaves_changed',
                    'caller_and_three_formatter_purity', 'whole_source_and_CORE_stable'):
            require(audit[key] is True, 'Root audit qualification missing: ' + key)
        audit_rows = audit['rows']
        require(type(audit_rows) is list and len(audit_rows) == 10, 'Missing per-row Root audit')
        for row, audit_row in zip(rows, audit_rows):
            require(row['expected_mapping_ready'] is True, 'Unmeasured row')
            for name in ('literal_index', 'full_source_row_sha256_json_ordered',
                         'input_sha256_json_ordered', 'original_projection_native090_sha256',
                         'candidate_projection_native090_sha256',
                         'original_caller_native090_sha256', 'candidate_caller_native090_sha256'):
                require(row[name] == audit_row[name], 'Root measured row binding drift: ' + name)
            require(row['original_caller_native090_sha256'] == row['candidate_caller_native090_sha256'],
                    'Original/candidate full caller graphs differ')
            require(audit_row['metric_leaf_admission_sha256'] == digest(row['metric_leaf_admission']),
                    'Root measured leaf proof mismatch')
            for field, name in (
                    ('Root_actual_original_receipt_sha256', 'original_receipt'),
                    ('Root_actual_candidate_receipt_sha256', 'candidate_receipt'),
                    ('Root_actual_pair_audit_sha256', 'pair_audit')):
                require(row[field] == self.mapping['proof_files'][name]['sha256'],
                        'Root row receipt/audit unbound')
            metrics = row['metric_leaf_admission']
            require(tuple(metrics) == tuple('estimate.skill.' + key for key in METRICS),
                    'Unknown/missing metric path')
            changed = []
            for key, leaf in metrics.items():
                validate_leaf(leaf)
                if leaf['actual_changed']:
                    changed.append(key)
            require(changed and 'estimate.skill.window_seconds' in changed, 'No proved window fix')
            require('estimate.skill.window_hps' not in changed,
                    'No healing-domain exception in this ten-row source matrix')
            for name in ('original_projection_native090_sha256',
                         'candidate_projection_native090_sha256',
                         'original_caller_native090_sha256', 'candidate_caller_native090_sha256'):
                value = row[name]
                require(type(value) is str and len(value) == 64 and
                        all(c in '0123456789abcdef' for c in value), 'Unbound measured graph digest')

    def install(self, original, native, current_row, current_caller):
        def projection(result):
            row = current_row()
            if row is None:
                return original(result)
            row_hash = digest(row)
            admitted = self.rows.get(row_hash)
            if admitted is None:
                return original(result)
            index = admitted['literal_index']
            require(index not in self.consumed, 'Duplicate bridge consumption')
            for key in ('section', 'pair_id', 'widget_checked'):
                require(type(row[key]) is type(admitted[key]) and row[key] == admitted[key],
                        'Changed row identity: ' + key)
            require(digest(row['input']) == admitted['input_sha256_json_ordered'],
                    'Changed ordered requested input')
            caller = current_caller()
            for key, value in row['input'].items():
                require(native(caller[key]) == native(value), 'Changed requested input: ' + key)
            require(digest(native(caller)) == admitted['candidate_caller_native090_sha256'],
                    'Whole actual caller differs from measured candidate')
            purity_before = digest(native((result, caller)))
            actual = original(result)  # The unmodified original projection, exactly once.
            actual_hash = digest(native(actual))
            require(actual_hash == admitted['candidate_projection_native090_sha256'],
                    'Whole measured candidate projection drift')
            old_skill = row['expected_public_projection']['estimate']['skill']
            actual_skill = actual['estimate']['skill']
            exceptions, measured = [], {}
            for name in METRICS:
                path = 'estimate.skill.' + name
                leaf = admitted['metric_leaf_admission'][path]
                old, new = validate_leaf(leaf)
                require(encoded(scalar(name in old_skill, old_skill.get(name))) == encoded(old),
                        'Old scalar differs from untouched literal: ' + path)
                require(encoded(scalar(name in actual_skill, actual_skill.get(name))) == encoded(new),
                        'Actual new scalar differs from measured oracle: ' + path)
                if name == 'window_seconds':
                    require(encoded(scalar(True, row['input']['window_seconds'])) == encoded(new),
                            'Measured new observation window must equal the declared input')
                measured[path] = {'old_source': old, 'actual_new': new,
                                  'actual_changed': leaf['actual_changed']}
                if leaf['actual_changed']:
                    exceptions.append(path)
            comparison = copy.deepcopy(actual)
            for path in exceptions:
                name = path.rsplit('.', 1)[1]
                comparison['estimate']['skill'][name] = old_skill[name]
            require(purity_before == digest(native((result, caller))),
                    'Bridge mutated raw result/caller')
            self.consumed.add(index)
            self.ledger.append({'literal_index': index, 'section': row['section'],
                'pair_id': row['pair_id'], 'widget_checked': row['widget_checked'],
                'full_source_row_sha256_json_ordered': row_hash,
                'input_sha256_json_ordered': admitted['input_sha256_json_ordered'],
                'actual_candidate_projection_native090_sha256': actual_hash,
                'actual_caller_native090_sha256': digest(native(caller)),
                'Root_original_caller_native090_sha256': admitted['original_caller_native090_sha256'],
                'comparison_only_exceptions': exceptions, 'metric_leaves': measured,
                'raw_result_and_caller_unchanged': True,
                'mapping_sha256': self.map_sha256, 'Root_actual_pair_audit_sha256': self.proof_sha256})
            self.write_ledger()
            return comparison
        return projection

    def write_ledger(self):
        record = {'kind': 'ACTUAL_FULL120_COMPARISON_ONLY_BRIDGE_LEDGER',
            'mapping_sha256': self.map_sha256, 'Root_actual_pair_audit_sha256': self.proof_sha256,
            'expected_literal_indices': list(INDICES), 'actual_admissions': self.ledger,
            'all10_admitted': sorted(self.consumed) == list(INDICES),
            'project_or_full_window_pass_claimed': False,
            'scope': '42 unchanged historical projections;10 protected projections with explicit proved113 window-metric exceptions',
            'native090_limit': 'Type/order/floatbits tree only; no alias or cycle identity proof'}
        temporary = self.out / 'full120-113-bridge-ledger.json.tmp'
        with temporary.open('wb') as stream:
            stream.write(encoded(record) + b'\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, self.out / 'full120-113-bridge-ledger.json')
