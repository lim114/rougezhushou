"""Attachment hashes plus AST only; no application or formatter execution."""
from pathlib import Path
import ast, json, hashlib
p=Path(__file__).resolve().parent
n=json.loads((p/'source-control-notes085.json').read_bytes())
for r in n['sources'].values():
 s=p/('source-'+Path(r['source_path']).name)
 if s.exists(): assert hashlib.sha256(s.read_bytes()).hexdigest()==r['sha256']
a=(p/'source-app.py').read_text(encoding='utf-8')
assert 'sortItems(' not in a and 'setSortingEnabled(' not in a
calc=next(node for node in ast.walk(ast.parse(a)) if isinstance(node,ast.FunctionDef)and node.name=='calculate')
handler=next(node for node in ast.walk(calc)if isinstance(node,ast.ExceptHandler))
assert isinstance(handler.type,ast.Name)and handler.type.id=='Exception' and handler.name=='error'
assert ast.unparse(handler.body[0])=='self.damage_result = None'
assert ast.unparse(handler.body[1])=='self.show_damage_text(str(error))'
manifest=json.loads((p/'manifest.json').read_bytes())
for r in manifest['files']:
 b=Path(r['source_path']).read_bytes()
 assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256']
print(json.dumps({'passed':True,'attachment_count':len(manifest['files']),'source_copies_exact':True,'error_handler':'except Exception as error: self.damage_result=None; self.show_damage_text(str(error))','application_or_API_calls':0,'Qt_or_Wine_calls':0}))
