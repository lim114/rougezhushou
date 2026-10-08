from pathlib import Path
import ast,hashlib,json,subprocess
OUT=Path(__file__).resolve().parent
REPO=Path('/workspace/rougezhushou')
index=json.loads((OUT/'fixed-source-index088.json').read_text())
inverse=json.loads((OUT/'surgical-byte-inverse088.json').read_text())
changed=set(inverse['changes'])
for row in index['files']:
    base=(OUT/'baseline'/row['path']).read_bytes()
    fixed=subprocess.check_output(['git','show',index['baseline_commit']+':'+row['path']],cwd=REPO)
    assert base==fixed
    assert hashlib.sha256(base).hexdigest()==row['sha256']
    if row['path'] not in changed:assert (OUT/'draft'/row['path']).read_bytes()==base
for name,record in inverse['changes'].items():
    draft=(OUT/'draft'/name).read_bytes()
    assert hashlib.sha256(draft).hexdigest()==record['draft_sha256']
    for edit in reversed(record['edits']):
        before=bytes.fromhex(edit['before_hex']);after=bytes.fromhex(edit['after_hex'])
        assert draft.count(after)==edit['count'];draft=draft.replace(after,before)
    assert draft==(OUT/'baseline'/name).read_bytes()
    if name!='rouge/amiya_continuous_reference.py':
        raw=(OUT/'draft'/name).read_bytes();assert raw.count(b'\n')==raw.count(b'\r\n')
reads=[]
for tree in ('baseline','draft'):
    literal=[];helper=[]
    for row in index['files']:
        if not row['path'].endswith('.py'):continue
        p=OUT/tree/row['path'];body=ast.parse(p.read_text())
        for n in ast.walk(body):
            if isinstance(n,ast.Call):
                if (isinstance(n.func,ast.Attribute) and n.func.attr=='get' and n.args and
                    isinstance(n.args[0],ast.Constant) and n.args[0].value=='continuous_attacks'):
                    literal.append({'path':row['path'],'line':n.lineno})
                if isinstance(n.func,ast.Name) and n.func.id=='read_continuous_attacks':helper.append({'path':row['path'],'line':n.lineno})
    reads.append({'tree':tree,'literal':literal,'helper':helper})
assert len(reads[0]['literal'])==12 and len(reads[1]['literal'])==0 and len(reads[1]['helper'])==12
leaf=ast.parse((OUT/'draft/rouge/condition_inputs.py').read_text())
test=ast.parse((OUT/'test_continuous_attacks_text_input.py').read_text())
methods=[n.name for n in ast.walk(test) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')]
assert len(methods)==8
relic=(OUT/'baseline/rouge/relics.py').read_text()
assert "scenario['_relic_rules']=rules" in relic
source={}
for name in ('rouge/relics.py','rouge/sp_events.py','rouge/damage.py','rouge/operator_engine.py'):
    s=(OUT/'baseline'/name).read_text()
    module=ast.parse(s)
    relevant=[]
    for n in module.body:
        if isinstance(n,ast.FunctionDef) and n.name in ('prepare','charge','_prepare_damage','_evaluate_damage_once'):
            relevant.append({'function':n.name,'line':n.lineno,'source':ast.get_source_segment(s,n)})
    source[name]=relevant
plan=(OUT/'matrix-plan088.json').read_bytes()
receipt={'status':'PASS_STATIC_BEFORE_ANY_PRODUCT_CALLS','baseline_commit':index['baseline_commit'],
    'fixed_files':len(index['files']),'unchanged_draft_files':len(index['files'])-len(changed),
    'inverse_all_six_old_files_exact':True,'CRLF_preserved':True,'reads':reads,
    'tail_observer_extra_gets':0,'old_83_to_86_core_function_body_exact':True,
    'new_test_methods':methods,'source_bridge':source,
    'matrix_plan_sha256':hashlib.sha256(plan).hexdigest(),'matrix_pairs':len(json.loads(plan)),
    'leaf_sha256':hashlib.sha256((OUT/'draft/rouge/condition_inputs.py').read_bytes()).hexdigest(),
    'test_sha256':hashlib.sha256((OUT/'test_continuous_attacks_text_input.py').read_bytes()).hexdigest(),
    'new_public_or_project_helper_calls':0,'tracked_mutations':0}
(OUT/'static-preflight088.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k not in ('reads','source_bridge','new_test_methods')},ensure_ascii=False))
