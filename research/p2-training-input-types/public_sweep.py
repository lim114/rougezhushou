import copy
import hashlib
import json
import sys
from pathlib import Path

PACKAGE = Path(sys.argv[1])
OUTPUT = Path(sys.argv[2])
sys.path.insert(0, str(PACKAGE))
from rouge.catalog import catalog, operator_attributes
from rouge.damage import calculate_damage

rows = []
for op, profile in catalog()['operators'].items():
    for elite, phase in enumerate(profile['phases']):
        for skill, skill_profile in enumerate(profile['skills'], 1):
            if skill_profile['unlock_elite'] > elite:
                continue
            for rank in ((1, 7, 10) if elite == 2 else (1, 5, 7)):
                for level in (1, phase['max_level']):
                    for potential in (1, 6):
                        for mode in ('frames', 'continuous'):
                            args = {'operator': op, 'elite': elite, 'level': level, 'potential': potential,
                                    'skill': skill, 'skill_rank': rank, 'timing_mode': mode}
                            frozen = copy.deepcopy(args)
                            result = calculate_damage(args)
                            assert args == frozen
                            rows.append({'scenario': args, 'result_sha256': hashlib.sha256(json.dumps(result, sort_keys=True, ensure_ascii=False).encode()).hexdigest()})

attributes = []
for op, profile in catalog()['operators'].items():
    for elite, phase in enumerate(profile['phases']):
        for level in (1, phase['max_level'], None):
            for potential in (1, 6):
                args = {'operator': op, 'elite': elite, 'level': level, 'potential': potential}
                attributes.append({'args': args, 'attributes': operator_attributes(**args)})
    for module in profile['modules']:
        for stage in (1, 2, 3):
            args = {'operator': op, 'elite': module['unlock_elite'], 'level': module['unlock_level'],
                    'module_id': module['id'], 'module_level': stage}
            attributes.append({'args': args, 'attributes': operator_attributes(**args)})
            for mode in ('frames', 'continuous'):
                scenario = {**args, 'skill': 1, 'skill_rank': 7, 'timing_mode': mode}
                result = calculate_damage(scenario)
                rows.append({'scenario': scenario, 'result_sha256': hashlib.sha256(json.dumps(result, sort_keys=True, ensure_ascii=False).encode()).hexdigest()})

result = {'public_calculation_calls': len(rows), 'public_attributes_calls': len(attributes),
          'records': rows, 'attributes': attributes}
OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'output': str(OUTPUT), 'public_calculation_calls': len(rows), 'public_attributes_calls': len(attributes)}))
