"""Observe real public-call integer query gates without changing results."""
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
package = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(package))
from rouge.damage import calculate_damage
from rouge.operator_engine import Combat

original_option = Combat.option
queries = []


def traced_option(self, key, default=0, maximum=None, integer=False):
    try:
        value = original_option(self, key, default, maximum, integer)
    except Exception as error:
        if key == 'bait_triggers':
            queries.append({'key': key, 'raw': self.s.get(key, default), 'maximum': maximum,
                            'integer': integer, 'error_type': type(error).__name__, 'error': str(error)})
        raise
    if key == 'bait_triggers':
        queries.append({'key': key, 'raw': self.s.get(key, default), 'maximum': maximum,
                        'integer': integer, 'validated_value': value})
    return value


Combat.option = traced_option
cases = [({'operator': 'char_1042_phatm2', 'skill': 2, 'bait_triggers': value})
         for value in (0, '0', '0.0', 1, '1.0', False)]
cases += [{'operator': 'char_1042_phatm2', 'skill': 2},
          {'operator': 'char_1042_phatm2', 'skill': 1, 'bait_triggers': {}},
          {'operator': 'char_1042_phatm2', 'skill': 3, 'bait_triggers': {}},
          {'operator': 'silverash', 'skill': 3, 'bait_triggers': {}}]
records = []
for args in cases:
    queries.clear()
    scenario = {'base_attack': 1000, 'window_seconds': 10, **args}
    try:
        result = calculate_damage(scenario)
        value = {'accepted': True, 'total_damage': result['total_damage'],
                 'neural_bait_reference': result.get('neural_bait_reference')}
    except Exception as error:
        value = {'accepted': False, 'error_type': type(error).__name__, 'error': str(error)}
    records.append({'input': scenario, 'queries': list(queries), 'outcome': value})
destination = Path(sys.argv[2]).resolve()
destination.write_text(json.dumps({'package': str(package), 'engine_sha256': hashlib.sha256((package/'rouge/operator_engine.py').read_bytes()).hexdigest(), 'records': records, 'private_state_read': False}, ensure_ascii=False, indent=2)+'\n')
print(json.dumps({'cases': len(records), 'bait_queries': sum(len(row['queries']) for row in records), 'engine_sha256': hashlib.sha256((package/'rouge/operator_engine.py').read_bytes()).hexdigest()}))
