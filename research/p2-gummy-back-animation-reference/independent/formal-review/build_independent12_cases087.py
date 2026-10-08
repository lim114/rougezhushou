"""Static independent case design; never imports a production helper."""
from pathlib import Path
import gzip
import json
ROOT = Path(__file__).resolve().parent
BASE = json.loads(gzip.decompress((ROOT.parent / 'source-snapshots/rouge/data/original-animation-references.json.gz').read_bytes()))
OP = 'char_196_sunbr'
FRONT = OP + ':Front:Attack'
BACK = OP + ':Back:Attack'
KALTSIT = next(r['id'] for r in BASE['operators']['kaltsit']['records'] if r['orientation'] == 'Front' and r['animation'] == 'Skill_3_Attack')
cases = [
    {'label': 'qualified_s2_default', 'expect': 'unchanged', 'scenario': {'operator': OP, 'skill': 2, 'elite': 2, 'level': 70, 'skill_rank': 10, 'base_attack': 1000, 'window_seconds': 11}},
    {'label': 'e1_s1_default_unknown', 'expect': 'unchanged', 'scenario': {'operator': OP, 'skill': 1, 'elite': 1, 'level': 60, 'skill_rank': 7, 'base_attack': 1234, 'window_seconds': 20}},
    {'label': 'front_s2_both', 'expect': 'unchanged', 'scenario': {'operator': OP, 'skill': 2, 'base_attack': 1000, 'window_seconds': 11, 'timing': {'animation_reference': FRONT, 'normal_animation_reference': FRONT}}},
    {'label': 'front_s1_normal', 'expect': 'unchanged', 'scenario': {'operator': OP, 'skill': 1, 'base_attack': 1000, 'window_seconds': 13, 'timing': {'normal_animation_reference': FRONT}}},
    {'label': 'other_kaltsit_original_front', 'expect': 'unchanged', 'scenario': {'operator': 'kaltsit', 'skill': 3, 'base_attack': 901, 'window_seconds': 6, 'timing': {'animation_reference': KALTSIT}}},
    {'label': 'other_shu_default', 'expect': 'unchanged', 'scenario': {'operator': 'char_2025_shu', 'skill': 1, 'base_attack': 901, 'window_seconds': 13}},
    {'label': 'back_s2_both_empty_enemy', 'expect': 'new_back', 'scenario': {'operator': OP, 'skill': 2, 'base_attack': 1000, 'window_seconds': 11, 'timing': {'animation_reference': BACK, 'normal_animation_reference': BACK, 'target_windows': []}}},
    {'label': 'back_s2_manual_half_open', 'expect': 'new_back', 'scenario': {'operator': OP, 'skill': 2, 'base_attack': 1000, 'window_seconds': 306 / 30, 'timing': {'animation_reference': BACK, 'windup_frames': 6, 'recovery_frames': 9}}},
    {'label': 'back_s1_both_unknown', 'expect': 'new_back', 'scenario': {'operator': OP, 'skill': 1, 'elite': 1, 'level': 60, 'skill_rank': 7, 'base_attack': 1234, 'window_seconds': 13, 'timing': {'animation_reference': BACK, 'normal_animation_reference': BACK}}},
    {'label': 'back_normal_continuous_zero_recipient', 'expect': 'new_back', 'scenario': {'operator': OP, 'skill': 2, 'base_attack': 1000, 'window_seconds': 12, 'healing_targets': 0, 'timing_mode': 'continuous', 'timing': {'normal_animation_reference': BACK}}},
    {'label': 'invalid_elite_before_recovered_reference', 'expect': 'exact_error', 'scenario': {'operator': OP, 'skill': 2, 'elite': 4, 'timing': {'animation_reference': BACK}}},
    {'label': 'invalid_potential_before_generic_reference', 'expect': 'exact_error', 'scenario': {'operator': OP, 'skill': 1, 'potential': 0, 'timing': {'animation_reference': OP + ':Back:Skill'}}},
]
assert len(cases) == len({json.dumps(case['scenario'], sort_keys=True, ensure_ascii=False) for case in cases}) == 12
(ROOT / 'independent12-cases087.json').write_text(json.dumps({'version': 1, 'case_count': 12, 'maximum_API_calls': 24, 'cases': cases}, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'case_count': 12, 'unique_inputs': 12, 'maximum_API_calls': 24}))
