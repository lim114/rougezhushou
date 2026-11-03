"""Read-only preparation facts from actual supported public catalog and code."""
from pathlib import Path
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in (HERE, *HERE.parents) if (p / 'rouge/app.py').is_file())
catalog_path = ROOT / 'rouge/data/catalog.json'
data = json.loads(catalog_path.read_bytes())
operators = data['operators']
simple = ['char_151_myrtle', 'char_133_mm', 'char_4107_vrdant', 'char_206_gnosis',
          'char_437_mizuki', 'char_4087_ines', 'char_2027_wang', 'char_4204_mantra',
          'char_1044_hsgma2', 'char_1035_wisdel', 'char_1048_orchd2', 'char_328_cammou',
          'char_1038_whitw2', 'char_298_susuro', 'char_196_sunbr', 'char_002_amiya']
assert all(key in operators for key in simple)
files = ['PROJECT_PROGRESS.md', 'rouge/data/catalog.json', 'rouge/operator_engine.py',
         'rouge/panel_native_bridge.py', 'rouge/calibration.py', 'rouge/offline_tools_view.py',
         'rouge/app.py', 'research/p2-chen-phase-reference/source-receipt.json',
         'research/p2-amiya-phase-reference/source-receipt.json',
         'research/p2-amiya-input-qualification/source-receipt.json',
         'research/p2-panel-native-finalization-283/source-manifest.json']
engine = (ROOT / 'rouge/operator_engine.py').read_text(encoding='utf8')
assignments = [{'line': line, 'text': text.strip()} for line, text in enumerate(engine.splitlines(), 1)
               if re.search(r'\b(?:attack|speed_reference)\s*[-+*/]?=', text)]
rows = [{'operator': key, 'name': op['name'],
         'skills': [{'number': i + 1, 'id': sk['id'],
                     'last_level_primitive_values': {name: sk['levels'][-1]['values'].get(name)
                        for name in ('atk', 'attack_speed', 'base_attack_time')}}
                    for i, sk in enumerate(op['skills'])]} for key, op in operators.items()]
result = {'kind': 'SECTION284_CANDIDATE_READONLY_FACT_INVENTORY_NOT_IMPLEMENTATION',
          'operator_count': len(operators), 'skill_count': sum(len(v['skills']) for v in operators.values()),
          'first_three_skill_count': sum(len(operators[k]['skills']) for k in ('kaltsit', 'silverash', 'mechanist')),
          'simple_branch_candidate_operator_ids': simple,
          'simple_branch_candidate_operator_count': len(simple),
          'simple_branch_candidate_skill_count': sum(len(operators[k]['skills']) for k in simple),
          'simple_candidate_is_completed_or_current_native_verified': False,
          'operator_skills': rows, 'local_actor_primitive_assignment_sites': assignments,
          'source_sha256': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in files},
          'catalog_source': data['source'], 'private_state_used': False,
          'game_or_chat_actions': 0, 'production_modified': False}
target = HERE / 'candidate-source-inventory-284.json'
assert not target.exists()
target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
print(json.dumps({'output': str(target), 'sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
                  'operators': len(operators), 'skills': result['skill_count'],
                  'simple_candidate_operators': len(simple), 'simple_candidate_skills': result['simple_branch_candidate_skill_count']}, ensure_ascii=False))
