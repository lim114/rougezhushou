from pathlib import Path
from hashlib import sha256
import ast, json
ROOT = Path(__file__).resolve().parents[1]
origin = ROOT / '.cache/p3-311-view'
raw = (origin / 'HANDOFF_FINAL.json').read_bytes()
assert sha256(raw).hexdigest() == '33cde547364ca343eecf598e6ac665aa8f3fc8f71becbbb2640e170b57f53dab'
h = json.loads(raw)
parent = ROOT / 'rouge/battle_view.py'
assert sha256(parent.read_bytes()).hexdigest() == 'ea4e0cf1bb2bf8df91ceca0036d050db2c5fc07241fd6d9bc8485e3bc577a716'
def methods(content):
    module = ast.parse(content)
    cls = next(node for node in module.body if isinstance(node, ast.ClassDef) and node.name == 'BattlePreviewPanel')
    return {node.name: ast.dump(node, include_attributes=False) for node in cls.body if isinstance(node, ast.FunctionDef)}
before = methods(parent.read_text('utf8'))
after = methods((origin / 'candidate/rouge/battle_view.py').read_text('utf8'))
unchanged = ['_refresh_enemy_form', 'open_enemy_form', '_refresh_boss_phase', 'open_boss_phase_reference',
             '_refresh_boss_cycle', 'open_boss_cycle_reference']
assert all(before[name] == after[name] for name in unchanged)
assert {name for name in before if before[name] != after[name]} == {'__init__', '_load_stage', 'render_rows', '_render_enemy'}
for name, pin in h['promotion_files'].items():
    target = ROOT / name
    assert target.resolve().is_relative_to(ROOT.resolve())
    assert name == 'rouge/battle_view.py' or not target.exists(), name
    content = (origin / 'candidate' / name).read_bytes()
    assert sha256(content).hexdigest() == pin['sha256'] and len(content) == pin['bytes'], name
    ast.parse(content.decode('utf8'))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)
out = ROOT / 'verification/sections/311-preparation'
(out / 'ui-final-handoff.json').write_bytes(raw)
(out / 'execution-promote-view.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({'section': 311, 'promoted_files': len(h['promotion_files']),
                  'six_old_reader_methods_AST_unchanged': True, 'native_or_product_acceptance': False}))
