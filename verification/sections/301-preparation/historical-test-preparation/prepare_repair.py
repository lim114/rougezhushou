"""Prepare one historical assertion-scope migration; never run tests or edit live."""
import ast
from hashlib import sha256
import difflib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
TEST='tests/test_documented_item_integration_295.py'
TARGET='test_every_reward_query_including_target_is_exactly_unchanged'
ORIGINAL_MODULE='verification/sections/298-preparation/before/rouge/node_catalog.py'
raw=(ROOT/TEST).read_bytes();old=raw.decode('utf8')
(HERE/'original-test.py').write_bytes(raw)
before_module=(ROOT/ORIGINAL_MODULE).read_bytes();current_module=(ROOT/'rouge/node_catalog.py').read_bytes()
baseline_raw=(ROOT/'verification/sections/295-preparation/pre295-query-baseline.json').read_bytes();baseline=json.loads(baseline_raw)
assert sha256(baseline_raw).hexdigest()=='50799b7758d235963e97f3c844211abcce9cfcb3caf5b3be16a69495a347bb27'
assert sha256(before_module).hexdigest()==baseline['node_catalog_sha256']
def function(raw,name):
 tree=ast.parse(raw.decode('utf8'));return next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name==name)
def canon(node):return ast.dump(node,include_attributes=False)
assert canon(function(before_module,'event_reward_options'))==canon(function(current_module,'event_reward_options'))
guard="        self.assertEqual(sha256((ROOT/'rouge/node_catalog.py').read_bytes()).hexdigest(),old['node_catalog_sha256'])"
assert old.count(guard)==1
replacement="""        original=(ROOT/'verification/sections/298-preparation/before/rouge/node_catalog.py').read_bytes()
        self.assertEqual(sha256(original).hexdigest(),old['node_catalog_sha256'])
        original_tree=ast.parse(original.decode('utf8'))
        current_tree=ast.parse((ROOT/'rouge/node_catalog.py').read_bytes().decode('utf8'))
        original_query=next(n for n in original_tree.body if isinstance(n,ast.FunctionDef) and n.name=='event_reward_options')
        current_query=next(n for n in current_tree.body if isinstance(n,ast.FunctionDef) and n.name=='event_reward_options')
        self.assertEqual(ast.dump(current_query,include_attributes=False),ast.dump(original_query,include_attributes=False))"""
newline='\r\n'if'\r\n'in old else'\n'
updated=old.replace('import json'+newline,'import ast'+newline+'import json'+newline,1).replace(guard,replacement.replace('\n',newline))
target=HERE/'candidate'/TEST;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(updated.encode('utf8'))
def tests(source):
 tree=ast.parse(source)
 return{n.name:n for c in tree.body if isinstance(c,ast.ClassDef)for n in c.body if isinstance(n,ast.FunctionDef)and n.name.startswith('test_')}
a,b=tests(old),tests(updated)
assert set(a)==set(b)
changed=[name for name in a if canon(a[name])!=canon(b[name])]
assert changed==[TARGET]
# The original baseline hash, count and full38 loop are the unchanged prefix.
assert all(canon(x)==canon(y)for x,y in zip(a[TARGET].body[:-1],b[TARGET].body[:len(a[TARGET].body)-1]))
prefix_ast=[canon(n)for n in a[TARGET].body[:-1]]
old_tree=ast.parse(old);new_tree=ast.parse(updated)
assert sum(isinstance(n,ast.Import)and len(n.names)==1 and n.names[0].name=='ast'for n in old_tree.body)==0
assert sum(isinstance(n,ast.Import)and len(n.names)==1 and n.names[0].name=='ast'for n in new_tree.body)==1
old_other=[n for n in old_tree.body if not isinstance(n,ast.ClassDef)]
new_other=[n for n in new_tree.body if not(isinstance(n,ast.Import)and len(n.names)==1 and n.names[0].name=='ast')and not isinstance(n,ast.ClassDef)]
assert[canon(n)for n in old_other]==[canon(n)for n in new_other]
diff=''.join(difflib.unified_diff(old.splitlines(keepends=True),updated.splitlines(keepends=True),fromfile='original/'+TEST,tofile='candidate/'+TEST))
(HERE/'migration.diff').write_bytes(diff.encode('utf8'))
proof={'section':301,'kind':'HISTORICAL295_QUERY_GUARD_SCOPE_MIGRATION_NOT_TEST_PASS',
 'test_file':TEST,'old_test_sha256':sha256(raw).hexdigest(),'new_test_sha256':sha256(updated.encode('utf8')).hexdigest(),
 'changed_method':TARGET,'test_method_count_before':len(a),'test_method_count_after':len(b),
 'changed_test_method_count':1,'unchanged_test_method_count':len(a)-1,
 'all_other_test_method_AST_unchanged':True,'module_change_outside_target_only_ast_import':True,
 'original38_loop_and_baseline_hash_assert_AST_unchanged':True,
 'original_assertion_guard_scope':'entire current node_catalog.py SHA equals pre295 SHA',
 'replacement_guard_scope':'actual pre298 archived full source bound to original pre295 SHA; complete event_reward_options FunctionDef AST unchanged',
 'original_baseline_file':'verification/sections/295-preparation/pre295-query-baseline.json',
 'original_baseline_sha256':sha256(baseline_raw).hexdigest(),'prior_full_source_file':ORIGINAL_MODULE,
 'prior_full_source_sha256':sha256(before_module).hexdigest(),'current_node_catalog_sha256':sha256(current_module).hexdigest(),
 'original_and_current_reward_function_AST_sha256':sha256(canon(function(before_module,'event_reward_options')).encode('utf8')).hexdigest(),
 'original_full_source_restored_or_production_changed':False,
 'source_first_failure_receipt':'verification/sections/301-necessary-attempt1/process.json',
 'source_first_failure_receipt_sha256':sha256((ROOT/'verification/sections/301-necessary-attempt1/process.json').read_bytes()).hexdigest(),
 'first_actual_exit':1,'first_actual_methods':99,'first_actual_failures':1,'first_actual_seconds':40.362,
 'first_actual_source_unchanged':True,'original_methods_not_added_to_final_pass_count':True,
 'preexecution_cache_draft_correction':{'original_draft_retained':'first-draft-missing-import',
  'cause':'Literal LF import insertion did not match original CRLF; caught in static source read before delivery or execution.',
  'new_import_count_explicitly_checked':1,'new_test_line_endings_match_original':True,
  'Qt_or_test_run_for_wrong_draft':False},
 'Qt_tests_or_live_source_executed_or_modified_by_this_preparation':False}
(HERE/'migration.json').write_bytes((json.dumps(proof,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
print(json.dumps({'candidate':str(target),'new_test_sha256':proof['new_test_sha256'],'proof_sha256':sha256((HERE/'migration.json').read_bytes()).hexdigest(),
 'method_count':len(a),'changed':1,'unchanged':len(a)-1,'tests_not_run':True},ensure_ascii=False))
