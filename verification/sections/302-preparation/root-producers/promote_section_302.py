from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import ast,json,subprocess
ROOT=Path(__file__).resolve().parents[1]
PARENT='87a622eea314ccce49712121fd42683eb2e7e463'
def sha(raw):return sha256(raw).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def load(path,digest):
    raw=(ROOT/path).read_bytes();assert sha(raw)==digest,path
    return json.loads(raw)
assert git('branch','--show-current')=='codex/p2-development'
assert git('rev-parse','HEAD')==PARENT and not git('diff','--cached','--name-only')
assert set(git('diff','--name-only').splitlines())=={'DEVELOPMENT_CHECKPOINT.json'}
backend=load('.cache/p3-302-backend/HANDOFF_FINAL.json','fde5d3147b7e649c20ffa61c26237bf3f0e08db0a529d692a8a476ea8a481ed0')
view=load('.cache/p3-302-view/HANDOFF.json','40b00237352e59cf10cb1b0115a458c13fa02ab775c6cf542972f2c7d8cd9e1f')
ready=load('.cache/p3-302-native-window/READY.json','df52451c2786c5af6c58e8c4a33bbc424a7b51719c266b140212ea4c191a2cc4')
for name,pin in backend['existing_dependency_files'].items():
    raw=(ROOT/name).read_bytes();assert sha(raw)==pin['sha256'] and len(raw)==pin['bytes'],name
sources={}
for package,key in ((backend,'promotion_files'),(view,'promote_files')):
    for name,pin in package[key].items():
        assert name not in sources
        sources[name]=(Path(package['candidate_root'])/name,pin)
for name in ('tests/test_ritual_weakening_integration_302.py','scripts/verify_ritual_weakening_window_302.py'):
    p=ROOT/'.cache/p3-302-parent'/name if name.startswith('tests/') else ROOT/'.cache/p3-302-native-window'/Path(name).name
    sources[name]=(p,ready['root_prospective_new_promotion_allowlist'][name])
assert set(sources)==set(ready['root_prospective_new_promotion_allowlist']) and len(sources)==13
pending={}
for name,(path,pin) in sources.items():
    assert not (ROOT/name).exists() and not Path(name).is_absolute() and '..' not in Path(name).parts,name
    raw=path.read_bytes();assert sha(raw)==pin['sha256'] and len(raw)==pin['bytes'],name
    assert pin==ready['root_prospective_new_promotion_allowlist'][name],name
    if name.endswith('.py'):ast.parse(raw)
    pending[name]=raw
name='rouge/node_catalog_view.py'
before=(ROOT/name).read_bytes();after=(ROOT/'.cache/p3-302-parent'/name).read_bytes()
assert sha(before)=='65420d73c69c275d96b63b14274e7b481b5795ca7053ea9f1b0412027e659bf5'
assert (ROOT/'verification/sections/302-preparation/before'/name).read_bytes()==before
assert sha(after)=='951c316c91ecb3624fafe8cc289ff8f2abc70b4fe232f0cb91f7959d272e2f39'
def methods(raw):return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(raw)) if isinstance(n,ast.FunctionDef)}
x,y=methods(before),methods(after)
assert set(x)-set(y)==set() and set(y)-set(x)=={'open_ritual_weakening'}
assert {n for n in x if x[n]!=y[n]}=={'__init__','show_selected'}
record={'section':302,'kind':'root_reviewed_functional_promotion_before_formal_verification',
 'at_utc':datetime.now(timezone.utc).isoformat(),'parent_commit':PARENT,
 'promoted':{n:sha(v) for n,v in pending.items()},'existing_production_changes':{name:sha(after)},
 'before_existing_sha256':{name:sha(before)},'old_tests_modified':False,
 'parent_methods_changed':['__init__','show_selected'],'parent_methods_added':['open_ritual_weakening'],
 'other_existing_method_AST_unchanged':47,
 'author_backend_handoff':'.cache/p3-302-backend/HANDOFF_FINAL.json','author_backend_handoff_sha256':sha((ROOT/'.cache/p3-302-backend/HANDOFF_FINAL.json').read_bytes()),
 'author_view_handoff':'.cache/p3-302-view/HANDOFF.json','author_view_handoff_sha256':sha((ROOT/'.cache/p3-302-view/HANDOFF.json').read_bytes()),
 'native_ready':'.cache/p3-302-native-window/READY.json','native_ready_sha256':sha((ROOT/'.cache/p3-302-native-window/READY.json').read_bytes()),
 'formal_verification_or_publication_claimed':False,'runtime_reads_complete_primary_table':False,
 'event_battle_links_or_calculation_model_modified':False,
 'fixed_reference_inventory':{'events':1,'choices':6,'weakening_effects':3,'related_fixed_stages':1}}
target=ROOT/'verification/sections/302-preparation/promotion.json';assert not target.exists()
for name,raw in pending.items():
    out=ROOT/name;out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('xb') as stream:stream.write(raw)
(ROOT/'rouge/node_catalog_view.py').write_bytes(after)
with target.open('x',encoding='utf8') as stream:stream.write(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'new_files':len(pending),'existing_production_files':1,'sources':14,'formal_verified':False}))
