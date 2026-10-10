"""Root-only exact local Source transport, after all bytes were reviewed."""
import argparse,datetime,hashlib,json
from pathlib import Path
p=argparse.ArgumentParser()
for k in ('guard','plan','out'):p.add_argument('--'+k,required=True)
a=p.parse_args();R=Path('/workspace/rougezhushou');G=Path(a.guard);P=Path(a.plan);O=Path(a.out)
g=json.loads(G.read_text());plan=json.loads(P.read_text())
def sha(b):return hashlib.sha256(b).hexdigest()
def mapping():
    values={}
    for d in ('rouge','tests','scripts'):
        for f in (R/d).rglob('*'):
            if f.suffix not in ('.py','.json') or '__pycache__' in f.parts:continue
            assert not f.is_symlink()
            if f.is_file():values[f.relative_to(R).as_posix()]=sha(f.read_bytes())
    return dict(sorted(values.items()))
assert not O.exists() and mapping()==g['source_sha256']
assert json.loads((R/'DEVELOPMENT_CHECKPOINT.json').read_text())['completed_sections']==g['section']-1
assert all(sha((R/f).read_bytes())==s for f,s in g['source_additional_sha256'].items())
assert plan['section']==g['section'] and len(plan['files'])==len({x['path'] for x in plan['files']})
composed={};old={}
for x in plan['files']:
    f=x['path'];q=Path(f);assert not q.is_absolute() and '..' not in q.parts and q.parts[0] in ('rouge','tests','scripts')
    target=R/q;assert not target.is_symlink()
    if 'new_source' in x:
        assert not target.exists();s=Path(x['new_source']);assert not s.is_symlink();b=s.read_bytes();assert sha(b)==x['new_source_sha256']
    else:
        original=target.read_bytes();assert sha(original)==g['source_sha256'][f];old[f]=original;b=original
        for block in x['blocks']:
            before=block['before'].encode();after=block['after'].encode();assert before and b.count(before)==1,(f,'not unique')
            b=b.replace(before,after,1)
        inverse=b
        for block in reversed(x['blocks']):
            after=block['after'].encode();before=block['before'].encode()
            if after:assert inverse.count(after)==1,(f,'inverse not unique');inverse=inverse.replace(after,before,1)
            else:
                # Deletions cannot be inversely located; exact forward assembly
                # from the byte-verified original still preserves other bytes.
                inverse=None;break
        if inverse is not None:assert inverse==original
    if q.suffix=='.py':compile(b,f,'exec')
    elif q.suffix=='.json':json.loads(b)
    composed[f]=b
assert set(composed)-set(g['source_sha256'])=={x['path'] for x in plan['files'] if 'new_source' in x}
for f,b in composed.items():(R/f).parent.mkdir(parents=True,exist_ok=True);(R/f).write_bytes(b)
actual=mapping();expected=dict(g['source_sha256']);expected.update({f:sha(b) for f,b in composed.items()});assert actual==dict(sorted(expected.items()))
assert all(sha((R/f).read_bytes())==s for f,s in g['source_additional_sha256'].items())
g.update(kind='ROOT_ACTUAL_APPLIED_SECTION_CANDIDATE_SOURCE_GUARD',source_sha256=actual,changed_paths=sorted(composed),product_applied=True,passed=False,candidate_completed=False,recorded_at_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),root_reviewed_local_plan_sha256=sha(P.read_bytes()))
O.write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'section':g['section'],'actual_source_count':len(actual),'changed_paths':g['changed_paths'],'product_applied':True,'runtime_pass':False}))
