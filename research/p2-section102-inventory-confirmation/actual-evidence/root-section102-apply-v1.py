"""Root exact local102 changes against actually published101 and actual Gold."""
import ast
import datetime
import hashlib
import json
from pathlib import Path
import subprocess

root=Path('/workspace/rougezhushou');base=Path('/workspace/.continuation')
def sha(raw):return hashlib.sha256(raw).hexdigest()
def methods(raw):
    tree=ast.parse(raw);cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='RunState')
    return {n.name:ast.dump(n,include_attributes=False) for n in cls.body if isinstance(n,ast.FunctionDef)}

def main():
    assert subprocess.check_output(['git','branch','--show-current'],cwd=root,text=True).strip()=='codex/p2-development'
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=root,text=True).strip()
    publication=json.loads((base/'section101-publication-v1.json').read_bytes())
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
    assert publication['local_HEAD']==publication['remote_HEAD']==head and publication['clean'] is True
    guard=json.loads((base/'resume101-applied-source-v1.json').read_bytes())
    for name,want in {**guard['source_sha256'],**guard['source_additional_sha256']}.items():assert sha((root/name).read_bytes())==want,name
    gold=json.loads((base/'resume102-window-gold-v1/receipt.json').read_bytes())
    assert (base/'resume102-window-gold-v1.exit-code').read_text().strip()=='0'
    assert gold['passed'] is True and gold['workflow_complete'] is True and len(gold['rows'])==6
    assert gold['source_before']==gold['source_after']==guard['source_sha256']
    assert gold['source_additional_before']==gold['source_additional_after']==guard['source_additional_sha256']
    flag=base/'section102-inventory-flag-consumption-source-v1';registry=base/'section102-registry-increment-source-v1'
    for packet in (flag,registry):
        manifest=json.loads((packet/'MANIFEST.json').read_bytes())
        for row in manifest['payload_files']:
            raw=(packet/row['path']).read_bytes();assert len(raw)==row['bytes'] and sha(raw)==row['sha256']
    path='rouge/run_state.py';original=(root/path).read_bytes();raw=original
    nl='\r\n' if b'\r\n' in raw else '\n'
    candidate=(flag/'run_state.candidate.py').read_text();tree=ast.parse(candidate)
    function=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_inventory_confirmation_flag')
    new_helper=ast.get_source_segment(candidate,function)+'\n\n\n'
    before=('class RunState:').encode();assert raw.count(before)==1
    raw=raw.replace(before,new_helper.replace('\n',nl).encode()+before,1)
    for before,after in (
        ("prior_inventory_verified=state['inventory_verified']","prior_inventory_verified=_inventory_confirmation_flag(state['inventory_verified'])"),
        ("state['inventory_verified'] and bool(incoming_items-set(self.held_relic_ids()+self.held_tool_ids()))","_inventory_confirmation_flag(state['inventory_verified']) and bool(incoming_items-set(self.held_relic_ids()+self.held_tool_ids()))"),
        ("complete=self.state['inventory_verified'] and count is not None and known+tools==count","complete=_inventory_confirmation_flag(self.state['inventory_verified']) and count is not None and known+tools==count")):
        assert raw.count(before.encode())==1,before;raw=raw.replace(before.encode(),after.encode(),1)
    old=methods(original);new=methods(raw);assert set(old)==set(new)
    assert {key for key in old if old[key]!=new[key]}=={'apply','inventory_status'}
    outputs={path:raw}
    full='scripts/verify_full_available.py';assert (root/full).read_bytes()==(registry/'verify_full_available.baseline.py').read_bytes()
    outputs[full]=(registry/'verify_full_available.candidate.py').read_bytes()
    cloud='scripts/verify_cloud.py';raw=(root/cloud).read_bytes();needle=b'MODULES = (\n';assert raw.count(needle)==1
    outputs[cloud]=raw.replace(needle,needle+b'    "tests.test_inventory_confirmation_102",\n',1)
    test='tests/test_inventory_confirmation_102.py';assert not (root/test).exists();outputs[test]=(flag/'test_inventory_confirmation_102.py').read_bytes()
    for name,raw in outputs.items():compile(raw,name,'exec')
    for name,raw in outputs.items():(root/name).write_bytes(raw)
    after={p.relative_to(root).as_posix():sha(p.read_bytes()) for folder in ('rouge','tests','scripts') for p in sorted((root/folder).rglob('*')) if p.is_file() and p.suffix in ('.py','.json') and '__pycache__' not in p.parts}
    assert len(after)==746 and set(after)-set(guard['source_sha256'])=={test}
    assert {key for key in guard['source_sha256'] if after[key]!=guard['source_sha256'][key]}=={path,full,cloud}
    for name,want in guard['source_additional_sha256'].items():assert sha((root/name).read_bytes())==want
    receipt={'section':102,'status':'ACTUALLY_APPLIED_RUNTIME_PENDING','baseline_HEAD':head,
             'applied_at_Beijing':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
             'source_sha256':after,'source_additional_sha256':guard['source_additional_sha256'],'source_count':746,
             'changed_paths':sorted(outputs),'AST_changed_RunState_methods':['apply','inventory_status'],
             'AST_unchanged_RunState_methods':sum(old[key]==new[key] for key in old),
             'actual_prior_publication':publication,'actual_Gold_receipt_sha256':sha((base/'resume102-window-gold-v1/receipt.json').read_bytes())}
    with (base/'resume102-applied-source-v1.json').open('x') as stream:json.dump(receipt,stream,ensure_ascii=False,indent=2);stream.write('\n')
    print(json.dumps({'applied':True,'section':102,'source_files':746,'changed_paths':sorted(outputs)}))

if __name__=='__main__':main()
