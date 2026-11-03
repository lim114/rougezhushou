import copy
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, sys.argv[1])
OUT = Path(sys.argv[2])
from rouge.catalog import catalog, operator_attributes, operator_profiles
from rouge.damage import calculate_damage, _prepare_damage
from rouge.reporting import format_report

before = hashlib.sha256(json.dumps(catalog(), sort_keys=True).encode()).hexdigest()
base = {'operator': 'char_298_susuro', 'skill': 1, 'skill_rank': 7, 'elite': 2, 'level': 40, 'potential': 1}
controls = []
for field in ('skill', 'skill_rank', 'elite', 'level', 'potential', 'module_level'):
    for value in (False, True, 0, 1, 1.0, '1', None):
        args = {**base, field: value}
        if field == 'module_level': args['module_id'] = 'uniequip_002_susuro'
        frozen = copy.deepcopy(args)
        try:
            result = calculate_damage(args)
            outcome = {'accepted': True, 'result_total_healing': result.get('total_healing')}
        except Exception as exc:
            outcome = {'accepted': False, 'error_type': type(exc).__name__, 'error': str(exc)}
        assert frozen == args
        controls.append({'field': field, 'value': value, 'value_type': type(value).__name__, **outcome})

pairs = []
for field, value in [('elite', False), ('elite', True), ('level', True), ('potential', True), ('module_level', True)]:
    boolean = {**base, field: value}
    if field == 'elite' and value is False: boolean['skill_rank'] = 1
    if field == 'module_level': boolean['module_id'] = 'uniequip_002_susuro'
    integer = {**boolean, field: int(value)}
    records = []
    for args in (boolean, integer):
        entry = {'scenario': args}
        try:
            entry['attributes'] = operator_attributes(args['operator'], args['elite'], args['level'], 100,
                                                     args['potential'], args.get('module_id'), args.get('module_level', 0))
            prepared = _prepare_damage(args)[0]
            entry['prepared_fields'] = {k: {'value': v, 'python_type': type(v).__name__} for k, v in prepared.items()
                                        if k in ('elite', 'level', 'potential', 'module_level')}
            result = calculate_damage(args)
            entry['result'] = result
            entry['formatted_training'] = format_report(result).splitlines()[4]
            entry['accepted'] = True
        except Exception as exc:
            entry.update(accepted=False, error_type=type(exc).__name__, error=str(exc))
        records.append(entry)
    pairs.append({'field': field, 'boolean': records[0], 'integer': records[1]})

matrix = []
for op, profile in catalog()['operators'].items():
    for skill in range(1, len(profile['skills']) + 1):
        for elite in range(3):
            for rank in range(1, 11):
                args = {'operator': op, 'skill': skill, 'elite': elite, 'skill_rank': rank}
                try:
                    _prepare_damage(args)
                    outcome = {'accepted': True}
                except Exception as exc:
                    outcome = {'accepted': False, 'error_type': type(exc).__name__, 'error': str(exc)}
                matrix.append({'scenario': args, **outcome})
after = hashlib.sha256(json.dumps(catalog(), sort_keys=True).encode()).hexdigest()
assert before == after
OUT.write_text(json.dumps({'public_controls': controls, 'public_pairs': pairs,
                           'internal_qualification_matrix': matrix,
                           'internal_matrix_is_not_native_qualification_evidence': True,
                           'catalog_hash_before': before, 'catalog_hash_after': after}, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'output': str(OUT), 'public_control_calls': len(controls), 'paired_cases': len(pairs),
                  'internal_matrix_cases': len(matrix), 'internal_matrix_accepted': sum(x['accepted'] for x in matrix)}))
