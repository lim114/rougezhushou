"""Root local103 transports only after actual published102 and healthy GUI Gold."""
import ast
import datetime
import hashlib
import json
from pathlib import Path
import subprocess

root=Path('/workspace/rougezhushou');base=Path('/workspace/.continuation')
def sha(raw):return hashlib.sha256(raw).hexdigest()
def functions(raw,class_name=None):
    tree=ast.parse(raw)
    if class_name:tree=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name==class_name)
    return {n.name:ast.dump(n,include_attributes=False) for n in tree.body if isinstance(n,ast.FunctionDef)}

def main():
    assert subprocess.check_output(['git','branch','--show-current'],cwd=root,text=True).strip()=='codex/p2-development'
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=root,text=True).strip()
    publication=json.loads((base/'section102-publication-v1.json').read_bytes())
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
    assert publication['local_HEAD']==publication['remote_HEAD']==head and publication['clean'] is True
    guard=json.loads((base/'resume102-applied-source-v1.json').read_bytes())
    for name,want in {**guard['source_sha256'],**guard['source_additional_sha256']}.items():assert sha((root/name).read_bytes())==want,name
    gold_path=base/'resume103-window-gold-v2/receipt.json';gold=json.loads(gold_path.read_bytes())
    assert (base/'resume103-window-gold-v2.exit-code').read_text().strip()=='0'
    assert gold['passed'] is True and gold['workflow_complete'] is True and len(gold['rows'])==9
    assert gold['source_before']==gold['source_after']==guard['source_sha256'] and not gold['source_drift']
    assert gold['source_additional_before']==gold['source_additional_after']==guard['source_additional_sha256']
    assert gold['phase']=='gold' and not gold['Qt_errors']
    assert gold['runner_sha256']=='c2eafe3f0aec05d2378b23d9f52160b243e3ee7ed0788a504bef2eaaa49f0074'
    packet=base/'section103-cache-recovery-candidate-source-v2'
    assert sha((packet/'exact-local-transports.json').read_bytes())=='c0988b5f7ef4a62b4a67e6cc49ed866901bdd0532e89438aa4c824f5133c0976'
    assert sha((packet/'candidate/tests/test_cache_recovery_103.py').read_bytes())=='40107e79366d141d4c2c9495094e86dc60000a1d3db2a9a5c369ecb5988e9844'
    review=packet/'INDEPENDENT_SOURCE_REVIEW.md';assert sha(review.read_bytes())=='9ed9c0187be948e9e2d65eaa452a3caa8897748f83d0787746bd7c5753574327'
    transports=json.loads((packet/'exact-local-transports.json').read_bytes())
    originals={name:(root/name).read_bytes() for name in {row['path'] for row in transports}};outputs=dict(originals)
    for row in transports:
        raw=outputs[row['path']];nl='\r\n' if b'\r\n' in raw else '\n'
        before=row['before'].replace('\n',nl).encode();after=row['after'].replace('\n',nl).encode()
        assert raw.count(before)==1,row['path'];outputs[row['path']]=raw.replace(before,after,1)
    test='tests/test_cache_recovery_103.py';assert not (root/test).exists();outputs[test]=(packet/'candidate'/test).read_bytes()
    changes={}
    for name,cls,expected in (('rouge/run_state.py','RunState',{'apply'}),('rouge/run_config.py',None,{'confirmed_config'})):
        old=functions(originals[name],cls);new=functions(outputs[name],cls);assert set(old)==set(new)
        changed={key for key in old if old[key]!=new[key]};assert changed==expected
        changes[name]={'changed_functions':sorted(changed),'unchanged_functions':len(old)-len(changed)}
    for name,raw in outputs.items():compile(raw,name,'exec')
    for name,raw in outputs.items():(root/name).write_bytes(raw)
    after={p.relative_to(root).as_posix():sha(p.read_bytes()) for folder in ('rouge','tests','scripts') for p in sorted((root/folder).rglob('*')) if p.is_file() and p.suffix in ('.py','.json') and '__pycache__' not in p.parts}
    assert len(after)==747 and set(after)-set(guard['source_sha256'])=={test}
    assert {key for key in guard['source_sha256'] if after[key]!=guard['source_sha256'][key]}=={'rouge/run_state.py','rouge/run_config.py','scripts/verify_cloud.py'}
    for name,want in guard['source_additional_sha256'].items():assert sha((root/name).read_bytes())==want
    receipt={'section':103,'status':'ACTUALLY_APPLIED_RUNTIME_PENDING','baseline_HEAD':head,
             'applied_at_Beijing':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
             'source_sha256':after,'source_additional_sha256':guard['source_additional_sha256'],'source_count':747,
             'changed_paths':sorted(outputs),'AST_checks':changes,'actual_prior_publication':publication,
             'actual_healthy_Gold_receipt_sha256':sha(gold_path.read_bytes()),'source_transport_sha256':sha((packet/'exact-local-transports.json').read_bytes())}
    with (base/'resume103-applied-source-v1.json').open('x') as stream:json.dump(receipt,stream,ensure_ascii=False,indent=2);stream.write('\n')
    print(json.dumps({'section':103,'applied':True,'source_files':747,'changed_paths':sorted(outputs)}))

if __name__=='__main__':main()
