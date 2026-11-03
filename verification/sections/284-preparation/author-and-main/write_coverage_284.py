"""Archive actual declared caller scope; eligibility is not actual native state."""
from pathlib import Path
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in (HERE, *HERE.parents) if (p / 'rouge/app.py').is_file())
sys.path.insert(0, str(ROOT))
from rouge.panel_native_bridge import capture_extended_skill_primitives

data = json.loads((ROOT / 'rouge/data/catalog.json').read_bytes())
rows = []
counts = {'attack': 0, 'attack_speed': 0, 'both': 0}
for op, profile in data['operators'].items():
    if op in ('kaltsit', 'silverash', 'mechanist'):
        continue
    for number, skill in enumerate(profile['skills'], 1):
        # This helper only decides field scope using op/skill and condition flags.
        # Nominal placeholders are not evaluated as a native/current game case.
        _, scope = capture_extended_skill_primitives({'operator': op}, number,
            {'attack_speed': 100}, 100, 0, 0, 0, skill['levels'][-1]['values'])
        for field in ('attack', 'attack_speed'):
            counts[field] += int(scope[field]['common_model_primitives_captured'])
        counts['both'] += int(all(s['common_model_primitives_captured'] for s in scope.values()))
        rows.append({'operator': op, 'operator_name': profile['name'], 'skill': number,
                     'skill_id': skill['id'], 'field_scope': scope})
assert len(rows) == 78 and counts == {'attack': 61, 'attack_speed': 77, 'both': 60}
files = ['rouge/operator_engine.py', 'rouge/panel_native_bridge.py',
         'tests/test_extended_skill_native_284.py', 'rouge/data/catalog.json',
         'rouge/panel_native_finalization.py', 'rouge/panel_native_precision.py']
result = {'kind': 'SECTION284_DECLARED_FIELD_SCOPE_READBACK_NOT_NATIVE_ACTIVATION',
          'operator_count': 29, 'skill_count': len(rows), 'default_scope_counts': counts,
          'default_missing_attack_fields': 17, 'default_missing_attack_speed_fields': 1,
          'condition_scope_changes': [
              'Shu S3 on sown tile excludes both fields; false preserves both.',
              'Xiangzi S2 organ excludes AS only, piano excludes ATK only.',
              'Angel S2 successful steal excludes AS only; false preserves it.'],
          'rows': rows,
          'source_sha256': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in files},
          'is_only_scope_readback_not_78_main_calculation_acceptance': True,
          'actual_native_inventory_calls_clock_hotfix_or_decode_verified': False,
          'legacy174_model_comparison_owned_by_root': True,
          'game_or_chat_actions': 0, 'private_state_used': False}
target = HERE / 'coverage-scope-284.json'
assert not target.exists()
target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
print(json.dumps({'output': str(target), 'sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
                  'default_scope_counts': counts}, ensure_ascii=False))
