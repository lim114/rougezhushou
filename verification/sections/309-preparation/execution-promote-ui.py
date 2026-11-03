from pathlib import Path
from hashlib import sha256
import ast, json
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'.cache/p3-309-view'
meta=json.loads((source/'HANDOFF.json').read_bytes())
assert sha256((source/'HANDOFF.json').read_bytes()).hexdigest()=='4d89cad5d34aa5cc977b50ef6935bab2f8ff57972b2b3f248b9fdaa5257b469f'
base=ROOT/meta['candidate_root']
old=(ROOT/'rouge/battle_view.py').read_bytes()
assert sha256(old).hexdigest()==meta['existing_production_change']['rouge/battle_view.py']['before']['sha256']
candidate=(base/'rouge/battle_view.py').read_bytes()
def methods(data):
    panel=next(n for n in ast.parse(data).body if isinstance(n,ast.ClassDef) and n.name=='BattlePreviewPanel')
    return {n.name:ast.dump(n,include_attributes=False) for n in panel.body if isinstance(n,ast.FunctionDef)}
one,two=methods(old),methods(candidate)
assert one['_refresh_enemy_form']==two['_refresh_enemy_form'] and one['open_enemy_form']==two['open_enemy_form']
for name,pin in meta['promotion_files'].items():
    data=(base/name).read_bytes();assert sha256(data).hexdigest()==pin['sha256'] and len(data)==pin['bytes']
    ast.parse(data);(ROOT/name).write_bytes(data)
out=ROOT/'verification/sections/309-preparation'
(out/'ui-candidate-handoff.json').write_bytes((source/'HANDOFF.json').read_bytes())
(out/'ui-preparation-correction.json').write_bytes((source/'revision2/preparation-correction.json').read_bytes())
(out/'execution-promote-ui.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({'promoted_files':list(meta['promotion_files']),'old306_methods_unchanged':True,'Qt_or_tests_run':False}))
