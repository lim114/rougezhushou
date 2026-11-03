"""Replay existing public scenarios on one isolated post61 source package."""
import copy
import hashlib
import json
import math
import sys
from contextlib import nullcontext
from pathlib import Path
from unittest.mock import patch

FOLDER = Path(__file__).resolve().parent
PACKAGE = FOLDER / sys.argv[1]
OUT = FOLDER / 'validation-after61'
OUT.mkdir(exist_ok=True)
sys.path.insert(0, str(PACKAGE))
sys.dont_write_bytecode = True
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.summons import module_rules


def safe(value):
    if isinstance(value, float) and not math.isfinite(value):
        return {'__nonfinite_float__': 'nan' if math.isnan(value) else '+inf' if value > 0 else '-inf'}
    if isinstance(value, dict):
        return {k: safe(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [safe(v) for v in value]
    return value


def restore(value):
    if isinstance(value, dict):
        if set(value) == {'__nonfinite_float__'}:
            return float({'nan': 'nan', '+inf': 'inf', '-inf': '-inf'}[value['__nonfinite_float__']])
        return {k: restore(v) for k, v in value.items()}
    if isinstance(value, list):
        return [restore(v) for v in value]
    return value


def digest(value):
    return hashlib.sha256(json.dumps(safe(value), sort_keys=True, ensure_ascii=False,
                                    allow_nan=False, separators=(',', ':')).encode()).hexdigest()


def hashes():
    return {p.relative_to(PACKAGE).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted((PACKAGE / 'rouge').rglob('*'))
            if p.is_file() and p.suffix in ('.py', '.json')}


before = hashes()
catalog_before = digest(catalog())
rules_before = digest(module_rules())
original = json.loads((FOLDER / 'public-outcomes.json').read_text())['records']
rows = []
for old in original:
    args = restore(old['input'])
    incoming = digest(args)
    synthetic = old['synthetic_guard_fixture']
    rules = copy.deepcopy(module_rules())
    rules['uniequip_002_deepcl']['hp_composition_verified'] = False
    fixture = patch('rouge.summons.module_rules', return_value=rules) if synthetic else nullcontext()
    row = {k: old[k] for k in ('id', 'context', 'count_label', 'input', 'synthetic_guard_fixture')}
    with fixture:
        try:
            result = calculate_damage(args)
            row.update(status='returned', result=result, result_sha256=digest(result))
        except Exception as error:
            row.update(status='raised', exception={'type': type(error).__name__, 'message': str(error)})
    assert digest(args) == incoming
    row['caller_unchanged'] = True
    rows.append(row)
after = hashes()
assert before == after
assert digest(catalog()) == catalog_before
assert digest(module_rules()) == rules_before
receipt = {'scope': 'Real public calculate_damage replay on post61 external source; no report observer or suppression',
           'package': str(PACKAGE), 'source_sha256': before, 'source_sha256_after': after,
           'source_drift': [], 'calls': len(rows), 'caller_catalog_module_rules_unchanged': True,
           'synthetic_hp_fixture_scope': 'Existing unknown-layer guard only; not a claim that the current original SUM-Y layer is unknown',
           'gui_executed': False, 'wine_executed': False, 'records': rows}
path = OUT / (sys.argv[1] + '.json')
path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
print(json.dumps({'package': sys.argv[1], 'calls': len(rows),
                  'returned': sum(r['status'] == 'returned' for r in rows),
                  'raised': sum(r['status'] == 'raised' for r in rows),
                  'source_drift': [], 'receipt': str(path)}))
