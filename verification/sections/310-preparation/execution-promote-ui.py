from pathlib import Path
from hashlib import sha256
import ast,json
ROOT=Path(__file__).resolve().parents[1];folder=ROOT/'.cache/p3-310-view';h=folder/'HANDOFF.json'
assert sha256(h.read_bytes()).hexdigest()=='04afcb60ea64e2ca745f711386e6c937c48768820fa650240d91c0e18cc5f9f1'
meta=json.loads(h.read_bytes());base=ROOT/meta['candidate_root'];old=(ROOT/'rouge/battle_view.py').read_bytes()
assert sha256(old).hexdigest()==meta['existing_production_change']['rouge/battle_view.py']['before']['sha256']
def methods(raw):
    cls=next(n for n in ast.parse(raw).body if isinstance(n,ast.ClassDef)and n.name=='BattlePreviewPanel')
    return{n.name:ast.dump(n,include_attributes=False)for n in cls.body if isinstance(n,ast.FunctionDef)}
one,two=methods(old),methods((base/'rouge/battle_view.py').read_bytes())
names=['_refresh_enemy_form','open_enemy_form','_refresh_boss_phase','open_boss_phase_reference'];assert all(one[n]==two[n]for n in names)
for name,pin in meta['promotion_files'].items():
    raw=(base/name).read_bytes();assert sha256(raw).hexdigest()==pin['sha256']and len(raw)==pin['bytes']
    ast.parse(raw);assert not raw.endswith(b'\n\n')and not raw.endswith(b'\r\n\r\n')
    (ROOT/name).write_bytes(raw)
out=ROOT/'verification/sections/310-preparation';(out/'ui-candidate-handoff.json').write_bytes(h.read_bytes());(out/'execution-promote-ui.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({'files_promoted':len(meta['promotion_files']),'old_methods_AST_unchanged':names,'tests_or_Qt_run':False}))
