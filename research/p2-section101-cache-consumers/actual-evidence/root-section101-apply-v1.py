"""Root exact reviewed101 transports, only after actual full100 publication."""
import ast
import datetime
import hashlib
import json
from pathlib import Path
import subprocess


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    root=Path('/workspace/rougezhushou');base=Path('/workspace/.continuation')
    packet=base/'section101-cache-consumer-candidate-source-v2'
    assert subprocess.check_output(['git','branch','--show-current'],cwd=root,text=True).strip()=='codex/p2-development'
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=root,text=True).strip()
    publication=json.loads((base/'full100-publication-v1.json').read_bytes())
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
    assert publication['local_HEAD']==publication['remote_HEAD']==head and publication['clean'] is True
    closure=json.loads((root/'verification/full-100/closure.json').read_bytes())
    assert closure['batch_validation_closed'] is True
    guard=json.loads((base/'full100-completed-source-guard-v1.json').read_bytes())
    for path,value in guard['source_sha256'].items():assert sha(root/path)==value,path
    for path,value in guard['source_additional_sha256'].items():assert sha(root/path)==value,path
    manifest=json.loads((packet/'manifest.json').read_bytes())
    for path,row in manifest['files'].items():
        assert (packet/path).stat().st_size==row['bytes'] and sha(packet/path)==row['sha256']
    transport=json.loads((packet/'exact-local-transports.json').read_bytes())['entries']
    originals={path:(root/path).read_bytes() for path in {row['path'] for row in transport}}
    outputs=dict(originals)
    for row in transport:
        raw=outputs[row['path']]
        newline='\r\n' if b'\r\n' in raw else '\n'
        before=row['before'].replace('\n',newline).encode();after=row['after'].replace('\n',newline).encode()
        assert raw.count(before)==1,row['path']
        outputs[row['path']]=raw.replace(before,after,1)
    for name in ('rouge/run_metadata_view.py','tests/test_cache_consumers_101.py'):
        assert not (root/name).exists();outputs[name]=(packet/'candidate'/name).read_bytes()
    assert len(outputs)==6
    for name,raw in outputs.items():compile(raw,name,'exec')
    ast_checks={}
    for name,changed,unchanged in (('rouge/run_state.py',{'apply','summary'},15),('rouge/app.py',{'sync_target_buffs'},58)):
        def methods(raw):
            tree=ast.parse(raw)
            cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name in ('RunState','MainWindow'))
            return {n.name:ast.dump(n,include_attributes=False) for n in cls.body if isinstance(n,ast.FunctionDef)}
        old=methods(originals[name]);new=methods(outputs[name]);assert set(old)==set(new)
        assert {key for key in old if old[key]!=new[key]}==changed
        assert sum(old[key]==new[key] for key in old)==unchanged
        ast_checks[name]={'changed_methods':sorted(changed),'unchanged_methods':unchanged}
    for name,raw in outputs.items():
        path=root/name
        with path.open('wb') as handle:handle.write(raw)
    after={p.relative_to(root).as_posix():sha(p) for name in ('rouge','tests','scripts') for p in sorted((root/name).rglob('*')) if p.is_file() and p.suffix in ('.py','.json') and '__pycache__' not in p.parts}
    assert len(after)==745 and set(after)-set(guard['source_sha256'])=={'rouge/run_metadata_view.py','tests/test_cache_consumers_101.py'}
    assert {key for key in guard['source_sha256'] if after[key]!=guard['source_sha256'][key]}=={'rouge/app.py','rouge/run_state.py','rouge/relic_counter_semantics.py','scripts/verify_cloud.py'}
    assert after['rouge/training_view.py']==guard['source_sha256']['rouge/training_view.py']
    receipt={'section':101,'status':'ACTUALLY_APPLIED_RUNTIME_PENDING','baseline_HEAD':head,
             'applied_at_Beijing':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
             'source_sha256':after,'source_count':745,'source_additional_sha256':guard['source_additional_sha256'],
             'changed_paths':sorted(outputs),'AST_checks':ast_checks,
             'actual_full100_publication':publication,'candidate_manifest_sha256':sha(packet/'manifest.json')}
    with (base/'resume101-applied-source-v1.json').open('x',encoding='utf-8') as handle:
        json.dump(receipt,handle,ensure_ascii=False,indent=2);handle.write('\n')
    print(json.dumps({'section':101,'applied':True,'source_files':745,'baseline_HEAD':head,'changed_paths':sorted(outputs)},ensure_ascii=False))


if __name__=='__main__':
    main()
