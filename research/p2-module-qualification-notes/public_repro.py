import json
import sys

sys.path.insert(0, sys.argv[1])
from rouge.damage import calculate_damage
from rouge.reporting import format_report

scenario = {'operator': 'mechanist', 'elite': 2, 'level': 59,
            'skill': 1, 'skill_rank': 7, 'timing_mode': 'frames',
            'module_id': 'uniequip_002_mcnist', 'module_level': 3}
plain = {key: value for key, value in scenario.items()
         if key not in ('module_id', 'module_level')}
requested, absent = calculate_damage(scenario), calculate_damage(plain)
print(json.dumps({
    'scenario': scenario,
    'request_base_stats': requested['estimate']['base_stats'],
    'without_module_base_stats': absent['estimate']['base_stats'],
    'request_training': requested['estimate']['training'],
    'module_notes': [note for note in requested['estimate']['notes'] if '模组' in note],
    'formatted_report': format_report(requested),
}, ensure_ascii=False, indent=2))
