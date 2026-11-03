"""Root reviewed local transport application with whole-source guards."""
import argparse,hashlib,json,pathlib,subprocess
p=argparse.ArgumentParser();p.add_argument('--guard',required=True);p.add_argument('--transport',required=True);p.add_argument('--out',required=True);p.add_argument('--original',action='append',required=True);a=p.parse_args()
R=pathlib.Path('/workspace/rougezhushou');B=pathlib.Path('/workspace/.continuation');g=json.loads(pathlib.Path(a.guard).read_text());tpath=pathlib.Path(a.transport);t=json.loads(tpath.read_text());section=g['section']
def sha(raw):return hashlib.sha256(raw).hexdigest()
def mapping():return dict(sorted((f.relative_to(R).as_posix(),sha(f.read_bytes())) for d in ['rouge','tests','scripts'] for f in (R/d).rglob('*') if f.is_file() and f.suffix in ('.py','.json') and '__pycache__' not in f.parts))
assert subprocess.check_output(['git','branch','--show-current'],cwd=R,text=True).strip()=='codex/p2-development'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()==g['root_prior_HEAD'];assert mapping()==g['source_sha256']
for path,digest in g['source_additional_sha256'].items():assert sha((R/path).read_bytes())==digest
for name in a.original:
 d=pathlib.Path(name);r=json.loads((d/'observations.json').read_text());assert (B/(d.name+'.exit-code')).read_text().strip()=='0';assert r['observation_complete'] and r['consumer_error_count']==0 and r['source_before']==g['source_sha256']==r['source_after']
plans=[];expected=dict(g['source_sha256']);rebases=[]
for item in t['existing_changed_files']:
 path=item['path'];old=(R/path).read_bytes();assert sha(old)==item['before_sha256'];new=old
 for block in item['blocks']:
  before=block['old'].encode();after=block['new'].encode();assert new.count(before)==block['occurrences']==1;new=new.replace(before,after,1)
 assert sha(new)==item['after_sha256'] and len(new)==item['after_bytes'];inverse=new
 for block in reversed(item['blocks']):assert inverse.count(block['new'].encode())==1;inverse=inverse.replace(block['new'].encode(),block['old'].encode(),1)
 assert inverse==old;compile(new,path,'exec');plans.append((path,new));expected[path]=sha(new)
for item in t['new_files']:
 path=item['repo_path'];assert not (R/path).exists();raw=(tpath.parent/item['packet_path']).read_bytes();assert len(raw)==item['bytes'] and sha(raw)==item['sha256'];compile(raw,path,'exec');plans.append((path,raw));expected[path]=sha(raw)
assert len(set(path for path,_ in plans))==len(plans)
for path,raw in plans:(R/path).write_bytes(raw)
assert mapping()==dict(sorted(expected.items()))
for path,digest in g['source_additional_sha256'].items():assert sha((R/path).read_bytes())==digest
applied={**g,'kind':f'ROOT_ACTUAL{section}_APPLIED_SOURCE_RUNTIME_PENDING','source_sha256':dict(sorted(expected.items())),'changed_paths':[path for path,_ in plans],'product_applied':True,'candidate_completed':False,'transport_sha256':sha(tpath.read_bytes()),'original_guard_sha256':sha(pathlib.Path(a.guard).read_bytes()),'original_observations':a.original}
with pathlib.Path(a.out).open('x') as f:json.dump(applied,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'section':section,'changed_files':len(plans),'source_files':len(expected),'candidate_runtime_pass':False}))
