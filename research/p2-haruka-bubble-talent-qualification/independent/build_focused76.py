import json
from pathlib import Path

own = Path(__file__).parent
initial = json.loads((own / 'author-initial-public-cases.json').read_text())
cases = [{'label': 'fresh-replay-initial24', 'scenario': x['scenario']} for x in initial]
for mode in ('frames', 'continuous'):
    base = {'operator': 'char_4202_haruka', 'skill': 1, 'skill_rank': 7,
            'elite': 2, 'level': 1, 'base_attack': 1000, 'window_seconds': 10,
            'bubble_bursts': 1, 'timing_mode': mode}
    for stage in (1, 2, 3):
        cases.append({'label': 'e2-s3-eligible-module-whole-output-stage-' + str(stage),
                      'scenario': {**base, 'skill': 3, 'skill_rank': 10, 'level': 60,
                                   'potential': 5, 'module_id': 'uniequip_002_haruka', 'module_level': stage}})
    for potential in (4, 5):
        cases.append({'label': 'e2-raw-talent-potential-boundary',
                      'scenario': {**base, 'potential': potential}})
    cases.append({'label': 'e2-s2-zero-attack-still-qualified-unknown',
                  'scenario': {**base, 'skill': 2, 'base_attack': 0}})
    cases.append({'label': 'e2-s3-zero-attack-with-module-still-qualified-unknown',
                  'scenario': {**base, 'skill': 3, 'skill_rank': 10, 'level': 60,
                               'module_id': 'uniequip_002_haruka', 'module_level': 3, 'base_attack': 0}})
    for level in (59, 60):
        cases.append({'label': 'e2-s2-module-level59-to60-boundary',
                      'scenario': {**base, 'skill': 2, 'level': level,
                                   'module_id': 'uniequip_002_haruka', 'module_level': 3}})
    for label, extra in (
        ('locked-extra-recipient-pending-retained', {'elite': 1, 'skill': 2, 'healing_targets': 3}),
        ('locked-zero-window-declaration-retained', {'elite': 1, 'window_seconds': 0}),
        ('locked-enemy-life0-friendly-treatment-retained', {'elite': 0, 'timing': {'target_disappears_seconds': 0}}),
        ('locked-empty-enemy-windows-ordinary-contract', {'elite': 1, 'skill': 2, 'timing': {'target_windows': []}}),
        ('locked-legal-decimal-string-parsing-retained', {'elite': 1, 'skill': 2, 'bubble_bursts': '1.0'}),
        ('locked-invalid-count-still-rejected', {'elite': 1, 'skill': 2, 'bubble_bursts': True}),
        ('earlier-skill-error-still-first', {'elite': 0, 'skill': 2, 'bubble_bursts': True}),
        ('foreign-owner-still-ignores-unrelated-bubble-count', {'operator': 'char_1035_wisdel', 'skill': 1, 'bubble_bursts': True}),
    ):
        cases.append({'label': label, 'scenario': {**base, **extra}})
(own / 'final-focused-cases76.json').write_text(json.dumps(cases, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'focused_case_records': len(cases), 'includes_initial_readonly_records': len(initial)}))
