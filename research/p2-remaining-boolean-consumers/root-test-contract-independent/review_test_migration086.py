"""Read-only exact source/AST review of the proposed historical test migration."""
import ast
import hashlib
import json
from pathlib import Path

OUT=Path(__file__).resolve().parent
PROPOSAL=OUT.with_name('p2-section086-root-test-contract-supplement')
REPO=Path('/workspace/rougezhushou')


def proof(path):
    data=path.read_bytes()
    return {'source_path':str(path),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}


a=(PROPOSAL/'test_orchid_near_text_input-original085.py').read_bytes()
b=(PROPOSAL/'test_orchid_near_text_input-adapted086.py').read_bytes()
assert hashlib.sha256(a).hexdigest()=='8fd8cdaf383ab54945404ad33c5f610c2fc2e4bb018800b1a8bed3193a0dce86'
assert hashlib.sha256(b).hexdigest()=='62c74f4f094442e689e60d5e6306fbdd6cec357173ff7a295bb5c47cf93af901'
old="        self.assertEqual(record({**args,'double_charge':'false'}),default)\n".encode()
new=("        # Section86 rejects text at this actual S1 consumer; S2/S3 stay ignored.\n"
     "        with self.assertRaisesRegex(ValueError,'^double_charge 不接受文本条件；请使用布尔值。$'):\n"
     "            record({**args,'double_charge':'false'})\n").encode()
assert a.count(old)==1 and b==a.replace(old,new)
trees=[ast.parse(v.decode()) for v in (a,b)]
find=lambda tree,name:next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name==name)
methods=[find(t,'test_double_charge_scope_defaults_and_unbound_clock_are_preserved') for t in trees]
assert len(methods[1].body)==len(methods[0].body)
changes=[i for i,(x,y) in enumerate(zip(methods[0].body,methods[1].body)) if ast.dump(x)!=ast.dump(y)]
assert changes==[3]
replacement=methods[1].body[3]
assert isinstance(replacement,ast.With) and len(replacement.items)==len(replacement.body)==1
call=replacement.items[0].context_expr
assert call.func.attr=='assertRaisesRegex' and ast.unparse(call.args[0])=='ValueError'
assert ast.literal_eval(call.args[1])=='^double_charge 不接受文本条件；请使用布尔值。$'
assert ast.dump(methods[0].body[3].value.args[0])==ast.dump(replacement.body[0].value)
for name in [n.name for n in ast.walk(trees[0]) if isinstance(n,ast.FunctionDef) and n.name!='test_double_charge_scope_defaults_and_unbound_clock_are_preserved']:
    assert ast.dump(find(trees[0],name))==ast.dump(find(trees[1],name))
scenario=find(trees[0],'scenario');assert scenario.args.args[0].arg=='skill' and ast.literal_eval(scenario.args.defaults[0])==1
assert "FIELD='near_previous_deployment'" in a.decode()
damage=(REPO/'rouge/damage.py').read_bytes();engine=(REPO/'rouge/operator_engine.py').read_bytes()
assert hashlib.sha256(damage).hexdigest()=='6cc15cf93eb52fc42120fff6b795e2cbbf2903cf0af8d7d293ffea9f73f121c6'
assert hashlib.sha256(engine).hexdigest()=='c6a7b5e5cd444480f3579a8174246a31f891cb7a2b1c93bbf0826aa4a7765c68'
text=damage.decode()
assert "if op=='char_1048_orchd2' and number==1:conditions+=('double_charge',)" in text
assert "if isinstance(scenario.get(field),str):\r\n            raise ValueError(field+' 不接受文本条件；请使用布尔值。')" in text
assert "self.s.get('double_charge',True)" in engine.decode()
for name in ('migration-proposal.json','test_orchid_near_text_input-original085.py','test_orchid_near_text_input-adapted086.py'):
    with (OUT/('bound-'+name)).open('xb') as f:f.write((PROPOSAL/name).read_bytes())
source={'current_product_bindings':[proof(REPO/'rouge/damage.py'),proof(REPO/'rouge/operator_engine.py')],
        'default_test_skill':1,'selected_old_field':False,'runtime_statement_changes':[3],
        'other_all_AST_functions_unchanged':True,'exact_full_test_byte_replacement_only':True,
        'new_guard':'owner Orchid and skill1 and str; no talent qualification required for double_charge',
        'legacy_numeric_and_nonstr_aliases_inactive_S2S3_and_unknown_clocks_preserved':True}
(OUT/'source-and-test-migration-proof086.json').write_text(json.dumps(source,ensure_ascii=False,indent=2)+'\n')
result={'status':'PASS_FINAL_STATIC_TEST_MIGRATION_ONLY','product_bytes_unchanged':True,
        'test_before_sha256':hashlib.sha256(a).hexdigest(),'test_after_sha256':hashlib.sha256(b).hexdigest(),
        'reason':'Old85 S1 textual truthiness assertion directly conflicts with the approved86 active consumer contract; exact ValueError assertion is the required contract migration.',
        'assertion_scope':'Only active S1 string call changed to anchored exact ValueError; default/bool/False/S2S3 ignored fields and unbound clock assertions remain exact.',
        'time_boundary':'Original root-source-086.json records the true PRE-migration 720 unchanged old files. AFTER applying this test-only migration, root must separately prove 719 unchanged + 1 exact assertion migration. Original checker, original author130 and independent39 remain immutable.',
        'source_proof':proof(OUT/'source-and-test-migration-proof086.json'),'API':0,'helpers':0,'tests':0,'Qt':0,'Wine':0,'tracked_edits':0,
        'root_apply_and_required_targeted_selected_rerun_not_claimed':True}
(OUT/'receipt-test-migration-final086.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False))
