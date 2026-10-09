"""Root only local resource104 admission after published103 and actual Gold."""
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
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
    publication=json.loads((base/'section103-publication-v1.json').read_bytes())
    assert publication['local_HEAD']==publication['remote_HEAD']==head and publication['clean'] is True
    guard=json.loads((base/'resume103-applied-source-v1.json').read_bytes())
    for name,want in {**guard['source_sha256'],**guard['source_additional_sha256']}.items():assert sha((root/name).read_bytes())==want,name
    gold_path=base/'resume104-window-gold-v1/receipt.json';gold=json.loads(gold_path.read_bytes())
    assert (base/'resume104-window-gold-v1.exit-code').read_text().strip()=='0'
    assert gold['passed'] is True and gold['workflow_complete'] is True and len(gold['rows'])==9 and gold['phase']=='gold'
    assert gold['source_before']==gold['source_after']==guard['source_sha256'] and not gold['source_drift']
    assert gold['source_additional_before']==gold['source_additional_after']==guard['source_additional_sha256'] and not gold['Qt_errors']
    assert gold['runner_sha256']=='24f6e00bf52d6a08e40e5da2c66eb45848311c75235434217b06f8c9fb42bbe1'
    packet=base/'section104-resource-admission-candidate-source-v1';manifest=json.loads((packet/'manifest.json').read_bytes())
    for row in manifest['files']:
        raw=(packet/row['path']).read_bytes();assert len(raw)==row['bytes'] and sha(raw)==row['sha256']
    review=base/'section104-resource-candidate-independent-source-v1/review.json'
    assert sha(review.read_bytes())=='79dad5266126680f1e53f19e294beda63da1de884841228620354a57d05e6a6f'
    edit=json.loads((packet/'edit-spec.json').read_bytes());path=edit['target'];assert path=='rouge/run_state.py'
    original=(root/path).read_bytes();nl='\r\n' if b'\r\n' in original else '\n'
    before=edit['old_utf8_lf'].replace('\n',nl).encode();after=edit['new_utf8_lf'].replace('\n',nl).encode()
    assert original.count(before)==1;raw=original.replace(before,after,1);assert raw.count(after)==1 and raw.replace(after,before,1)==original
    old=methods(original);new=methods(raw);assert set(old)==set(new) and {key for key in old if old[key]!=new[key]}=={'apply'}
    outputs={path:raw};cloud='scripts/verify_cloud.py';raw=(root/cloud).read_bytes();needle=b'MODULES = (\n';assert raw.count(needle)==1
    outputs[cloud]=raw.replace(needle,needle+b'    "tests.test_resource_observation_104",\n',1)
    test='tests/test_resource_observation_104.py';assert not (root/test).exists();outputs[test]=(packet/'candidate'/test).read_bytes()
    assert sha(outputs[test])=='3d1aa8cd3b6865d8f567010f17f44841058b7f06620bd16c8cbaab457fbe6f8e'
    for name,raw in outputs.items():compile(raw,name,'exec')
    for name,raw in outputs.items():(root/name).write_bytes(raw)
    sources={p.relative_to(root).as_posix():sha(p.read_bytes()) for folder in ('rouge','tests','scripts') for p in sorted((root/folder).rglob('*')) if p.is_file() and p.suffix in ('.py','.json') and '__pycache__' not in p.parts}
    assert len(sources)==748 and set(sources)-set(guard['source_sha256'])=={test}
    assert {key for key in guard['source_sha256'] if sources[key]!=guard['source_sha256'][key]}=={path,cloud}
    for name,want in guard['source_additional_sha256'].items():assert sha((root/name).read_bytes())==want
    receipt={'section':104,'status':'ACTUALLY_APPLIED_RUNTIME_PENDING','baseline_HEAD':head,
             'applied_at_Beijing':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
             'source_sha256':sources,'source_additional_sha256':guard['source_additional_sha256'],'source_count':748,
             'changed_paths':sorted(outputs),'AST_changed_methods':['apply'],'AST_unchanged_RunState_methods':16,
             'original_actual_resource_observations_sha256':'6cc40a282005aec7d201bc6aeec4608f83e1b96954055bdd7cc75059e7c0cb7f',
             'actual_prior_publication':publication,'actual_healthy_Gold_receipt_sha256':sha(gold_path.read_bytes())}
    with (base/'resume104-applied-source-v1.json').open('x') as stream:json.dump(receipt,stream,ensure_ascii=False,indent=2);stream.write('\n')
    print(json.dumps({'section':104,'applied':True,'source_files':748,'changed_paths':sorted(outputs)}))

if __name__=='__main__':main()
