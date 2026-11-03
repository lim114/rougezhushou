"""Root-owned local AST adapter; new feature remains cache-only until explicit apply."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import ast,json,subprocess,argparse,textwrap
R=Path(__file__).resolve().parents[1]
def method(s,name):return next(n for c in ast.parse(s).body if isinstance(c,ast.ClassDef) and c.name=='ExpansionUpdatePanel' for n in c.body if isinstance(n,ast.FunctionDef) and n.name==name)
def rewrite(s,name,front):
    n=method(s,name);original=deepcopy(n.body);prefix=ast.parse(textwrap.dedent(front)).body;n.body=prefix+n.body
    assert [ast.dump(x) for x in n.body[len(prefix):]]==[ast.dump(x) for x in original]
    lines=s.splitlines(keepends=True);return ''.join(lines[:n.lineno-1])+textwrap.indent(ast.unparse(n),'    ')+'\n'+''.join(lines[n.end_lineno:])
ADAPTERS='''
def _close_terrain_directory(self):
    child=getattr(self,'terrain_directory_dialog',None)
    if child is not None:child.panel.clear_reference();child.close()
    self.terrain_directory_dialog=None

def _sync_terrain_directory(self,ready):
    allowed=self.full_catalog and 'stages' in self.allowed_categories
    self.terrain_directory_button.setVisible(allowed);self.terrain_directory_button.setEnabled(ready and allowed)
    child=getattr(self,'terrain_directory_dialog',None)
    if not ready or not allowed:self._close_terrain_directory();return False
    if child is not None and child.isVisible():child.panel.refresh_reference()
    return True

def open_terrain_directory(self):
    if not self.full_catalog or 'stages' not in self.allowed_categories:self._close_terrain_directory();return False
    fresh=model.packet()
    if fresh is None or fresh['source_identity']!=self.source_identity:self._unavailable();return False
    from .current_terrain_directory_view import CurrentTerrainDirectoryDialog
    self._close_terrain_directory();child=CurrentTerrainDirectoryDialog(self);self.terrain_directory_dialog=child
    if child.panel.reference is None:self._close_terrain_directory();return False
    child.show();return True
'''

def add_selectors_before_main(source, selectors):
    tree = ast.parse(source)
    expected = ast.dump(ast.parse("__name__ == '__main__'", mode='eval').body, include_attributes=False)
    guards = [node for node in tree.body if isinstance(node, ast.If) and ast.dump(node.test, include_attributes=False) == expected]
    if len(guards) != 1:
        raise ValueError('Expected exactly one top-level __main__ guard')
    prior = [ast.dump(node, include_attributes=False) for node in tree.body]
    addition = ast.parse('ADDITIONAL_MODULES += ' + repr(tuple(selectors))).body[0]
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AugAssign)):
            value = getattr(node, 'value', None)
            if isinstance(value, (ast.Tuple, ast.List)):
                old = [item.value for item in value.elts if isinstance(item, ast.Constant) and isinstance(item.value, str)]
                if set(selectors).intersection(old):
                    raise ValueError('New selector already present')
    guard_index = tree.body.index(guards[0])
    lines = source.splitlines(keepends=True)
    lines[guards[0].lineno - 1:guards[0].lineno - 1] = [ast.unparse(addition) + '\n\n']
    result = ''.join(lines)
    actual = ast.parse(result).body
    if ast.dump(actual[guard_index], include_attributes=False) != ast.dump(addition, include_attributes=False):
        raise ValueError('Selector addition is not immediately before original main guard')
    recovered = actual[:guard_index] + actual[guard_index + 1:]
    if [ast.dump(node, include_attributes=False) for node in recovered] != prior:
        raise ValueError('Existing top-level AST/order changed')
    return result

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--expected-head',required=True);parser.add_argument('--apply',action='store_true');args=parser.parse_args()
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R).decode().strip()==args.expected_head
    assert subprocess.check_output(['git','branch','--show-current'],cwd=R).decode().strip()=='codex/p2-development'
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=R).strip()
    cp=json.loads((R/'DEVELOPMENT_CHECKPOINT.json').read_bytes());assert cp['completed_sections']==377
    proposed={'rouge/current_terrain_directory.py':(R/'.cache/terrain378-model.py').read_bytes(),
        'rouge/current_terrain_directory_view.py':(R/'.cache/terrain378-view.py').read_bytes(),
        'tests/test_current_terrain_directory_378.py':(R/'.cache/terrain378-tests.py').read_bytes(),
        'scripts/verify_current_terrain_directory_window_378.py':(R/'.cache/terrain378-native.py').read_bytes(),
        'scripts/check_current_terrain_directory_378.py':(R/'.cache/terrain378-sourcecheck.py').read_bytes()}
    for name,raw in proposed.items():assert not(R/name).exists();ast.parse(raw)
    name='rouge/expansion_view.py';before=(R/name).read_text('utf8');assert 'def open_terrain_directory(' not in before;s=before
    n=method(s,'__init__');anchor=next(x for x in ast.walk(n) if isinstance(x,ast.Expr) and 'self.enemy_directory_button.clicked.connect(self.open_enemy_directory)'==ast.unparse(x))
    lines=s.splitlines(keepends=True);code="self.terrain_directory_dialog=None\nself.terrain_directory_button=QPushButton('按地形与效果查找关卡')\nself.terrain_directory_button.setAccessibleName('按地形效果查找准确关卡和地图格')\nlayout.addWidget(self.terrain_directory_button)\nself.terrain_directory_button.setVisible(self.full_catalog and 'stages' in self.allowed_categories)\nself.terrain_directory_button.clicked.connect(self.open_terrain_directory)\n"
    s=''.join(lines[:anchor.end_lineno])+textwrap.indent(code,'        ')+''.join(lines[anchor.end_lineno:])
    for name,front in(('_unavailable','self._close_terrain_directory();self.terrain_directory_button.setEnabled(False)'),('close_children','self._close_terrain_directory()'),('_sync_enemy_directory','self._sync_terrain_directory(ready)')):s=rewrite(s,name,front)
    tree=ast.parse(s);klass=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='ExpansionUpdatePanel');lines=s.splitlines(keepends=True)
    s=''.join(lines[:klass.end_lineno])+'\n'+textwrap.indent(textwrap.dedent(ADAPTERS).strip()+'\n','    ')+''.join(lines[klass.end_lineno:]);ast.parse(s)
    oldcls=next(x for x in ast.parse(before).body if isinstance(x,ast.ClassDef) and x.name=='ExpansionUpdatePanel');newcls=next(x for x in ast.parse(s).body if isinstance(x,ast.ClassDef) and x.name=='ExpansionUpdatePanel');new={x.name:x for x in newcls.body if isinstance(x,ast.FunctionDef)}
    for f in(x for x in oldcls.body if isinstance(x,ast.FunctionDef)):
        seq=iter([ast.dump(x) for x in new[f.name].body]);assert all(any(v==ast.dump(x) for v in seq) for x in f.body),f.name
    proposed['rouge/expansion_view.py']=s.encode()
    selector_source=add_selectors_before_main((R/'scripts/verify_full_available.py').read_text('utf8'),('tests.test_current_terrain_directory_378',))
    proposed['scripts/verify_full_available.py']=selector_source.encode('utf8')
    sources=['research/p3-current-battle-314/source-inputs.json','research/p3-current-battle-314/source-selection.json','research/p3-current-terrain-353/source-notes.json','research/p3-current-terrain-353/runtime-manifest.json','rouge/current_terrain.py','rouge/current_stage_directory.py','rouge/current_map_position.py']
    notes={'section':378,'purpose':'按固定地形效果反查关卡与准确原格，不计算实际部署/生效。','sources':{n:{'bytes':len((R/n).read_bytes()),'sha256':sha256((R/n).read_bytes()).hexdigest()} for n in sources},'new_mechanism_assumed':False,'all_current_source_stages_required':True,'original_tile_index_retained':True,'only_grid_used_tile_declarations_included':True,'different_parameter_declarations_not_merged':True,'effect_names_and_units':'Reuse the already source-verified353 single-tile decoder, including its unknowns and exact source URLs. No new terrain name or numerical model.','map_boundary':'Only319 already qualified centers may appear on original images. Selecting an unqualified cell does not infer its image position.','unknown_exact_tile_key':'tile_pollution_roadf remains unknown; no new lead or fabricated effect.','current_generation_deployment_first_tick_damage_unknown':True,'private_state_touched':False}
    proposed['research/p3-current-terrain-directory-378/source-notes.json']=(json.dumps(notes,ensure_ascii=False,indent=2)+'\n').encode()
    plan={'section':378,'expected_head':args.expected_head,'applied':args.apply,'existing_AST_statements_retained_in_order':True,'files':{n:{'bytes':len(raw),'sha256':sha256(raw).hexdigest()} for n,raw in proposed.items()},'tests_or_native_run_by_installer':False}
    (R/'.cache/terrain378-install-plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    if args.apply:
        for n,raw in proposed.items():p=R/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
    print(json.dumps({'section':378,'applied':args.apply,'public_paths':list(proposed)},ensure_ascii=False))
if __name__=='__main__':main()
