from pathlib import Path
from hashlib import sha256
import ast,json
ROOT=Path(__file__).resolve().parents[1]
name='tests/test_map_projection_048.py'
before=(ROOT/name).read_bytes();assert sha256(before).hexdigest()=='c9055a58b2d02014c2e12c360e061c0cd7164cee7f4405e354bb7b2892625b2c'
comparison=json.loads((ROOT/'.cache/p3-303-root/first-reading-comparison.json').read_bytes())
assert comparison['groups']['ro6_n_2_3']['accepted']==12
text=before.decode('utf8')
old="            if sid in ('ro6_n_2_4', 'ro6_t_1'):"
new="            if sid in ('ro6_n_2_4', 'ro6_t_1', 'ro6_n_2_3'):"
assert text.count(old)==1;text=text.replace(old,new)
old='                self.assertEqual(len(actual.points), 8)'
new="                self.assertEqual(len(actual.points), 12 if sid == 'ro6_n_2_3' else 8)"
assert text.count(old)==1;text=text.replace(old,new)
after=text.encode('utf8');ast.parse(after)
def methods(raw):return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(raw)) if isinstance(n,ast.FunctionDef)}
x,y=methods(before),methods(after)
changed={k for k in x if x[k]!=y.get(k)}
assert changed=={'test_unaccepted_wood_decorations_and_portal_probes_are_retained'} and set(x)==set(y)
target=ROOT/'.cache/p3-303-parent'/name;target.parent.mkdir(parents=True,exist_ok=True);assert not target.exists();target.write_bytes(after)
proof={'section':303,'kind':'historical048_single_method_current_direct_admission_candidate_not_formal_acceptance','path':name,
 'before_sha256':sha256(before).hexdigest(),'after_sha256':sha256(after).hexdigest(),
 'changed_methods':sorted(changed),'other_method_AST_unchanged':len(x)-1,'replaced_lines':2,
 'preserved':['rejected whole-plane records','all four fallback-disabled unknown assertions','two prior direct8 records','unknown ro6_n_3_5','no inverse or segments'],
 'new_direct_point_count':12,'root_full89_comparison_sha256':sha256((ROOT/'.cache/p3-303-root/first-reading-comparison.json').read_bytes()).hexdigest(),
 'production_or_tests_modified_yet':False}
path=ROOT/'.cache/p3-303-parent/historical048-candidate.json';path.write_text(json.dumps(proof,indent=2)+'\n',encoding='utf8')
print(json.dumps(proof))
