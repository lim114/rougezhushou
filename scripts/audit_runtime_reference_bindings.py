"""Read-only static byte audit; not a semantic or whole-program review."""
from pathlib import Path
from hashlib import sha256
import ast,json,argparse

ROOT_EXPR=ast.dump(ast.parse('Path(__file__).resolve().parents[1]',mode='eval').body)


def audit(root):
    root=Path(root).resolve();cache={};rows=[];unresolved=[]
    def value(node,env):
        if ast.dump(node)==ROOT_EXPR:return str(root)
        if isinstance(node,ast.Constant):return node.value
        if isinstance(node,ast.Name):return env.get(node.id)
        if isinstance(node,ast.BinOp):
            a,b=value(node.left,env),value(node.right,env)
            if isinstance(a,str)and isinstance(b,str):
                if isinstance(node.op,ast.Add):return a+b
                if isinstance(node.op,ast.Div):return str(Path(a)/b)
        return None
    def pin(name):
        path=Path(name);path=path if path.is_absolute()else root/path
        if not path.resolve().is_relative_to(root)or any(p in ('.local','.cache')for p in path.parts):return {'unavailable':'outside public scope'}
        name=path.relative_to(root).as_posix()
        if name not in cache:
            try:raw=path.read_bytes();cache[name]={'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
            except OSError as exc:cache[name]={'unavailable':type(exc).__name__}
        return cache[name]
    for path in sorted((root/'rouge').glob('*.py')):
        raw=path.read_bytes()
        if b'MANIFEST_SHA256'not in raw:continue
        tree=ast.parse(raw);env={}
        for node in tree.body:
            if isinstance(node,ast.Assign):
                result=value(node.value,env)
                if result is not None:
                    for target in node.targets:
                        if isinstance(target,ast.Name):env[target.id]=result
        manifest=env.get('MANIFEST')
        if not isinstance(manifest,str):
            candidates=[value(node,env)for node in ast.walk(tree)if isinstance(node,ast.BinOp)and isinstance(node.op,ast.Div)
                        and isinstance(node.right,ast.Constant)and node.right.value in ('source_manifest.json','runtime-manifest.json')]
            manifest=next((m for m in candidates if isinstance(m,str)),None)
        if not isinstance(manifest,str)and isinstance(env.get('PACK'),str)and '/runtime-manifest.json'in raw.decode('utf8'):
            manifest=env['PACK']+'/runtime-manifest.json'
        if not isinstance(manifest,str):unresolved.append(path.relative_to(root).as_posix());continue
        p=Path(manifest);p=p if p.is_absolute()else root/p
        rel=p.relative_to(root).as_posix()
        try:data=json.loads(p.read_bytes())
        except(OSError,ValueError)as exc:rows.append({'module':path.stem,'manifest':rel,'error':type(exc).__name__});continue
        support='files'not in data
        runtime=data.get('runtime_files',data.get('files',{}))
        if support:runtime={str(p.parent/n):{'sha256':v}for n,v in data.get('support_files_sha256',{}).items()}
        runtime=dict(runtime);separate=[]
        if isinstance(env.get('DATA'),str)and isinstance(env.get('DATA_SHA256'),str)and env['DATA']not in runtime:
            runtime[env['DATA']]={'sha256':env['DATA_SHA256']};separate.append(env['DATA'])
        if isinstance(env.get('PROOF_SHA256'),str):
            for node in ast.walk(tree):
                if isinstance(node,ast.BinOp)and isinstance(node.op,ast.Div)and isinstance(node.right,ast.Constant)and node.right.value=='source-proof.json':
                    proof=value(node,env)
                    if isinstance(proof,str)and proof not in runtime:runtime[proof]={'sha256':env['PROOF_SHA256']};separate.append(str(Path(proof).relative_to(root)))
        checks=[]
        for name,expected in runtime.items():
            actual=pin(name)
            checks.append({'path':str(Path(name).relative_to(root))if Path(name).is_absolute()else name,
                           'matches':all(actual.get(k)==expected[k]for k in ('sha256','bytes')if k in expected),
                           'expected':expected,'actual':actual})
        rows.append({'module':path.stem,'module_path':path.relative_to(root).as_posix(),'source_sha256':sha256(raw).hexdigest(),
                     'manifest':rel,'manifest_digest_matches':pin(rel).get('sha256')==env.get('MANIFEST_SHA256'),
                     'runtime_files':len(checks),'runtime_code_files':[c['path']for c in checks if c['path'].endswith(('.py','.js','.cjs'))],
                     'runtime_file_checks':checks,'separately_pinned_data_or_proofs':separate,'support_only_scope':support})
    return {'static_resolved_runtime_bindings':len(rows),'unresolved':unresolved,'rows':rows,
            'all_resolved_runtime_bytes_match':all(not r.get('error')and r['manifest_digest_matches']and all(p['matches']for p in r['runtime_file_checks'])for r in rows),
            'limitation':'Static manifest/support-file byte audit only. No importing target modules, no private files or network, no proof that loaders execute or schemas, UI, formulas or actual game mechanisms are correct.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();result=audit(Path(__file__).resolve().parents[1]);assert not args.output.exists()
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8')
    print(json.dumps({k:result[k]for k in ('static_resolved_runtime_bindings','unresolved','all_resolved_runtime_bytes_match')},ensure_ascii=False))
